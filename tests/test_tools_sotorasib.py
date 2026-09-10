"""
소토라십 고정 케이스 회귀 테스트 — evidence/검증된_근거_모음.md 기대값과 대조.
네트워크 호출(ChEMBL·openFDA·CT.gov)은 `-m network` 마커로 분리한다.
"""
import pytest

from app.schema.trial_schema import ReviewState, TrialSchema
from app.tools import design_sim, pharmacology

SMILES = "C=CC(=O)N1CCN(c2nc(=O)n(-c3c(C)ccnc3C(C)C)c3nc(-c4c(O)cccc4F)c(F)cc23)[C@@H](C)C1"


def test_schema_roundtrip():
    s = ReviewState(run_id="r1", trial=TrialSchema())
    s.trial.design.dose_strategy.rp2d_rule_text = "The MTD will be selected as the RP2D."
    d = s.model_dump()
    s2 = ReviewState.model_validate(d)
    assert s2.trial.design.dose_strategy.rp2d_rule_text.startswith("The MTD")
    assert s2.budget.max_tokens == 150_000 and not s2.budget.exhausted()


def test_rdkit_profile_matches_evidence():
    r = pharmacology.structure_profile(SMILES)
    assert r.ok, r.error
    p = r.data["properties"]
    assert abs(p["MW"] - 560.61) < 0.05
    assert abs(p["cLogP"] - 4.48) < 0.02
    assert abs(p["TPSA"] - 104.45) < 0.05
    assert "irreversible_covalent_inhibitor_candidate" in r.data["structural_class"]
    assert len(r.data["alerts"]) == 3
    assert abs(r.data["fu_estimated"] - 0.113) < 0.002


def test_tcr_three_metrics_split():
    mw = 560.61
    r960 = pharmacology.tcr_three_metrics(960, 26.2, mw, 0.11, 30.0, t_half_hr=5.0)
    r240 = pharmacology.tcr_three_metrics(240, 26.2, mw, 0.11, 30.0, t_half_hr=5.0)
    assert r960.ok and r240.ok
    assert abs(r960.data["TCR_max"] - 34.5) < 0.2 and abs(r960.data["TCR_avg"] - 10.0) < 0.1 and abs(r960.data["TCR_trough"] - 1.24) < 0.02
    assert abs(r240.data["TCR_trough"] - 0.31) < 0.01
    assert r240.data["verdict"] == "abstain_metric_dependent"
    assert abs(r960.data["V_ss_L"] - 189) < 1


def test_exposure_power_widths():
    r = pharmacology.exposure_power(0.76)
    assert r.ok
    by_n = {row["n_per_arm"]: row for row in r.data["rows"]}
    assert abs(by_n[2]["fold"] - 14.1) < 0.2
    assert abs(by_n[4]["fold"] - 6.5) < 0.2


def test_design_sim_boin_boundaries_and_pcs_range():
    r = design_sim.operating_characteristics([0.10, 0.18, 0.30, 0.45, 0.58, 0.70], "3+3", n_sim=1000)
    assert r.ok, r.error
    b = r.data["boin_boundaries"]
    assert abs(b["escalate_le"] - 0.236) < 0.01 and abs(b["deescalate_ge"] - 0.359) < 0.01
    assert 10 <= r.data["PCS"] <= 50


def test_compare_sample_matched_shape():
    r = design_sim.compare_sample_matched([0.10, 0.18, 0.30, 0.45, 0.58, 0.70], n_sim=500)
    assert r.ok and "3+3" in r.data["rows"] and r.data["n_matched"] in (12, 15, 18)


@pytest.mark.network
def test_openfda_lumakras_live():
    r = pharmacology.openfda_label("LUMAKRAS")
    assert r.ok, r.error
    pk = r.data["pk"]
    assert pk.get("cl_f_L_per_hr") == 26.2 and pk.get("t_half_hr") == 5.0 and pk.get("protein_binding_pct") == 89.0
    assert r.data["nonlinear_pk_statement"] and r.data["exposure_response_unknown_statement"]
    assert r.data["has_liver_monitoring"]


@pytest.mark.network
def test_openfda_tagrisso_no_liver_monitoring_live():
    r = pharmacology.openfda_label("TAGRISSO")
    assert r.ok, r.error
    assert not r.data["has_liver_monitoring"]  # 오시머티닙 반례(같은 warhead, 간기능 모니터링 없음)


@pytest.mark.network
def test_chembl_sotorasib_live():
    r = pharmacology.chembl_potency("CHEMBL4535757", target_keyword="KRAS")
    assert r.ok, r.error
    assert r.data["target_matched"] and r.data["n_censored_excluded"] >= 3
    assert r.data["cell_based_median_nM"] == 30.0


@pytest.mark.network
def test_ctgov_kras_live():
    from app.tools import analog_trial
    r = analog_trial.search_analog_trials("KRAS G12C", page_size=5)
    assert r.ok, r.error
    assert r.data["total_count"] and r.data["total_count"] >= 100 and r.data["studies"][0]["nct_id"].startswith("NCT")


@pytest.mark.network
def test_open_targets_kras_live():
    from app.tools import open_targets
    r = open_targets.target_evidence("KRAS")
    assert r.ok, r.error
    assert r.data["ensembl_id"] == "ENSG00000133703"
    assert any((x["drug"] or "").upper() == "SOTORASIB" for x in r.data["known_drugs"])
