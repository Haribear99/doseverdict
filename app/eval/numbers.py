"""
수치 원천표 — 기술서·발표·영상·README에 쓰는 모든 수치의 단일 출처(PRD P0-7). 결과 파일에서 자동 생성한다(토큰 0).

실행: .venv/Scripts/python.exe -m app.eval.numbers  →  docs/numbers.md
규칙: 제출물의 수치는 이 표에서만 가져온다. 결과가 바뀌면 이 스크립트를 다시 돌리고 모든 제출물을 재대조한다.
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "app" / "eval" / "data" / "results"


def _ci(xs: list[float], n_boot: int = 4000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    b = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(n_boot))
    return b[int(0.025 * n_boot)], b[int(0.975 * n_boot)]


def _subset(rows: list[dict]) -> str:
    """세트 이름은 case_id 접두어로 정한다(문자열 대소 비교는 새 접두어에서 틀린다)."""
    cid = rows[0]["case_id"] if rows else ""
    if cid.startswith("AXD-"):
        drugs = sorted({r["case_id"].split("-")[1].lower() for r in rows})
        return f"다약물 {len(rows)}({'·'.join(drugs)})"
    return "확장 40(AX1-021~060)" if cid >= "AX1-021" else "원 20(AX1-001~020)"


def config_rows(cfgs: list[tuple[str, str]]) -> list[str]:
    out = ["| 설정 | 설명 | 세트 | n | span recall | grounded (95% CI) | 검증 통과율 | 토큰/케이스 | LLM 실패 | 원천 |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for cfg, desc in cfgs:
        p = RES / f"{cfg}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        rows, a = d["rows"], d["aggregate"]
        lo, hi = _ci([r["grounded_recall"] for r in rows])
        fails = sum(r.get("llm_failures", 0) for r in rows) if any("llm_failures" in r for r in rows) else "—"
        subset = _subset(rows)
        out.append(f"| {cfg} | {desc} | {subset} | {len(rows)} | {a['recall']:.3f} | {a['grounded_recall']:.3f} [{lo:.3f}, {hi:.3f}] | "
                   f"{a['verified_rate']:.3f} | {a['tokens']:,.0f} | {fails} | `app/eval/data/results/{cfg}.json` |")
    return out


PAIRS = [  # (기준, 비교, 설명) — 기술서·발표의 쌍대 비교 수치는 이 절에서만 가져온다
    ("lean", "lean_combo", "09-11 배포 기본 → 현재 기본(원 20)"),
    ("lean", "lean_d3", "09-11 배포 기본 → 09-23 경화 코드(원 20)"),
    ("lean_d3", "lean_g6all", "경화 코드 → 전 노드 gpt-6-sol(원 20)"),
    ("lean_d3", "lean_combo", "경화 코드 → 현재 기본(원 20)"),
    ("lean_g6all", "lean_combo", "gpt-6-sol → + strict·250자(원 20)"),
    ("lean_d3ext", "lean_g6allext", "경화 코드 → 전 노드 gpt-6-sol(확장 40)"),
    ("lean_d3ext", "lean_comboext", "경화 코드 → 현재 기본(확장 40)"),
    ("lean_g6allext", "lean_comboext", "gpt-6-sol → + strict·250자(확장 40)"),
    ("lean_combo", "lean_v2", "09-25 기본 → 09-26 업그레이드 코드(원 20, 회귀)"),
    ("lean", "lean_v2", "09-11 배포 기본 → 09-26 업그레이드 코드(원 20)"),
    ("lean_combo", "lean_v3", "09-25 기본 → 최종 코드 1차 실행(원 20, 회귀)"),
    ("lean_combo", "lean_v3b", "09-25 기본 → 최종 코드 2차 실행(원 20, 회귀)"),
    ("lean_v3", "lean_v3b", "최종 코드 같은 설정 반복(원 20) — 실행 간 변동 크기"),
    ("lean", "lean_v3", "09-11 배포 기본 → 최종 코드 1차(원 20)"),
    ("lean", "lean_v3b", "09-11 배포 기본 → 최종 코드 2차(원 20)"),
    ("lean_mdrug", "lean_mdrug3", "09-26 코드 → 최종 코드(다약물 30)"),
]


def multidrug_lines(cfg: str = "lean_mdrug3") -> list[str]:
    """다약물 세트의 약물별 지표와 약리 축 도달(저장 상태에서 집계). 원 세트와 결함 풀은 같고 기준 시놉시스만 다르다."""
    from collections import Counter, defaultdict
    p = RES / f"{cfg}.json"
    if not p.exists():
        return []
    rows = json.loads(p.read_text(encoding="utf-8"))["rows"]
    by = defaultdict(list)
    for r in rows:
        by[r["case_id"].split("-")[1]].append(r)
    reach: dict[str, Counter] = defaultdict(Counter)
    tools: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for sp in sorted((RES / "states" / cfg).glob("*.json")):
        d = json.loads(sp.read_text(encoding="utf-8"))
        drug = sp.stem.split("-")[1]
        src = d["scratch"].get("tcr_source")
        st = next((t["status"] for t in d["tasks"] if t["kind"] == "exposure_dose_relationship"), "없음")
        reach[drug][f"{'TCR 계산' if src else 'TCR 기권(입력 부족)'}·{st}"] += 1
        for c in d["tool_log"]:
            tools[drug][0 if c["ok"] else 1] += 1
    out = ["| 약물(기준 시놉시스) | n | span recall | grounded (95% CI) | 검증 통과율 | precision proxy | 토큰/케이스 | 도구 성공/실패 | 약리 축(TCR) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for drug, v in sorted(by.items()):
        lo, hi = _ci([r["grounded_recall"] for r in v])
        m = lambda k: sum(r[k] for r in v) / len(v)
        out.append(f"| {drug.lower()} | {len(v)} | {m('recall'):.3f} | {m('grounded_recall'):.3f} [{lo:.3f}, {hi:.3f}] | {m('verified_rate'):.3f} | "
                   f"{m('precision_proxy'):.3f} | {m('tokens'):,.0f} | {tools[drug][0]}/{tools[drug][1]} | {', '.join(f'{k} {n}' for k, n in reach[drug].most_common())} |")
    return out + ["", "도구 실패의 대부분은 미승인 후보(DV-505)의 openFDA 라벨 404(라벨이 없는 것이 정상)다. 약리 축 'TCR 기권(입력 부족)'은 PK·구조·IC50 중 하나를 얻지 못해 전형값 없이 멈춘 경우다.", ""]


def pair_lines() -> list[str]:
    from app.eval.compare import load, paired, verdict
    out = ["| 비교 | n | 토큰/케이스 차이 [95% CI] | 토큰 비율 | grounded [95% CI] | 검증 [95% CI] | precision [95% CI] | 사전 규칙 |",
           "|---|---|---|---|---|---|---|---|"]
    for b, a, desc in PAIRS:
        if not ((RES / f"{b}.json").exists() and (RES / f"{a}.json").exists()):
            continue
        base, arm = load(b), load(a)
        t, tl, th, n = paired(base, arm, "tokens")
        rel = sum(arm[c]["tokens"] for c in arm if c in base) / sum(base[c]["tokens"] for c in arm if c in base) - 1
        cells = []
        for k in ("grounded_recall", "verified_rate", "precision_proxy"):
            m, lo, hi, _ = paired(base, arm, k)
            cells.append(f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        out.append(f"| {desc} (`{b}`→`{a}`) | {n} | {t:+,.0f} [{tl:+,.0f}, {th:+,.0f}] | {rel:+.1%} | " + " | ".join(cells)
                   + f" | {verdict(base, arm).split(' ')[0]} |")
    return out + ["", "쌍대 부트스트랩 5,000회(`app/eval/compare.py`, seed 0). 사전 규칙: 기각 = 토큰 +2% 초과 또는 grounded·검증 점추정 −5pp 초과 하락, 채택 = 토큰 −15% 이하 또는 grounded CI 하한 > 0, 그 외 보류.", ""]


MEAN_PAIRS = [  # (기준, [같은 설정 반복 실행들], 설명) — 반복 실행의 케이스별 평균을 한 팔로 비교한다
    ("lean", ["lean_v3", "lean_v3b"], "09-11 배포 기본 → 최종 코드 2회 평균(원 20)"),
    ("lean_combo", ["lean_v3", "lean_v3b"], "09-25 기본 → 최종 코드 2회 평균(원 20)"),
]


def mean_pair_lines() -> list[str]:
    """같은 설정을 여러 번 돌린 실행의 케이스별 평균을 한 팔로 삼는다. 기준선은 1회 실행이므로 기준선 쪽 실행 변동은 여전히 CI에 들어가지 않는다."""
    from app.eval.compare import load, paired
    out = ["| 비교 | n | 토큰 비율 | grounded [95% CI] | 검증 [95% CI] |", "|---|---|---|---|---|"]
    for b, arms, desc in MEAN_PAIRS:
        if not all((RES / f"{c}.json").exists() for c in [b, *arms]):
            continue
        base, runs = load(b), [load(a) for a in arms]
        cases = [c for c in base if all(c in r for r in runs)]
        arm = {c: {k: sum(r[c][k] for r in runs) / len(runs) for k in ("grounded_recall", "verified_rate", "tokens")} for c in cases}
        rel = sum(arm[c]["tokens"] for c in cases) / sum(base[c]["tokens"] for c in cases) - 1
        cells = []
        for k in ("grounded_recall", "verified_rate"):
            m, lo, hi, _ = paired(base, arm, k)
            cells.append(f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        out.append(f"| {desc} (`{b}`→`{'+'.join(arms)}`) | {len(cases)} | {rel:+.1%} | " + " | ".join(cells) + " |")
    return out + ["", "케이스 단위 부트스트랩 CI는 실행 간 변동을 담지 못한다. 같은 설정 반복(`lean_v3`→`lean_v3b`)에서 grounded +0.067 [−0.000, +0.133]이 나왔으므로, 1회 실행 grounded 차이는 CI가 0을 벗어나도 점추정으로만 해석한다.", ""]


def usage_lines() -> list[str]:
    """원천 = 감사로그 공개 집계본(`app/eval/data/audit_usage.jsonl`, `python -m app.eval.audit_export`로 갱신). 쿼터 헤더는 09-22 한도 재설정 이후 값만 보여 누적 사용량과 대조할 수 없다."""
    from collections import Counter

    from app.eval.audit_export import iter_audit
    tot, last_ts, by_day, by_model = 0, "", Counter(), Counter()
    for r in iter_audit():
        u = r["usage"]["total_tokens"]
        tot += u
        by_day[r["ts"][:10]] += u
        by_model[r.get("model")] += u
        last_ts = max(last_ts, r["ts"])
    out = [f"- 합계 **{tot:,}** 토큰(총 쿼터 6,000만의 {tot / 60_000_000:.1%}), 마지막 호출 {last_ts[:16]} UTC.",
           "- 일자별(UTC): " + ", ".join(f"{d} {v:,}" for d, v in sorted(by_day.items())),
           "- 모델별: " + ", ".join(f"{m} {v:,}" for m, v in by_model.most_common())]
    return out + ["- 원본 `logs/`는 git·Docker에서 제외되고, 재현에 필요한 필드(시각·모델·용도·usage)만 공개 집계본으로 커밋한다. 이 절이 제출물의 누적 토큰 단일 출처다.", ""]


def retro_lines() -> list[str]:
    """실사례 후향 검증(`app/eval/retro.py`, 사전 등록 `docs/retro_prereg.md`)."""
    fp = ROOT / "app/eval/data/results/retro.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    m, d = r["metrics"], r.get("descriptive_post_hoc") or {}
    desc = {"S1": "1차: 검증된 용량최적화 finding 수", "S2": "2차: 중증도 가중합(검증+보류)", "B1": "키워드 규칙(초록)", "B2": "승인연도",
            "B3": "축③ 라벨 규칙(승인 후 라벨, 참고)", "B4": "사후: 약 이름을 준 모델 기억"}
    out = [f"n = {r['n']}(양성 {r['n_pos']}, 무작위 PR-AUC {r['n_pos'] / r['n']:.3f}). 판정: **{r['verdict']}**", "",
           "| 점수 | 설명 | n | AUROC [95% CI] | PR-AUC |", "|---|---|---|---|---|"]
    for k in ("S1", "S2", "B1", "B2", "B3", "B4"):
        if k in m:
            out.append(f"| {k} | {desc[k]} | {m[k].get('n', r['n'])} | {m[k]['auroc']:.3f} [{m[k]['ci'][0]:.3f}, {m[k]['ci'][1]:.3f}] | {m[k]['pr_auc']:.3f} |")
    post = r.get("reidentification_post_hoc") or {}
    out += ["", f"- 재식별 탐침(사전 등록): {r.get('reidentification_rate')} · 사후 변형: SMILES 제거 {post.get('nosmiles')}, SMILES·표적·기전 제거 {post.get('noid')}",
            f"- 사후 기술통계: 용량최적화 지적 ≥1 {d.get('flagged_S1_ge1')}/{r['n']}, 평균 S1 양성 {d.get('mean_S1_pos')} · 음성 {d.get('mean_S1_neg')}, F00 기권 {d.get('f00_abstain')}/{r['n']}, "
            f"S1–B4 Spearman ρ {(d.get('spearman_S1_B4') or [None])[0]} (p {(d.get('spearman_S1_B4') or [None, None])[1]}), 토큰 {d.get('tokens_total', 0):,}(케이스당 {d.get('tokens_per_case', 0):,})",
            f"- 사후(red-judge 09-29): 템플릿 문장 유발 S1 지적 {d.get('S1_template')}/{d.get('S1_total')}건(제외 시 지적 케이스 {d.get('flagged_excl_template')}/{r['n']}), 지적 정확성 미평가, "
            f"파이프라인이 약 이름을 스스로 복원 {d.get('name_restored')}/{r['n']}(양성 {d.get('name_restored_pos')}), 마스킹 누락 코드명 1건(E7080, RETRO-13 lenvatinib)", ""]
    return out


def oneshot_lines() -> list[str]:
    """강한 LLM 원샷 베이스라인(`app/eval/oneshot.py`, 사전 등록 `docs/oneshot_prereg.md`)."""
    fp = ROOT / "app/eval/data/results/oneshot_compare.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    out = ["| 팔 | n | grounded 에이전트 / 팔 | 차이(팔−에이전트) [95% CI] | span 차이 | precision 차이 | 토큰/케이스 에이전트 / 팔 | 판정 |", "|---|---|---|---|---|---|---|---|"]
    for name, a in r["arms"].items():
        g, sp, pr = a["grounded_diff"], a["span_diff"], a["precision_diff"]
        out.append(f"| {name} | {a['n']} | {a['grounded_agent']:.3f} / {a['grounded_arm']:.3f} | {g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}] | {sp[0]:+.3f} [{sp[1]:+.3f}, {sp[2]:+.3f}] | "
                   f"{pr[0]:+.3f} [{pr[1]:+.3f}, {pr[2]:+.3f}] | {a['tokens_agent']:,} / {a['tokens_arm']:,} | {a['verdict'] if name.startswith('oneshot') else '기술용(1회)'} |")
    out += ["", "에이전트 = `lean_v3`+`lean_v3b` 케이스별 평균. 원샷 = gpt-6-sol 단일 호출(effort medium, 도구·검색·검증 없음, 문서 목록만) 2회 평균. "
            "에이전트는 결함 출처 조항을 검색에서 뺀(hold-out) 조건이고 원샷은 모델 기억에 제한이 없어, 이 비교는 원샷에 유리한 쪽이다.", "",
            "| 인용 충실도 | 인용문 | 원문 일치 | 비율(전체) | 검사 불가(본문 미색인 문서) | 비율(검사 가능분) |", "|---|---|---|---|---|---|"]
    for cfg, q in r.get("quote_fidelity", {}).items():
        out.append(f"| {cfg} | {q['n_quotes']} | {q['matched']} | {q['rate']} | {q['unknown_doc_id']} | {q['rate_checkable']} |")
    ph = r.get("post_hoc") or {}
    if ph:
        fa, fo, fe, sy = ph["fidelity"]["agent"], ph["fidelity"]["oneshot"], ph["fidelity"]["agent_evidence_quote"], ph["symmetric_grounded"]
        pct = lambda n, d: f"{n / max(1, d):.1%}"
        out += ["", "사후(사전 등록 밖) — 같은 인용 판정기를 양쪽에(에이전트 evidence_fact / 원샷 guidance_quote):", "",
                "| 쪽 | 검사 가능 | 원문 일치 | 일치 또는 NLI 의역 | 둘 다 아님 |", "|---|---|---|---|---|",
                f"| 에이전트 | {fa['checkable']} | {fa['exact']} ({pct(fa['exact'], fa['checkable'])}) | {fa['exact_or_nli']} ({pct(fa['exact_or_nli'], fa['checkable'])}) | {fa['unsupported']} ({pct(fa['unsupported'], fa['checkable'])}) |",
                f"| 원샷 | {fo['checkable']} | {fo['exact']} ({pct(fo['exact'], fo['checkable'])}) | {fo['exact_or_nli']} ({pct(fo['exact_or_nli'], fo['checkable'])}) | {fo['unsupported']} ({pct(fo['unsupported'], fo['checkable'])}) |", "",
                f"- 에이전트 근거 풀의 규제 조항 인용문(evidence.quote) {fe['verbatim']}/{fe['n']}건이 코퍼스 원문(정규화한 앞 200자 포함 기준)."]
        for k, lab in (("exact", "원문 일치만"), ("nli", "일치 또는 NLI 의역")):
            d = sy[k]["diff"]
            out.append(f"- 대칭 필터({lab}) grounded: 에이전트 {sy[k]['agent']:.3f}, 원샷 {sy[k]['oneshot']:.3f}, 차이(원샷 − 에이전트) {d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}]")
        out.append(f"- 한국어 등 문자열 판정 불가 인용: 에이전트 {fa.get('non_latin_uncheckable')}건, 원샷 {fo.get('non_latin_uncheckable')}건 — 검사 불가로 빼고 grounded에서 불인정(에이전트에 불리).")
        out.append("- NLI 의역 판정은 인용 문서의 가까운 조항 3개만 본다(임계 0.7, 결과를 본 뒤 정한 단일 설정). 판정 모델은 에이전트 검증기와 같다(에이전트에 유리).")
    return out + [""]


def abstain_lines() -> list[str]:
    """기권 평가(`app/eval/abstain_eval.py`, 사전 등록 `docs/abstain_prereg.md`). A′는 사후 조건."""
    fp = ROOT / "app/eval/data/results/abstain.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    f = lambda s: f"{s['mean']:.3f} ({s['min']:.3f}–{s['max']:.3f})" if s else "—"
    A, B, M = r["A"], r["B"], r.get("A_mem") or {}
    g = lambda k: f(M.get(k)) if M else "—"
    out = [f"항목(약 × 용량군) {r['n_items']}개, 정답(도구 판정) {r['truth_counts']}. 원샷 = gpt-6-sol 단일 호출(effort medium, 도구 없음), 조건마다 약 4종 × 3회. 지시문에 기권 선택지(indeterminate·cannot_assess)와 그 정의를 줬다.", "",
           "| 지표 | 조건 A(시놉시스만) | 조건 B(도구 입력·규칙 제공) | 사후 A′(시놉시스 + 기억·추정 권장) |", "|---|---|---|---|",
           f"| A-1 정답 indeterminate에서 확정 판정(1차) | {f(A['definite_on_indeterminate'])} | {f(B['definite_on_indeterminate'])} | {g('definite_on_indeterminate')} |",
           f"| A-3 정답 covered에서 기권 | {f(A['abstain_on_covered'])} | {f(B['abstain_on_covered'])} | {g('abstain_on_covered')} |",
           f"| B-2 도구 판정 일치율 | {f(A['agreement'])} | {f(B['agreement'])} | {g('agreement')} |",
           f"| A-2 입력에 없는 수치 비율(조건 A는 분자량 등 유도 수치) | {f(A['unsourced_number_rate'])} | {f(B['unsourced_number_rate'])} | {g('unsourced_number_rate')} |",
           f"| B-1 TCR_avg / TCR_trough 상대 오차 중앙값 | {A['median_rel_err_tcr_avg']} / {A['median_rel_err_tcr_trough']} | {B['median_rel_err_tcr_avg']} / {B['median_rel_err_tcr_trough']} | {M.get('median_rel_err_tcr_avg')} / {M.get('median_rel_err_tcr_trough')} |",
           f"| 토큰 | {A['tokens_total']:,} | {B['tokens_total']:,} | {M.get('tokens_total', 0):,} |", ""]
    rep = (ROOT / "app/eval/data/results/ABSTAIN_REPORT.md").read_text(encoding="utf-8")
    out += [l for l in rep.splitlines() if l.startswith("- 조건 ") or l.startswith("- 사후 A′") or l.startswith("- 반복 일관성")]
    out += ["- 조건 A의 A-1 = 0 분해: 정답 indeterminate 7건 중 5건(소토라십 4, 아다그라십 150 mg)은 자료 부족으로 cannot_assess였고, 지표 의존을 인지해 멈춘 것은 DV-505 2건이다.",
            "- 에이전트는 같은 도구 판정을 내므로 도구 일치율은 정의상 1이다(순환성). '도구 판정과 불일치'는 도구 모형(선형 1구획, ChEMBL 중앙값 IC50) 기준의 차이이지 실제 오답이라는 뜻이 아니다. 반복 간 일관성은 도구와 무관한 모델 내부 지표다.", ""]
    return out


def specificity_lines() -> list[str]:
    """특이도 평가(`app/eval/specificity.py`, 사전 등록 `docs/specificity_prereg.md`)."""
    fp = ROOT / "app/eval/data/results/specificity.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    out = ["A. 문장 단위(기준 문장 = 결함 없음으로 가정한 하한). 지적 = defect finding span이 문장과 겹침(F00 제외).", "",
           "| 실행 | n | 민감도 [95% CI] | 특이도 [95% CI] | Youden J [95% CI] |", "|---|---|---|---|---|"]
    for cfg in ("lean_v3", "lean_v3b", "lean_mdrug3"):
        s_ = r["A"][cfg]["summary"]
        out.append(f"| {cfg} | {s_['n_cases']} | {s_['sensitivity']:.3f} {s_['sensitivity_ci']} | {s_['specificity']:.3f} {s_['specificity_ci']} | {s_['youden_j']:.3f} {s_['youden_ci']} |")
    b, c = r.get("B"), r.get("C")
    if b:
        out += ["", f"B. 결함 없는 기준 시놉시스 {len(b['runs'])}회: 특이도 {b['specificity']}, 실행당 지적된 기준 문장 {b['mean_flagged_base_sentences']}, defect finding {b['mean_defect_findings']}, 토큰 {b['tokens_total']:,}"]
    if c:
        out += [f"C. 수정안 적용 재검토 {c['n_cases']}케이스·수정안 {c['n_patches']}건: 수정된 문장 재지적률 {c['re_flag_rate']}, defect finding {c['defects_before_mean']} → {c['defects_after_mean']}, "
                f"수정하지 않은 주입 문장 지적 {c['unpatched_inj_keep'][0]} → {c['unpatched_inj_keep'][1]}, 토큰 {c['tokens_total']:,}"]
    return out + [""]


def calibration_lines() -> list[str]:
    """특이도 보정 A/B(`docs/calibration_prereg.md`, `specificity.py::calibration`)."""
    fp = ROOT / "app/eval/data/results/calibration.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    g, sp = r["grounded_diff"], r["span_diff"]
    return ["| 지표 | 현재 | 보정판(DV_FINDINGS_CALIBRATED=1) |", "|---|---|---|",
            f"| 결함 없는 기준 시놉시스 문장 특이도(12회) | {r['clean_specificity'][0]} | {r['clean_specificity'][1]} |",
            f"| 결함 없는 기준 시놉시스 실행당 defect finding | {r['clean_defects_per_run'][0]} | {r['clean_defects_per_run'][1]} |",
            f"| 원 20 문장 민감도(현재 = 2회 평균) | {r['orig_sentence_sensitivity'][0]} | {r['orig_sentence_sensitivity'][1]} |",
            f"| 원 20 문장 특이도 | {r['orig_sentence_specificity'][0]} | {r['orig_sentence_specificity'][1]} |",
            f"| 원 20 Youden J(민감도 + 특이도 − 1) | {r['orig_youden_j'][0]} | {r['orig_youden_j'][1]} |",
            f"| grounded 차이(보정 − 현재 2회 평균) [95% CI] | — | {g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}] |",
            f"| span recall 차이 [95% CI] | — | {sp[0]:+.3f} [{sp[1]:+.3f}, {sp[2]:+.3f}] |", "",
            f"사전 규칙 판정: **{r['verdict']}** — 특이도는 올랐지만 민감도 하락이 0.05를 넘었다. 운영점만 옮긴 것이 아니라 판별력(Youden J)도 낮아졌다. 보정판은 기본값이 아닌 '보수적 지적' 선택지로만 둔다. 보정판 양성은 1회 실행이다.", ""]


def hybrid_lines() -> list[str]:
    """원샷 + 같은 인용 판정기, 결함 없는 판 비교(`docs/hybrid_prereg.md`, `hybrid.py`)와 사후 원 20 문장 단위 J."""
    fp = ROOT / "app/eval/data/results/hybrid.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    a = r["agent"]
    out = ["| 팔(결함 없는 기준 시놉시스 4종 × 3회) | 지적된 기준 문장/실행 | 특이도 | finding/실행 | 토큰/실행 | 차이(팔 − 에이전트) [95% CI] |", "|---|---|---|---|---|---|",
           f"| 에이전트(평가 B) | {a['flagged_per_run']} | {a['specificity']} | {a['findings_per_run']} | {a['tokens_per_run']:,} | — |"]
    for k, v in r["arms"].items():
        d = v["diff"]
        out.append(f"| {k} | {v['flagged_per_run']} | {v['specificity']} | {v['findings_per_run']} | {v['tokens_per_run']:,} | {d[0]:+.2f} [{d[1]:+.2f}, {d[2]:+.2f}] |")
    out += ["", f"사전 등록 판정: **{r['verdict']}**. 판정기는 인용 판정기이며 에이전트 검증기 전체가 아니다.", "",
            "사후(사전 등록 밖, 원 20 원샷 결과는 이미 본 데이터) — 문장 단위 민감도·특이도·J(평가 A와 같은 규칙):", "",
            "| 팔 · 실행 | 민감도 | 특이도 | Youden J [95% CI] |", "|---|---|---|---|"]
    for k, v in r.get("post_hoc_orig20", {}).items():
        out.append(f"| {k} | {v['sensitivity']:.3f} | {v['specificity']:.3f} | {v['youden_j']:.3f} {v['youden_ci']} |")
    return out + [""]


def refute_lines() -> list[str]:
    """반박 가능한 Review Arena A/B(`docs/refute_prereg.md`, `specificity.py::refute_ab`)."""
    fp = ROOT / "app/eval/data/results/refute_ab.json"
    if not fp.exists():
        return ["(결과 없음)", ""]
    r = json.loads(fp.read_text(encoding="utf-8"))
    c, o, m = r["clean"], r["orig20"], r["multidrug30"]
    d, g, gm = c["flagged_diff"], o["grounded_diff"], m["grounded_diff"]
    out = ["| 지표 | 현재 기본 | 반박 모드 |", "|---|---|---|",
           f"| 결함 없는 판(12회): 지적 기준 문장/실행 · 특이도 · defect finding/실행 | {c['current']['mean_flagged_base_sentences']} · {c['current']['specificity']} · {c['current']['mean_defect_findings']} | {c['refute']['mean_flagged_base_sentences']} · {c['refute']['specificity']} · {c['refute']['mean_defect_findings']} (차이 {d[0]:+.2f} [{d[1]:+.2f}, {d[2]:+.2f}]) |",
           f"| 원 20: 민감도 · 특이도 · Youden J (현재 = 2회 평균) | {o['current']['sensitivity']} · {o['current']['specificity']} · {o['current']['sensitivity'] + o['current']['specificity'] - 1:.3f} | {o['refute']['sensitivity']} · {o['refute']['specificity']} · {o['refute']['youden_j']} |",
           f"| 다약물 30(확인용): 민감도 · 특이도 · Youden J | {m['current']['sensitivity']} · {m['current']['specificity']} · {m['current']['youden_j']} | {m['refute']['sensitivity']} · {m['refute']['specificity']} · {m['refute']['youden_j']} |",
           f"| grounded 차이(반박 − 현재) [95% CI] | — | 원 20 {g[0]:+.3f} [{g[1]:+.3f}, {g[2]:+.3f}] · 다약물 {gm[0]:+.3f} [{gm[1]:+.3f}, {gm[2]:+.3f}] |", ""]
    rules = " · ".join(f"{k} {'충족' if v else '미충족'}" for k, v in r["rules"].items())
    return out + [f"사전 규칙 판정: **{r['verdict']}** — {rules}.", ""]


def main() -> None:
    cfgs = [
        ("full", "09-11 본평가: Reviewer 3인"), ("lean", "09-11 기본: Reviewer 1인 + 재선택"),
        ("no_arena", "ablation: Reviewer 없음"), ("no_calc", "ablation: 계산 도구 없음"), ("no_verifier", "ablation: 검증기 없음"),
        ("lean_d3", "09-23 새 코드 기준선(구조화 출력 경화·불변식·범주 필터)"), ("lean_cnone", "A/B: compile effort none"),
        ("lean_strict", "A/B: reviewers·findings strict"), ("lean_q250", "A/B: 근거 인용문 250자"), ("lean_notopic", "A/B: 주제 태그 프롬프트 제거"), ("lean_fmed", "A/B: findings effort medium"),
        ("lean_c6sol", "A/B: compile gpt-6-sol"), ("lean_g6all", "A/B: 전 노드 gpt-6-sol"), ("lean_combo", "09-25 기본: gpt-6-sol + strict + 인용문 250자"),
        ("lean_d3ext", "09-23 새 코드, 확장 세트"), ("lean_g6allext", "전 노드 gpt-6-sol, 확장 세트"), ("lean_comboext", "09-25 기본, 확장 세트"),
        ("lean_v2", "09-26 업그레이드 코드(약물 무관화·보류 재검색·예산 가드)"), ("lean_mdrug", "09-26 업그레이드 코드, 다약물 세트"),
        ("lean_v3", "최종 코드(c7dc0be, 투여 간격 수정) 1차"), ("lean_v3b", "최종 코드 2차(같은 설정 반복)"), ("lean_mdrug3", "최종 코드, 다약물 세트"),
    ]
    tcr = json.loads((ROOT / "evidence" / "tcr_240mg.json").read_text(encoding="utf-8"))
    lines = [f"# 수치 원천표 (자동 생성 {datetime.now():%Y-%m-%d %H:%M}, `python -m app.eval.numbers`)", "",
             "제출물(기술서·발표·영상·README·데모 화면)의 모든 수치는 이 표에서만 가져온다. 점추정 간 차이는 n=20에서 대부분 신뢰구간이 겹친다 — 유의 여부는 `python -m app.eval.compare`로 확인한 것만 주장한다.", "",
             "## 1. 평가(축① Silver Set — 원·확장 세트는 기준 시놉시스 DV-DEMO-002, 다약물 세트는 아다그라십·로를라티닙·DV-505(가상) 시놉시스의 결함 주입 변형)", ""] + config_rows(cfgs) + [
             "", "## 1-1. 다약물 세트 약물별(`lean_mdrug3`, 최종 코드)", ""] + multidrug_lines() + [
             "", "## 1-2. 쌍대 비교(같은 케이스끼리)", ""] + pair_lines() + ["## 1-3. 반복 실행 평균 비교", ""] + mean_pair_lines() + [
             "## 1-4. 실사례 후향 검증(승인 전 1상 초록 → FDA 용량최적화 PMR/PMC, `retro.json`)", ""] + retro_lines() + [
             "## 1-5. 강한 LLM 원샷 베이스라인(원 20, `oneshot_compare.json`)", ""] + oneshot_lines() + [
             "## 1-6. 기권 평가(도구 없는 원샷의 표적 커버리지 판정, `abstain.json`)", ""] + abstain_lines() + [
             "## 1-7. 특이도 평가(문장 단위·음성 대조·수정안 재검토, `specificity.json`)", ""] + specificity_lines() + [
             "## 1-8. 특이도 보정 A/B(`calibration.json`)", ""] + calibration_lines() + [
             "## 1-9. 원샷 + 같은 인용 판정기, 결함 없는 판(`hybrid.json`)", ""] + hybrid_lines() + [
             "## 1-10. 반박 가능한 Review Arena A/B(`refute_ab.json`)", ""] + refute_lines() + [
             "## 2. 소토라십 240 mg TCR (`evidence/tcr_240mg.json`)", "",
             "| 가정 | C_max | C_avg | C_trough | 판정 |", "|---|---|---|---|---|"]
    for r in tcr["rows"]:
        lines.append(f"| {r['assumption']} | {r['TCR_max']} | {r['TCR_avg']} | {r['TCR_trough']} | {r['verdict']} |")
    lines += [f"\n종합: **{tcr['overall']}** — {tcr['overall_reason']}", "",
              "## 3. 게이트웨이 실측 (`docs/gateway_probe.md`)", "",
              "- 쿼터: 총 6,000만(09-22 공지). 09-23 13:45 헤더 잔여 59,999,986. 과금 = usage.total_tokens 1:1(모델별 가중치 없음, reasoning 포함).",
              "- 캐시: gpt-6-luna 적중 2,780토큰에도 차감 2,788 → 캐시 절감 0(⑩-b).",
              "- 모델: gpt-5.6-sol/terra/luna, gpt-6-sol/luna 200 / gpt-6-astra 404(09-11·09-23). 기본값은 09-24부터 planner·reviewer·extract 모두 gpt-6-sol.",
              "- 토큰 구성: reasoning 비중 gpt-5.6 세대 3.7~4.9%, gpt-6-sol 0.9~1.0%. 입력이 약 70~80%(`docs/token_ledger.md`).", "",
              "## 4. 누적 사용량 (감사로그 공개 집계본 `app/eval/data/audit_usage.jsonl`의 usage.total_tokens 합)", ""] + usage_lines()
    (ROOT / "docs" / "numbers.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
