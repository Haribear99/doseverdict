"""
규제 코퍼스 매니페스트 — 문서의 기관·버전·발효일·관할·규범 강도를 메타데이터로 고정한다.

완료 기준(제안서 3장): 코퍼스 크기가 아니라 버전·발효일·규범 강도 메타데이터의 정확성.
URL은 리서치 세션 D의 확인 결과로 채운다. 확인되지 않은 문서는 `verified_url=False`로 두고 검색 대상에서 제외한다.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from app.schema.trial_schema import Applicability, NormStrength

CORPUS_DIR = Path(__file__).resolve().parent
RAW_DIR = CORPUS_DIR / "raw"
INDEX_DIR = CORPUS_DIR / "index"
MANIFEST_ID = "MANIFEST-2026-09-11"


@dataclass
class CorpusDoc:
    doc_id: str
    authority: str                     # FDA / ICH / MFDS / CTTI
    title: str
    version_label: str                 # "Final Aug 2024" / "Draft Jan 2025" / "Step 4 2025-01-06"
    effective_date: str                # ISO
    jurisdiction: Applicability
    norm_strength: NormStrength
    language: str                      # en / ko
    url: str = ""
    verified_url: bool = False
    local_file: str = ""               # raw/ 아래 파일명
    docket_or_number: str = ""
    superseded_by: str | None = None   # 폐기·개정된 문서면 후속 doc_id (버전 충돌 경고용)
    notes: str = ""
    tags: list[str] = field(default_factory=list)


# 초기 7문서 + 보조 2문서. URL은 리서치 D 확인 후 채운다(verified_url=True로 전환).
DOCS: list[CorpusDoc] = [
    CorpusDoc("FDA-DOSE-OPT-2024", "FDA",
              "Optimizing the Dosage of Human Prescription Drugs and Biological Products for the Treatment of Oncologic Diseases",
              "Final guidance, Aug 2024", "2024-08-09", Applicability.US, NormStrength.final_guidance, "en",
              docket_or_number="FDA-2022-D-2827", tags=["dose_optimization", "oncology", "project_optimus"],
              notes="FIH 시작용량은 적용 제외. 89 FR 65366."),
    CorpusDoc("FDA-DOSE-OPT-2023-DRAFT", "FDA",
              "Optimizing the Dosage of Human Prescription Drugs and Biological Products for the Treatment of Oncologic Diseases (Draft)",
              "Draft guidance, Jan 2023", "2023-01-13", Applicability.US, NormStrength.draft_guidance, "en",
              docket_or_number="FDA-2022-D-2827", superseded_by="FDA-DOSE-OPT-2024", tags=["dose_optimization"],
              notes="폐기된 초안 — 최신인 것처럼 제시되면 버전 충돌 경고를 내야 하는 적대 테스트 대상."),
    CorpusDoc("FDA-AI-CREDIBILITY-2025-DRAFT", "FDA",
              "Considerations for the Use of Artificial Intelligence to Support Regulatory Decision-Making for Drug and Biological Products",
              "Draft guidance, Jan 2025", "2025-01-07", Applicability.US, NormStrength.draft_guidance, "en",
              tags=["ai", "context_of_use", "credibility"], notes="본 시스템 자신에 대한 규제 문서. 7단계 credibility 평가."),
    CorpusDoc("FDA-EXPANSION-COHORTS-2022", "FDA",
              "Expansion Cohorts: Use in First-in-Human Clinical Trials to Expedite Development of Oncology Drugs and Biologics",
              "Final guidance, Mar 2022", "2022-03-01", Applicability.US, NormStrength.final_guidance, "en",
              tags=["expansion_cohort", "oncology"]),
    CorpusDoc("ICH-E6R3-2025", "ICH", "ICH E6(R3) Good Clinical Practice — Principles and Annex 1",
              "Step 4, 2025-01-06", "2025-01-06", Applicability.common, NormStrength.final_guidance, "en",
              tags=["gcp", "quality_by_design"], notes="EU 적용 2025-07-23, FDA 채택 2025-09. 국내 반영 진행 중 → 전환기 gap."),
    CorpusDoc("ICH-E4-1994", "ICH", "ICH E4 Dose-Response Information to Support Drug Registration",
              "Step 4, 1994-03-10", "1994-03-10", Applicability.common, NormStrength.final_guidance, "en",
              tags=["dose_response"]),
    CorpusDoc("MFDS-1443-01-2025", "MFDS", "항암제 임상시험 중 용량 최적화 전략 가이드라인 (민원인 안내서)",
              "안내서-1443-01, 2025-08-29", "2025-08-29", Applicability.KR, NormStrength.civil_guide, "ko",
              docket_or_number="안내서-1443-01",
              tags=["dose_optimization", "oncology"], notes="민원인 안내서 = 법적 구속력 없음. '의무화' 술어 금지."),
    CorpusDoc("MFDS-EXPANSION-COHORT-2025", "MFDS", "용량 확장 코호트 설계 시 고려사항 (민원인 안내서)",
              "2025", "2025-08-29", Applicability.KR, NormStrength.civil_guide, "ko", tags=["expansion_cohort"]),
    CorpusDoc("CTTI-QBD", "CTTI", "CTTI Quality by Design Recommendations / Critical to Quality Factors Principles Document",
              "2015 (rev.)", "2015-05-01", Applicability.common, NormStrength.reference, "en",
              tags=["ctq", "quality_by_design", "burden"]),
]


def write_manifest(path: Path | None = None) -> Path:
    path = path or (CORPUS_DIR / "manifest.json")
    payload = {"manifest_id": MANIFEST_ID, "docs": [asdict(d) | {"jurisdiction": d.jurisdiction.value, "norm_strength": d.norm_strength.value} for d in DOCS]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def by_id(doc_id: str) -> CorpusDoc:
    for d in DOCS:
        if d.doc_id == doc_id:
            return d
    raise KeyError(doc_id)
