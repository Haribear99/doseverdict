"""
Citation & Consistency Verifier — 주장·근거 쌍의 함의 판정.

규칙(제안서 2장): 검증자는 생성자(LLM)와 분리한다. 영문은 전용 NLI 모델, 한국어 근거는 결정론적 문자열 대조.
규범 강도 검사: 근거의 norm_strength가 civil_guide/draft_guidance인데 주장 술어가 '의무화·must·required'류면 기각.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

NLI_MODEL_EN = os.getenv("DV_NLI_MODEL", "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")  # 제안서 ID(-ling-wanli 없음)는 404
NLI_MODEL_MULTI = os.getenv("DV_NLI_MODEL_MULTI", "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")

_BINDING_PREDICATES = re.compile(r"(의무화|의무이다|강제|반드시\s*(해야|하여야)|\bmust\b|\bis required\b|\bare required\b|\bmandat(?:es|ory)\b|\bshall\b)", re.I)
_NON_BINDING = {"civil_guide", "draft_guidance", "reference"}


@dataclass
class NLIResult:
    label: Literal["entailment", "neutral", "contradiction"]
    scores: dict[str, float]
    method: str  # nli_en / nli_multi / string_match


@dataclass
class Verdict:
    status: Literal["verified", "rejected", "held"]
    reason: str
    nli: NLIResult | None = None


_ATTRIBUTION = re.compile(
    r"^\s*(?:(?:the\s+)?(?:FDA|EMA|MFDS|ICH|식약처|가이던스|guidance|guideline|label|labeling|document|regulator|agency)[^,:]{0,40}?"
    r"\b(?:states?|says?|notes?|indicates?|requires?|recommends?|provides?|instructs?|directs?|advises?|specifies|calls for|explains?)\s+(?:that\s+)?)", re.I)


def strip_attribution(claim: str) -> str:
    """'FDA guidance states that X' → 'X'. NLI는 귀속 프레임을 근거에서 찾지 못해 중립으로 판정하므로 명제만 남긴다(실측: 0.002 → 0.996)."""
    return _ATTRIBUTION.sub("", claim, count=1).strip() or claim


def _is_korean(text: str) -> bool:
    return sum("가" <= ch <= "힣" for ch in text) > max(5, 0.2 * len(text))


@lru_cache(maxsize=2)
def _pipeline(model_name: str):
    import torch
    from transformers import pipeline
    device = 0 if torch.cuda.is_available() and os.getenv("DV_NLI_DEVICE", "auto") != "cpu" else -1
    return pipeline("text-classification", model=model_name, device=device, top_k=None)


def nli(premise: str, hypothesis: str, multilingual: bool = False) -> NLIResult:
    """premise(근거 원문) → hypothesis(주장) 함의 판정. 라벨 순서는 모델 카드 기준 entailment/neutral/contradiction."""
    model_name = NLI_MODEL_MULTI if multilingual else NLI_MODEL_EN
    pipe = _pipeline(model_name)
    out = pipe({"text": premise[:1500], "text_pair": hypothesis[:500]}, truncation=True, max_length=512)
    rows = out[0] if isinstance(out[0], list) else out
    scores = {r["label"].lower(): float(r["score"]) for r in rows}
    label = max(scores, key=scores.get)
    return NLIResult(label=label, scores=scores, method="nli_multi" if multilingual else "nli_en")  # type: ignore[arg-type]


def string_support(evidence_quote: str, claim: str, min_overlap: float = 0.6) -> NLIResult:
    """한국어 근거: 주장의 핵심 토큰(2음절 이상 어절)이 근거 발췌에 얼마나 포함되는지로 판정한다."""
    toks = [t for t in re.findall(r"[가-힣]{2,}|[A-Za-z0-9.%]{2,}", claim)]
    if not toks:
        return NLIResult("neutral", {"overlap": 0.0}, "string_match")
    hit = sum(1 for t in toks if t in evidence_quote)
    ratio = hit / len(toks)
    label = "entailment" if ratio >= min_overlap else "neutral"
    return NLIResult(label, {"overlap": round(ratio, 3)}, "string_match")  # type: ignore[arg-type]


def verify_claim(claim: str, evidence_quote: str, norm_strength: str | None = None,
                 evidence_effective_date: str | None = None, superseded: bool = False,
                 entail_threshold: float = 0.7) -> Verdict:
    """
    1) 결정론적 검사 — 폐기 문서 인용 기각, 규범 강도 초과 술어 기각
    2) 함의 판정 — 영문 NLI / 한국어 문자열 대조 / 혼합은 다국어 NLI
    """
    if superseded:
        return Verdict("rejected", "폐기·개정된 문서 버전을 인용 — 최신 버전으로 교체 필요")
    if norm_strength in _NON_BINDING and _BINDING_PREDICATES.search(claim):
        return Verdict("rejected", f"근거의 규범 강도({norm_strength})가 주장의 술어(의무화/must)를 지탱하지 못함 — 술어를 '안내한다/권고한다'로 낮출 것")
    if _is_korean(evidence_quote) and _is_korean(claim):
        res = string_support(evidence_quote, claim)
        if res.label == "entailment":
            return Verdict("verified", f"문자열 대조 overlap={res.scores['overlap']}", res)
        return Verdict("held", f"한국어 근거 문자열 대조 미달(overlap={res.scores['overlap']}) — 원문 발췌 재확인 또는 기계번역 후 NLI", res)
    res = nli(evidence_quote, strip_attribution(claim), multilingual=_is_korean(evidence_quote) != _is_korean(claim))
    if res.label == "entailment" and res.scores["entailment"] >= entail_threshold:
        return Verdict("verified", f"NLI entailment={res.scores['entailment']:.2f}", res)
    if res.label == "contradiction":
        return Verdict("rejected", f"NLI contradiction={res.scores['contradiction']:.2f}", res)
    return Verdict("held", f"NLI 불충분 label={res.label} entail={res.scores.get('entailment', 0):.2f}", res)
