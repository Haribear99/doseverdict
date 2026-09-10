"""
규제 코퍼스 인덱스 — BM25(어휘) + bge-m3 dense(의미)의 RRF 하이브리드 검색.

빌드(로컬 GPU, 1회):  .venv/Scripts/python.exe -m app.corpus.index build
검색(배포본 CPU):     search("dose optimization randomized comparison", k=5, jurisdiction="US")

파일 레이아웃 (app/corpus/index/):
  clauses.jsonl      청크 메타+본문 (Clause dataclass)
  dense.npy          float16 [n_chunks, 1024] 정규화 임베딩 (bge-m3)
  bm25.pkl           rank_bm25 인덱스 (토큰화: 소문자 영숫자 + 한글 음절 bigram)
  build_meta.json    모델명·매니페스트 ID·빌드 시각·청크 수
"""
from __future__ import annotations

import json
import pickle
import re
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from app.corpus.chunker import Clause, load_pages, split_clauses
from app.corpus.manifest import DOCS, INDEX_DIR, MANIFEST_ID, RAW_DIR

EMBED_MODEL = "BAAI/bge-m3"
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-.'][a-z0-9]+)*|[가-힣]+")


def tokenize(text: str) -> list[str]:
    """영문은 소문자 단어, 한글은 음절 bigram(형태소 분석기 없이 부분 일치 확보)."""
    out: list[str] = []
    for tok in _TOKEN_RE.findall(text.lower()):
        if "가" <= tok[0] <= "힣":
            out.extend(tok[i:i + 2] for i in range(max(1, len(tok) - 1)))
        else:
            out.append(tok)
    return out


# ----------------------------------------------------------------- build
def build_clauses() -> list[Clause]:
    clauses: list[Clause] = []
    for d in DOCS:
        if not d.local_file or not d.verified_url:
            continue
        pages = load_pages(RAW_DIR / d.local_file)
        clauses.extend(split_clauses(d, pages))
    return clauses


def _embed(texts: list[str], device: str | None = None, batch_size: int = 16) -> np.ndarray:
    from sentence_transformers import SentenceTransformer  # 지연 import (배포본 CPU에서도 동작)
    model = SentenceTransformer(EMBED_MODEL, device=device)
    if device and device.startswith("cuda"):
        model.half()
    vecs = model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True, max_length=1024)
    return np.asarray(vecs, dtype=np.float16)


def build(device: str | None = None) -> dict[str, Any]:
    from rank_bm25 import BM25Okapi
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    clauses = build_clauses()
    with (INDEX_DIR / "clauses.jsonl").open("w", encoding="utf-8") as f:
        for c in clauses:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
    texts = [f"{c.heading}\n{c.text}" for c in clauses]
    bm25 = BM25Okapi([tokenize(t) for t in texts])
    (INDEX_DIR / "bm25.pkl").write_bytes(pickle.dumps(bm25))
    if device is None:
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:  # noqa: BLE001
            device = "cpu"
    dense = _embed(texts, device=device)
    np.save(INDEX_DIR / "dense.npy", dense)
    meta = {"embed_model": EMBED_MODEL, "manifest_id": MANIFEST_ID, "built_at": datetime.now(timezone.utc).isoformat(),
            "n_chunks": len(clauses), "device": device, "dim": int(dense.shape[1])}
    (INDEX_DIR / "build_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


# ----------------------------------------------------------------- search
class CorpusIndex:
    _instance: "CorpusIndex | None" = None

    def __init__(self, load_dense: bool = True):
        self.clauses: list[dict[str, Any]] = [json.loads(l) for l in (INDEX_DIR / "clauses.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        self.bm25 = pickle.loads((INDEX_DIR / "bm25.pkl").read_bytes())
        self.meta = json.loads((INDEX_DIR / "build_meta.json").read_text(encoding="utf-8"))
        self.dense = np.load(INDEX_DIR / "dense.npy").astype(np.float32) if load_dense else None
        self._encoder = None

    @classmethod
    def get(cls) -> "CorpusIndex":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _encode_query(self, q: str) -> np.ndarray:
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(EMBED_MODEL, device="cpu")
        return np.asarray(self._encoder.encode([q], normalize_embeddings=True)[0], dtype=np.float32)

    def search(self, query: str, k: int = 5, jurisdiction: str | None = None, doc_ids: list[str] | None = None,
               rrf_k: int = 60, use_dense: bool = True) -> list[dict[str, Any]]:
        """BM25와 dense 순위를 RRF로 융합. jurisdiction('US'|'KR'|'common')·doc_ids로 사전 필터(국가별 검색 분리 규칙)."""
        allowed = [i for i, c in enumerate(self.clauses)
                   if (jurisdiction is None or c["jurisdiction"] in (jurisdiction, "common"))
                   and (doc_ids is None or c["doc_id"] in doc_ids)]
        if not allowed:
            return []
        bm = np.asarray(self.bm25.get_scores(tokenize(query)), dtype=np.float32)
        bm_rank = sorted(allowed, key=lambda i: -bm[i])
        fused: dict[int, float] = {}
        for r, i in enumerate(bm_rank[:50]):
            fused[i] = fused.get(i, 0.0) + 1.0 / (rrf_k + r + 1)
        if use_dense and self.dense is not None:
            qv = self._encode_query(query)
            sims = self.dense @ qv
            de_rank = sorted(allowed, key=lambda i: -sims[i])
            for r, i in enumerate(de_rank[:50]):
                fused[i] = fused.get(i, 0.0) + 1.0 / (rrf_k + r + 1)
        top = sorted(fused.items(), key=lambda kv: -kv[1])[:k]
        out = []
        for i, score in top:
            c = dict(self.clauses[i])
            c["score_rrf"] = round(score, 5)
            c["score_bm25"] = round(float(bm[i]), 3)
            out.append(c)
        return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        print(json.dumps(build(), ensure_ascii=False, indent=2))
    else:
        idx = CorpusIndex.get()
        for hit in idx.search(" ".join(sys.argv[1:]) or "dose comparison randomized", k=5):
            print(hit["score_rrf"], hit["doc_id"], hit["heading"][:50], "|", hit["text"][:120].replace("\n", " "))
