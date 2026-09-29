"""후향 검증 시점 고정: 라벨 차단·CT.gov 컷오프·승인약 목록 생략 (네트워크 없음)."""
from app.tools import analog_trial, pharmacology


def test_label_blinded_is_404(monkeypatch):
    monkeypatch.setenv("DV_BLIND_LABEL", "1")
    called = []
    monkeypatch.setattr(pharmacology, "_openfda_label_raw", lambda *a, **k: called.append(1))
    r = pharmacology.openfda_label(generic="SOTORASIB")
    assert not r.ok and "404" in r.error and not called   # 네트워크 호출 없이 '라벨 없음' 경로


def test_ctgov_asof_filter(monkeypatch):
    monkeypatch.setenv("DV_ASOF_DATE", "2021-05-28")
    seen = {}

    def fake_get(url, timeout=40):
        seen["url"] = url
        mk = lambda nct, d: {"protocolSection": {"identificationModule": {"nctId": nct}, "statusModule": {"startDateStruct": {"date": d}}}}
        return {"totalCount": 3, "studies": [mk("NCT1", "2018-08-27"), mk("NCT2", "2022-02"), mk("NCT3", None)]}

    monkeypatch.setattr(analog_trial, "_get", fake_get)
    r = analog_trial.search_analog_trials("KRAS G12C")
    assert r.ok and [s["nct_id"] for s in r.data["studies"]] == ["NCT1"]
    assert "RANGE%5BMIN%2C+2021-05-28%5D" in seen["url"]


def test_no_asof_by_default(monkeypatch):
    monkeypatch.delenv("DV_ASOF_DATE", raising=False)
    monkeypatch.delenv("DV_BLIND_LABEL", raising=False)
    from app.tools import asof_date, label_blinded
    assert asof_date() is None and not label_blinded()
