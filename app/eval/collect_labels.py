"""
평가 축 ③ — openFDA 항암 승인 라벨 수집 (라벨 PK·구조만 입력, 정답은 FDA 용량 최적화 PMR 부과 여부).

실행: .venv/Scripts/python.exe -m app.eval.collect_labels  →  app/eval/data/oncology_labels.jsonl, oncology_labels_summary.csv
정답(PMR 여부)은 승인서한에서 사람이 채운다(컬럼 pmr_dose_optimization: 공란). 이 스크립트는 팀 판단을 개입시키지 않는다.
"""
from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "data"
UA = {"User-Agent": "DoseVerdict-Eval/0.1 (academic competition prototype)"}
BASE = "https://api.fda.gov/drug/label.json"

# 항암 경구 표적치료제가 몰리는 EPC(established pharmacologic class) 검색어
CLASS_QUERIES = [
    'openfda.pharm_class_epc:"Kinase Inhibitor"',
    'openfda.pharm_class_epc:"Poly(ADP-Ribose) Polymerase Inhibitor"',
    'openfda.pharm_class_epc:"Cyclin-dependent Kinase Inhibitor"',
    'openfda.pharm_class_epc:"Hedgehog Pathway Inhibitor"',
    'openfda.pharm_class_epc:"Bcl-2 Inhibitor"',
    'openfda.pharm_class_epc:"Histone Deacetylase Inhibitor"',
    'openfda.pharm_class_epc:"Proteasome Inhibitor"',
    'openfda.pharm_class_epc:"Isocitrate Dehydrogenase-1 Inhibitor"',
    'openfda.pharm_class_epc:"Isocitrate Dehydrogenase-2 Inhibitor"',
    'openfda.pharm_class_epc:"Menin Inhibitor"',
    'openfda.pharm_class_epc:"KRAS G12C Inhibitor"',
]
_PK = {
    "cl_f_L_per_hr": r"apparent (?:oral )?clearance[^.]*?(?:is|was|of)\s+(?:approximately\s+)?([\d.]+)\s*L/h",
    "t_half_hr": r"(?:terminal |elimination )?half-life[^.]*?(?:is|was|of)\s+(?:approximately\s+)?([\d.]+)\s*(?:hours?|h\b)",
    "protein_binding_pct": r"(?:plasma )?protein binding[^.]*?(?:is|was|of)\s+(?:approximately\s+)?([\d.]+)\s*%",
    "vd_L": r"volume of distribution[^.]*?(?:is|was|of)\s+(?:approximately\s+)?([\d,]+)\s*L\b",
}
_NONLINEAR = re.compile(r"(non-?linear|less than (?:dose[- ])?proportional|greater than dose[- ]proportional|saturable)[^.]*\.", re.I)
_ER_UNKNOWN = re.compile(r"exposure[- ]response relationships?[^.]*(unknown|not (?:been )?(?:fully )?(?:characterized|established))[^.]*\.", re.I)


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_labels(query: str, limit: int = 100, key: str | None = None) -> list[dict]:
    out, skip = [], 0
    while True:
        q = urllib.parse.urlencode({"search": f"({query}) AND _exists_:clinical_pharmacology", "limit": limit, "skip": skip} | ({"api_key": key} if key else {}))
        try:
            data = _get(f"{BASE}?{q}")
        except Exception as e:  # noqa: BLE001 — 404 = 결과 없음
            if "404" in str(e):
                break
            raise
        out.extend(data.get("results", []))
        total = data.get("meta", {}).get("results", {}).get("total", 0)
        skip += limit
        if skip >= total or skip >= 1000:
            break
        time.sleep(0.3)
    return out


def summarize(label: dict) -> dict:
    of = label.get("openfda", {})
    text = " ".join(label.get("clinical_pharmacology", []))
    pk = {}
    for k, pat in _PK.items():
        m = re.search(pat, text, flags=re.I)
        if m:
            pk[k] = float(m.group(1).replace(",", ""))
    nl = _NONLINEAR.search(text)
    er = _ER_UNKNOWN.search(text)
    return {
        "set_id": label.get("set_id"), "effective_time": label.get("effective_time"),
        "brand_name": (of.get("brand_name") or [None])[0], "generic_name": (of.get("generic_name") or [None])[0],
        "pharm_class_epc": of.get("pharm_class_epc"), "route": of.get("route"), "unii": (of.get("unii") or [None])[0],
        "pk": pk, "pk_fields_found": len(pk),
        "nonlinear_pk_statement": nl.group(0)[:300] if nl else None,
        "exposure_response_unknown": er.group(0)[:300] if er else None,
        "pmr_dose_optimization": None,          # 정답: 승인서한 기준, 사람이 채움
        "approval_year": None,                  # Drugs@FDA로 보강 예정
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    key = os.getenv("OPENFDA_API_KEY")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen: dict[str, dict] = {}
    for q in CLASS_QUERIES:
        labels = fetch_labels(q, key=key)
        for lb in labels:
            s = summarize(lb)
            g = (s["generic_name"] or "").upper()
            if not g or "KIT" in g and len(g) < 4:
                continue
            # 같은 성분의 라벨이 여러 제조사/버전으로 있으면 최신 effective_time만 유지
            if g not in seen or (s["effective_time"] or "") > (seen[g]["effective_time"] or ""):
                seen[g] = s
        print(f"{q:70s} → {len(labels):3d} labels, cumulative generics {len(seen)}")
        time.sleep(0.5)
    rows = sorted(seen.values(), key=lambda r: r["generic_name"] or "")
    with (OUT_DIR / "oncology_labels.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (OUT_DIR / "oncology_labels_summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["generic_name", "brand_name", "effective_time", "pk_fields_found", "cl_f_L_per_hr", "t_half_hr", "protein_binding_pct", "nonlinear", "er_unknown", "pmr_dose_optimization"])
        for r in rows:
            w.writerow([r["generic_name"], r["brand_name"], r["effective_time"], r["pk_fields_found"], r["pk"].get("cl_f_L_per_hr"), r["pk"].get("t_half_hr"),
                        r["pk"].get("protein_binding_pct"), bool(r["nonlinear_pk_statement"]), bool(r["exposure_response_unknown"]), ""])
    n_pk = sum(1 for r in rows if r["pk_fields_found"] >= 2)
    print(f"\n총 {len(rows)}개 성분, PK 파라미터 2개 이상 추출 {n_pk}개, 비선형 PK 진술 {sum(1 for r in rows if r['nonlinear_pk_statement'])}개, E-R 미상 {sum(1 for r in rows if r['exposure_response_unknown'])}개")
    print(f"→ {OUT_DIR / 'oncology_labels.jsonl'}")


if __name__ == "__main__":
    main()
