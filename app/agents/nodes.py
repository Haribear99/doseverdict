"""
도구 실행 노드 — 과제(Task)별로 결정론적 도구를 호출해 Evidence를 만든다. LLM 호출 없음.

규칙:
- 도구 실패는 예외가 아니라 관측값(ToolCall.ok=False) → 재계획 트리거 ②
- 수치 판정은 도구가 낸다(TCR verdict, 설계 OC). LLM은 나중에 이 값을 '인용'만 한다.
- 근거 우선순위: 1 = 직접 측정(라벨 보고값), 2 = 문서 규범, 3 = 파생 추정 지표
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from app.schema.trial_schema import Evidence, ReviewState, Task, ToolCall, TrialSchema
from app.agents.planner import generic_name
from app.tools import ToolResult, analog_trial, design_sim, open_targets, pharmacology

_CHEMBL_BY_GENERIC = {"sotorasib": "CHEMBL4535757", "adagrasib": "CHEMBL4594398", "osimertinib": "CHEMBL3353410"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(state: ReviewState, tool: str, args: dict[str, Any], r: ToolResult) -> str:
    cid = f"tc_{len(state.tool_log) + 1:03d}"
    summary = None
    if r.ok and isinstance(r.data, dict):
        summary = ", ".join(f"{k}={str(v)[:40]}" for k, v in list(r.data.items())[:6])
    state.tool_log.append(ToolCall(tool_call_id=cid, tool=tool, args=args, ok=r.ok, result_summary=summary, error=r.error,
                                   started_at=_now(), latency_s=r.latency_s))
    state.budget.used_tool_calls += 1
    return cid


def _ev(state: ReviewState, kind: str, authority: str, quote: str, *, title: str | None = None, section: str | None = None,
        applicability: str | None = None, norm_strength: str | None = None, url: str | None = None, tool_call_id: str | None = None,
        tier: int = 2, version_date: str | None = None) -> str:
    eid = f"ev_{len(state.evidence) + 1:03d}"
    state.evidence[eid] = Evidence(evidence_id=eid, kind=kind, authority=authority, document_title=title, section=section, quote=quote[:1200],
                                   applicability=applicability, norm_strength=norm_strength, url=url, retrieved_at=_now(),
                                   tool_call_id=tool_call_id, priority_tier=tier, version_date=version_date)
    return eid


# ----------------------------------------------------------------- 과제별 실행
def run_structure_class(state: ReviewState, task: Task) -> None:
    ip = state.trial.study.investigational_product
    r = pharmacology.structure_profile(ip.smiles or "")
    cid = _log(state, "rdkit.structure_profile", {"smiles": ip.smiles}, r)
    if r.ok:
        _ev(state, "calculation", "RDKit", f"구조 계열: {r.data['structural_class']}; 알림 {[a['description'] for a in r.data['alerts']]}; MW {r.data['properties']['MW']}, cLogP {r.data['properties']['cLogP']}. "
            "구조 알림은 HTS 간섭 필터이며 임상 독성 예측용으로 검증되지 않았으므로 계열 분류까지만 사용한다.", tool_call_id=cid, tier=3)
        state.scratch["structure"] = r.data
    chembl_id = ip.chembl_id or _CHEMBL_BY_GENERIC.get(generic_name(ip))
    if chembl_id:
        r2 = pharmacology.chembl_potency(chembl_id, target_keyword=(ip.target or "").split()[0] if ip.target else None)
        cid2 = _log(state, "chembl.potency", {"chembl_id": chembl_id, "target": ip.target}, r2)
        if r2.ok and r2.data.get("n_target"):
            _ev(state, "database_record", "ChEMBL", f"{(ip.target or '표적').split()[0]} 표적 활성값 {r2.data['n_target']}건 중 검열값 {r2.data['n_censored_excluded']}건 제외. 세포 기반 {r2.data['cell_based_nM']} nM (중앙값 {r2.data['cell_based_median_nM']}), 생화학 {r2.data['biochemical_nM'][:5]} nM. 어세이 유형을 풀링하지 않는다.",
                url=r2.source.get("url"), tool_call_id=cid2, tier=1)
            state.scratch["chembl"] = r2.data
        elif not r2.ok:   # 재시도 후에도 실패 — 과제는 RDKit 결과로 계속하되 TCR의 IC50 대체를 기록한다
            state.replan_events.append({"trigger": "tool_failure", "tasks": [task.task_id], "tool": "chembl.potency",
                                        "action": "IC50 미확보 → TCR은 기본값 30 nM(소토라십 ChEMBL 세포 기반 중앙값, 2026-09 조회)으로 계산하고 근거에 명시"})
    task.status = "done" if r.ok else "failed"


def run_target_evidence(state: ReviewState, task: Task) -> None:
    ip = state.trial.study.investigational_product
    sym = (ip.target or ip.drug_class_hint or "").split()[0].upper()
    r = open_targets.target_evidence(sym)
    cid = _log(state, "opentargets.target_evidence", {"symbol": sym}, r)
    if r.ok and r.data.get("found"):
        drugs = [d for d in r.data["known_drugs"] if d.get("max_stage") == "APPROVAL"]
        _ev(state, "database_record", "Open Targets", f"{r.data['symbol']} ({r.data['ensembl_id']}): 승인약 {[d['drug'] for d in drugs]}, safety liabilities {len(r.data['safety_liabilities'])}건 {[s['event'] for s in r.data['safety_liabilities']][:5]}",
            url=r.source.get("url"), tool_call_id=cid, tier=1)
        state.scratch["approved_same_target"] = [d["drug"] for d in drugs]
    task.status = "done" if r.ok else "failed"


_BRAND_BY_GENERIC = {"SOTORASIB": "LUMAKRAS", "ADAGRASIB": "KRAZATI", "OSIMERTINIB": "TAGRISSO", "AFATINIB": "GILOTRIF"}


def run_class_label_check(state: ReviewState, task: Task) -> None:
    ip = state.trial.study.investigational_product
    names = list(dict.fromkeys([generic_name(ip).upper()] + [x.upper() for x in state.scratch.get("approved_same_target", [])]))
    checked = 0
    for g in names:
        brand = _BRAND_BY_GENERIC.get(g)
        if not brand:
            continue
        r = pharmacology.openfda_label(brand)
        cid = _log(state, "openfda.label", {"brand": brand}, r)
        if not r.ok:
            if g == generic_name(ip).upper():   # 시험약 자체 라벨 실패 → PK 미확보로 TCR 기권 finding이 빠진다. 원인을 남긴다
                state.replan_events.append({"trigger": "tool_failure", "tasks": [task.task_id], "tool": "openfda.label",
                                            "action": f"{brand} 라벨 PK 미확보(재시도 후 실패) → 노출-용량 계산 불가, 근거 미확보로 표기"})
            continue
        checked += 1
        d = r.data
        mon = "; ".join(d["liver_monitoring_statements"][:2]) or "간기능 모니터링 요구 없음"
        _ev(state, "label_statement", "FDA label", f"{brand} ({d['generic']}) 라벨 5.x 경고: {mon}", title=f"{brand} prescribing information", section="5 Warnings and Precautions",
            applicability="US", norm_strength="final_guidance", url=r.source.get("url"), tool_call_id=cid, tier=1, version_date=str(d.get("effective_time")))
        if d.get("nonlinear_pk_statement") or d.get("exposure_response_unknown_statement"):
            _ev(state, "label_statement", "FDA label", f"{brand} 12.2/12.3: {d.get('exposure_response_unknown_statement') or ''} {d.get('nonlinear_pk_statement') or ''}".strip(),
                title=f"{brand} prescribing information", section="12 Clinical Pharmacology", applicability="US", norm_strength="final_guidance",
                url=r.source.get("url"), tool_call_id=cid, tier=1, version_date=str(d.get("effective_time")))
        if g == generic_name(ip).upper() and d.get("pk"):
            state.scratch["label_pk"] = d["pk"] | {"brand": brand}
    task.status = "done" if checked else "failed"


def run_exposure_dose(state: ReviewState, task: Task) -> None:
    pk = state.scratch.get("label_pk")
    struct = state.scratch.get("structure", {})
    chembl = state.scratch.get("chembl", {})
    if not pk or not all(k in pk for k in ("cl_f_L_per_hr", "t_half_hr", "fu_label")):
        task.status = "abstained"
        _ev(state, "calculation", "DoseVerdict", "노출-용량 관계를 계산할 PK 보고값(CL/F, t½, f_u)이 없다 → 용량군별 반복투여 PK 자료 요청. 판정 보류.", tier=3)
        return
    mw = struct.get("properties", {}).get("MW", 560.61)
    ic50 = chembl.get("cell_based_median_nM")
    ic50_src = "ChEMBL 세포 기반 중앙값"
    if not ic50:
        ic50, ic50_src = 30.0, "ChEMBL 미확보 → 기본값(소토라십 ChEMBL 세포 기반 중앙값, 2026-09 조회)"
    doses = []
    for lvl in state.trial.design.dose_strategy.dose_levels:
        try:
            doses.append(float(str(lvl.dose).split()[0]))
        except (ValueError, AttributeError):
            pass
    rows = []
    for dose in sorted(set(doses))[:8]:
        r = pharmacology.tcr_three_metrics(dose, pk["cl_f_L_per_hr"], mw, pk["fu_label"], ic50, t_half_hr=pk["t_half_hr"])
        cid = _log(state, "pharm.tcr_three_metrics", {"dose_mg": dose, "ic50_nM": ic50}, r)
        if r.ok:
            rows.append((dose, r.data["TCR_max"], r.data["TCR_avg"], r.data["TCR_trough"], r.data["verdict"]))
    split = any(v == "abstain_metric_dependent" for *_, v in rows)
    table = "; ".join(f"{d:.0f} mg: Cmax {a:.1f}/Cavg {b:.1f}/Ctrough {c:.2f} → {v}" for d, a, b, c, v in rows)
    _ev(state, "calculation", "DoseVerdict", f"TCR(선형 CL/F 가정, IC50 {ic50} nM — {ic50_src}, f_u {pk['fu_label']}, t½ {pk['t_half_hr']} h): {table}. "
        + ("판정이 지표(Cavg vs Ctrough)에 따라 갈리므로 '커버된다'는 결론을 만들지 않는다. " if split else "")
        + "라벨이 비선형 PK를 보고하므로 선형 외삽은 라벨과 모순될 수 있다 → 두 가정을 병기하고 용량군별 반복투여 PK를 요청한다.", tier=3)
    cv_pct = pk.get("cl_cv_pct")
    cv_src = "라벨 12.3"
    if not cv_pct:
        cv_pct, cv_src = 76, "라벨 미기재 → 기본값(소토라십 라벨 CL/F CV)"
    r2 = pharmacology.exposure_power(cv_pct / 100)
    cid2 = _log(state, "pharm.exposure_power", {"cv": cv_pct / 100}, r2)
    if r2.ok:
        by = {x["n_per_arm"]: x for x in r2.data["rows"]}
        _ev(state, "calculation", "DoseVerdict", f"CL/F CV {cv_pct}%({cv_src}) 기준 두 용량군 AUC 비 95% CI 폭: n=2 {by[2]['fold']}배, n=4 {by[4]['fold']}배, n=12 {by[12]['fold']}배. 증량 코호트 규모(2~4명)로는 노출 포화를 확정할 수 없다.", tool_call_id=cid2, tier=3)
    state.scratch["tcr_split"] = split
    task.status = "abstained" if split else "done"


def run_design_oc(state: ReviewState, task: Task) -> None:
    ds = state.trial.design.dose_strategy
    n_levels = max(3, min(len(ds.dose_levels), 8))
    # 시나리오: 중간 용량이 MTD(목표 30%) — 프로토콜 자체 독성 가정이 없으므로 대표 시나리오 1개 + 비교표
    tox = [round(0.05 + 0.65 * i / max(1, n_levels - 1), 2) for i in range(n_levels)]
    r = design_sim.compare_sample_matched(tox, n_sim=2000)
    cid = _log(state, "design.compare_sample_matched", {"true_dlt": tox}, r)
    if r.ok:
        rows = r.data["rows"]
        p = rows["3+3"]
        _ev(state, "calculation", "DoseVerdict", f"용량군 {n_levels}개, 목표 DLT 30%, 대표 독성 곡선 {tox}에서 3+3: 평균 표본 {p['N']}명, 정확 MTD 선택률 {p['PCS']}%, MTD 미확정 {p['none']}%, 과다노출 비율 {p['pct_over']}%. "
            f"표본 정합 BOIN(n={r.data['n_matched']}): PCS {rows[f'BOIN(n={r.data['n_matched']})']['PCS']}%, 미확정 {rows[f'BOIN(n={r.data['n_matched']})']['none']}%. 조건을 통제한 비교만 인용한다.", tool_call_id=cid, tier=3)
    r2 = design_sim.required_sample_for_pcs(tox, target_pcs=50.0, n_sim=1000)
    cid2 = _log(state, "design.required_sample_for_pcs", {"target_pcs": 50}, r2)
    if r2.ok:
        _ev(state, "calculation", "DoseVerdict", f"정확 MTD 선택률 50%를 목표로 하면 BOIN 기준 필요 n_max = {r2.data['required_n_max']} (격자 {[(g['n_max'], g['PCS']) for g in r2.data['grid']]}). 3+3은 알고리즘상 이 표본에 도달하지 못한다.", tool_call_id=cid2, tier=3)
    task.status = "done" if r.ok else "failed"


_REG_QUERIES = {
    "US": [("dose optimization randomized comparison of multiple dosages before RP2D", "FDA-DOSE-OPT-2024"),
           ("trial sized for sufficient assessment of safety and antitumor activity for each dosage, not powered for superiority", "FDA-DOSE-OPT-2024"),
           ("expansion cohort scientific rationale sample size safety monitoring", "FDA-EXPANSION-COHORTS-2022")],
    "KR": [("다양한 용량 비교 임상시험 설계 권장 용량 선정", "MFDS-1443-01-2025"),
           ("안전성 내약성 노출 기간 용량 감량 권장 용량", "MFDS-1443-01-2025")],
    "common": [("quality management critical to quality factors risk proportionate", "ICH-E6R3-2025"),
               ("dose-response information parallel dose-response design", "ICH-E4-1994")],
}


def run_regulatory_search(state: ReviewState, task: Task) -> None:
    from app.corpus.index import CorpusIndex
    from app.corpus.manifest import by_id
    country = task.task_id.rsplit("_", 1)[-1]
    juris = country if country in ("US", "KR") else None
    idx = CorpusIndex.get()
    # 공통(ICH) 조항은 첫 국가 검색에서만 붙인다 — 국가별 검색은 분리하되 같은 청크를 두 번 근거로 만들지 않는다
    seen = state.scratch.setdefault("clause_ids_seen", [])
    queries = _REG_QUERIES.get(country, []) + (_REG_QUERIES["common"] if not state.scratch.get("common_done") else [])
    state.scratch["common_done"] = True
    # 플래너가 가설별로 만든 검색 질의(국가 일치 또는 common)를 덧붙인다 — 고정 질의가 못 덮는 결함의 근거 조항 확보
    for q in state.review_questions:
        sq, qj = (q.get("search_query") or "").strip(), (q.get("jurisdiction") or "common")
        if sq and (qj == country or qj == "common" and not state.scratch.get("common_done_planner")):
            queries.append((sq, None))
    state.scratch["common_done_planner"] = True
    t0 = time.perf_counter()
    n = 0
    for q, _doc_hint in queries:
        hits = idx.search(q, k=3 if _doc_hint is None else 2, jurisdiction=juris)   # 플래너 생성 질의는 3건
        for h in hits:
            if h["chunk_id"] in seen or "....." in h["text"] or h["chunk_id"] in state.scratch.get("holdout_chunk_ids", []):   # 중복·목차·hold-out 제외
                continue
            seen.append(h["chunk_id"])
            doc = by_id(h["doc_id"])
            _ev(state, "regulatory_clause", doc.authority, h["text"], title=doc.title, section=h["heading"], applicability=h["jurisdiction"],
                norm_strength=h["norm_strength"], url=doc.url, tier=2, version_date=doc.effective_date)
            n += 1
    state.tool_log.append(ToolCall(tool_call_id=f"tc_{len(state.tool_log) + 1:03d}", tool="corpus.search", args={"country": country, "queries": len(queries)}, ok=n > 0,
                                   result_summary=f"{n} clauses", started_at=_now(), latency_s=round(time.perf_counter() - t0, 3)))
    state.budget.used_tool_calls += 1
    task.status = "done" if n else "failed"


def run_analog_trial(state: ReviewState, task: Task) -> None:
    ip = state.trial.study.investigational_product
    term = ip.target or ip.name or state.trial.study.indication or ""
    r = analog_trial.search_analog_trials(term, page_size=8)
    cid = _log(state, "ctgov.search_analog_trials", {"term": term}, r)
    if r.ok:
        st = r.data["studies"]
        rand = [s for s in st if (s.get("allocation") == "RANDOMIZED")]
        _ev(state, "analog_trial", "ClinicalTrials.gov", f"'{term}' Phase 1/2 등록 {r.data['total_count']}건 중 조회 {len(st)}건; 무작위 배정 {len(rand)}건 {[s['nct_id'] for s in rand][:4]}; 상태 {[s['overall_status'] for s in st][:8]}. 설계 구조 비교 전용.",
            url=r.source.get("url"), tool_call_id=cid, tier=2)
    task.status = "done" if r.ok else "failed"


RUNNERS = {
    "structure_class": run_structure_class, "target_evidence": run_target_evidence, "class_label_check": run_class_label_check,
    "exposure_dose_relationship": run_exposure_dose, "design_oc": run_design_oc, "regulatory_clause_search": run_regulatory_search,
    "analog_trial": run_analog_trial,
}


_CALC_KINDS = {"structure_class", "exposure_dose_relationship", "design_oc"}


def execute_tasks(state: ReviewState) -> ReviewState:
    """의존 순서대로 실행. 예산 초과 시 남은 과제는 skipped. ablation 'no_calc'면 계산 과제는 건너뛴다."""
    if "no_calc" in state.scratch.get("ablate", []):
        for t in state.tasks:
            if t.kind in _CALC_KINDS:
                t.status = "skipped"
    done: set[str] = set()
    pending = [t for t in state.tasks if t.status == "planned"]
    for _ in range(len(pending) + 1):
        progressed = False
        for t in pending:
            if t.status != "planned" or any(d not in done for d in t.depends_on):
                continue
            if state.budget.exhausted():
                t.status = "skipped"
                continue
            t.status = "running"
            try:
                RUNNERS[t.kind](state, t)
            except Exception as e:  # noqa: BLE001 — 실패도 관측값
                t.status = "failed"
                state.tool_log.append(ToolCall(tool_call_id=f"tc_{len(state.tool_log) + 1:03d}", tool=t.kind, args={}, ok=False, error=str(e)[:300], started_at=_now()))
            done.add(t.task_id)
            progressed = True
        if not progressed:
            break
    for t in state.tasks:
        if t.status == "planned":
            t.status = "skipped"
    return state
