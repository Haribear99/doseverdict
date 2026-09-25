"""약물 무관화(09-26) — PK 출처 우선순위·기본값 제거·폴백 경로를 네트워크 없이 검증."""
from app.agents import nodes
from app.agents.findings import deterministic_tcr_finding
from app.schema.trial_schema import DoseLevel, ProtocolPK, ReviewState, Task
from app.tools import ToolResult


def _state(**ip) -> ReviewState:
    st = ReviewState(run_id="t")
    for k, v in ip.items():
        setattr(st.trial.study.investigational_product, k, v)
    st.trial.design.dose_strategy.dose_levels = [DoseLevel(label=f"L{i}", dose=f"{d} mg") for i, d in enumerate((100, 200, 400), 1)]
    return st


def _task(kind: str) -> Task:
    return Task(task_id="T", kind=kind, rationale="test")


def test_label_pk_has_priority_over_protocol():
    st = _state(clinical_pk=ProtocolPK(cl_f_L_per_hr=10, t_half_hr=12))
    st.scratch["label_pk"] = {"cl_f_L_per_hr": 26.2, "t_half_hr": 5.0, "protein_binding_pct": 89.0, "brand": "X"}
    pk, src = nodes._pk_inputs(st)
    assert pk["cl"] == 26.2 and src.startswith("FDA 라벨")


def test_protocol_pk_used_when_no_label():
    st = _state(clinical_pk=ProtocolPK(cl_f_L_per_hr=10, t_half_hr=12, protein_binding_pct=90, dosing_interval_hr=12, ic50_nM=5))
    pk, src = nodes._pk_inputs(st)
    assert pk["cl"] == 10 and pk["tau"] == 12 and src == "프로토콜 보고 PK"


def test_no_typical_defaults_abstain_with_reason():
    st = _state(name="XYZ-1")          # PK·구조·IC50 모두 없음 → 소토라십 기본값을 쓰지 않고 기권
    t = _task("exposure_dose_relationship")
    nodes.run_exposure_dose(st, t)
    assert t.status == "abstained"
    q = next(iter(st.evidence.values())).quote
    assert "CL/F" in q and "MW" in q and "IC50" in q and "전형값" in q
    assert not any(tc.tool == "pharm.tcr_three_metrics" for tc in st.tool_log)


def test_protocol_pk_runs_tcr_with_sources():
    st = _state(clinical_pk=ProtocolPK(cl_f_L_per_hr=20, t_half_hr=6, ic50_nM=50))   # 단백결합 없음 → cLogP 추정 f_u
    st.scratch["structure"] = {"properties": {"MW": 500.0}, "fu_estimated": 0.1, "structural_class": ["no_reactive_warhead_alert"]}
    t = _task("exposure_dose_relationship")
    nodes.run_exposure_dose(st, t)
    assert t.status in ("done", "abstained")
    q = [e.quote for e in st.evidence.values() if "TCR" in e.quote][0]
    assert "프로토콜 보고 PK" in q and "추정" in q and "1일 1회 가정" in q and "비선형" not in q
    if st.scratch["tcr_split"]:
        f = deterministic_tcr_finding(st)
        assert "라벨의 노출 유사" not in f.claim and "kinact" not in " ".join(f.required_additional_data)


def test_label_generic_fallback_and_unapproved(monkeypatch):
    calls = []

    def fake_label(brand=None, generic=None):
        calls.append((brand, generic))
        if generic == "NEWDRUG":
            return ToolResult(tool="openfda.label", ok=False, error="HTTPError: HTTP Error 404: Not Found")
        return ToolResult(tool="openfda.label", ok=True, data={"brand": "BRANDX", "generic": [generic], "pk": {"cl_f_L_per_hr": 5.0, "t_half_hr": 10.0},
                                         "liver_monitoring_statements": [], "nonlinear_pk_statement": None,
                                         "exposure_response_unknown_statement": None, "effective_time": "2025"})

    monkeypatch.setattr(nodes.pharmacology, "openfda_label", fake_label)
    st = _state(name="NewDrug", target="EGFR")
    st.scratch["approved_same_target"] = ["OTHERDRUG"]
    t = _task("class_label_check")
    nodes.run_class_label_check(st, t)
    assert calls == [(None, "NEWDRUG"), (None, "OTHERDRUG")]
    assert st.scratch.get("no_label") and t.status == "done"            # 미승인 404는 실패가 아니다
    assert not any(e.get("trigger") == "tool_failure" for e in st.replan_events)


def test_tau_uses_dose_levels_not_other_sentences():
    """09-26 red-judge: 주입 문장 '240 mg twice daily'를 시험약 투여 간격으로 오인해 원 세트 4/20에서 240 mg 기권이 빠졌다."""
    st = _state()
    st.trial.design.dose_strategy.dose_levels = [DoseLevel(label="L1", dose="180 mg once daily, oral"), DoseLevel(label="L2", dose="360 mg once daily, oral")]
    st.raw_protocol_text = "Planned dose levels (once daily). After the lead-in, all participants will receive 240 mg twice daily."
    assert nodes._tau(st)[0] == 24.0
    st.trial.design.dose_strategy.dose_levels = [DoseLevel(label="L1", dose="150 mg twice daily"), DoseLevel(label="L2", dose="600 mg BID")]
    assert nodes._tau(st)[0] == 12.0
    st.trial.design.dose_strategy.dose_levels = [DoseLevel(label="L1", dose="150 mg twice daily"), DoseLevel(label="L2", dose="300 mg once daily")]
    assert nodes._tau(st) == (None, "용량군 투여 간격 표기 충돌")


def test_missing_inputs_produce_visible_abstain_finding():
    st = _state(name="XYZ-1")
    nodes.run_exposure_dose(st, _task("exposure_dose_relationship"))
    f = deterministic_tcr_finding(st)
    assert f and f.verdict == "abstain" and "IC50" in f.abstain_reason and f.evidence_ids
