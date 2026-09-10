"""코퍼스 청커·토크나이저·검증기 결정론 규칙 테스트(모델 다운로드 없음)."""
from app.corpus.chunker import _clean_heading, _is_heading, split_clauses
from app.corpus.index import tokenize
from app.corpus.manifest import DOCS, RAW_DIR, by_id
from app.verify.nli import string_support, verify_claim


def test_heading_filters():
    assert _is_heading("III. DOSAGE OPTIMIZATION RECOMMENDATIONS") == ("III", "DOSAGE OPTIMIZATION RECOMMENDATIONS")
    assert _is_heading("I. INTRODUCTION 11") == ("I", "INTRODUCTION")          # 초안 행번호 제거
    assert _is_heading("27 April 1995") is None                                    # 날짜
    assert _is_heading("9 Ibid.") is None                                          # 각주
    assert _is_heading("17 The terms fit for use and fit for purpose are sometimes used interchangeably") is None
    assert _is_heading("3.2 다양한 용량을 비교하기 위한 임상시험 설계 ····················") is None  # 목차
    assert _is_heading("3.2 다양한 용량을 비교하기 위한 임상시험 설계") == ("3.2", "다양한 용량을 비교하기 위한 임상시험 설계")
    assert _clean_heading("A", "Definition") == ("A", "Definition")


def test_tokenize_mixed():
    toks = tokenize("Dose optimization 용량 최적화 RP2D")
    assert "dose" in toks and "rp2d" in toks and "용량" in toks and "최적" in toks and "적화" in toks


def test_mfds_pdf_clauses_and_korean_normative():
    d = by_id("MFDS-1443-01-2025")
    from app.corpus.chunker import load_pages
    cl = split_clauses(d, load_pages(RAW_DIR / d.local_file))
    assert len(cl) >= 8
    assert any("2025. 8. 29." in c.heading or "2025. 8. 29." in c.text for c in cl)   # 제정일 명시
    assert sum(len(c.normative_sentences) for c in cl) >= 20
    assert all(c.norm_strength == "civil_guide" and c.jurisdiction == "KR" for c in cl)


def test_all_verified_docs_chunk():
    from app.corpus.chunker import load_pages
    n = 0
    for d in DOCS:
        if d.local_file:
            n += len(split_clauses(d, load_pages(RAW_DIR / d.local_file)))
    assert 300 <= n <= 600


def test_verifier_norm_strength_rule():
    v = verify_claim("식약처도 동일한 용량 비교를 의무화하고 있다", "식약처는 용량 최적화 전략을 안내한다", norm_strength="civil_guide")
    assert v.status == "rejected" and "규범 강도" in v.reason
    v2 = verify_claim("식약처는 안내서-1443-01로 용량 최적화 전략을 안내하고 있다", "안내서-1443-01 항암제 임상시험 중 용량 최적화 전략 가이드라인 … 용량 최적화 전략을 안내하고 있다", norm_strength="civil_guide")
    assert v2.status == "verified"
    assert verify_claim("anything", "anything", superseded=True).status == "rejected"


def test_string_support_overlap():
    r = string_support("두 개 이상의 용량을 무작위 배정하여 비교", "두 개 이상의 용량을 무작위 배정하여 비교한다")
    assert r.label == "entailment" and r.scores["overlap"] >= 0.6


def test_strip_attribution():
    from app.verify.nli import strip_attribution
    assert strip_attribution("FDA guidance states that the trial does not need to be powered.") == "the trial does not need to be powered."
    assert strip_attribution("The label indicates exposure is similar across doses.") == "exposure is similar across doses."
    assert strip_attribution("Exposure is similar across doses.") == "Exposure is similar across doses."
