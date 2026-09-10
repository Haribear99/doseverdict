"""
절(clause) 단위 청킹 — 규제 문서는 문서 단위가 아니라 절 단위로 정확해야 한다(제안서 3장).

전략: PDF → 페이지 텍스트 → 절 번호/제목 패턴(예: "III. DOSAGE OPTIMIZATION", "A. ...", "1.2 ...", "제3장", "3.1")으로
분할 → 각 청크에 doc_id·section_path·page·norm_strength를 붙인다. 문장 단위 검색을 위해 긴 절은 슬라이딩 윈도우로 나눈다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from app.corpus.manifest import CorpusDoc

_HEADING_PATTERNS = [
    re.compile(r"^\s*(?P<num>[IVX]{1,5})\.\s+(?P<title>[A-Z][A-Z \-,/&()]{3,})\s*$"),          # III. DOSAGE OPTIMIZATION
    re.compile(r"^\s*(?P<num>[A-Z])\.\s+(?P<title>[A-Z][^\n]{3,80})\s*$"),                        # A. Background
    re.compile(r"^\s*(?P<num>\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+(?P<title>[A-Z가-힣][^\n]{2,80})\s*$"),  # 1.2 Title / 3.1 제목
    re.compile(r"^\s*(?P<num>제\s?\d+\s?[장절조])\s*(?P<title>[^\n]{0,60})\s*$"),                    # 제3장 ...
    re.compile(r"^\s*(?P<num>Annex\s+\d+|ANNEX\s+\d+)\s*(?P<title>[^\n]{0,80})\s*$"),
]
_SHOULD = re.compile(
    r"(\b(should|must|shall|recommend(?:s|ed)?|is required|are required|is expected|are expected)\b"
    r"|필요하다|필요가 있다|권고한다|권고된다|권장한다|권장된다|바람직하다|하여야 한다|해야 한다|고려하여야|고려해야|요구된다|제출하여야|확보하여야)",
    re.I,
)
_MONTHS = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b", re.I)
_TRAILING_LINENO = re.compile(r"\s+\d{1,4}\s*$")  # FDA 초안 PDF의 행번호가 제목 끝에 붙는 경우


def _clean_heading(num: str, title: str) -> tuple[str, str] | None:
    """행번호·날짜·목차·각주를 제목으로 오인한 경우를 걸러낸다. None이면 제목이 아니다."""
    title = _TRAILING_LINENO.sub("", title).strip()
    if "····" in title or "……" in title:            # 목차 점선
        return None
    if _MONTHS.search(f"{num} {title}") or re.fullmatch(r"\d{4}", title):
        return None                                   # "27 April 1995"
    if title.lower().startswith("ibid") or title.endswith("."):
        return None                                   # 각주·본문 문장
    if num.isdigit() and not (title.isupper() or len(title.split()) <= 8):
        return None                                   # 행번호 + 본문 문장
    if len(title) < 3:
        return None
    return num, title


@dataclass
class Clause:
    chunk_id: str
    doc_id: str
    section_path: str
    heading: str
    page_start: int
    page_end: int
    text: str
    norm_strength: str
    jurisdiction: str
    effective_date: str
    normative_sentences: list[str] = field(default_factory=list)


def _pages_from_pdf(path: Path) -> list[str]:
    from pypdf import PdfReader  # 지연 import — 배포본에서 선택 의존성
    reader = PdfReader(str(path))
    return [(p.extract_text() or "") for p in reader.pages]


def _pages_from_text(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return text.split("\f") if "\f" in text else [text]


def load_pages(path: Path) -> list[str]:
    if path.suffix.lower() == ".pdf":
        return _pages_from_pdf(path)
    return _pages_from_text(path)


def _is_heading(line: str):
    for pat in _HEADING_PATTERNS:
        m = pat.match(line)
        if m:
            return _clean_heading(m.group("num").strip(), (m.group("title") or "").strip())
    return None


def split_clauses(doc: CorpusDoc, pages: list[str], max_chars: int = 1800, overlap: int = 200) -> list[Clause]:
    clauses: list[Clause] = []
    cur_lines: list[str] = []
    cur_head = ("0", "PREAMBLE")
    cur_page_start = 1
    stack: list[str] = []

    def flush(page_end: int):
        text = "\n".join(l for l in cur_lines if l.strip()).strip()
        if len(text) < 40:
            return
        section_path = " > ".join(stack) if stack else cur_head[0]
        # 슬라이딩 윈도우
        start, k = 0, 0
        while start < len(text):
            piece = text[start: start + max_chars]
            norm = [s.strip() for s in re.split(r"(?<=[.。])\s+", piece) if _SHOULD.search(s)]
            clauses.append(Clause(
                chunk_id=f"{doc.doc_id}#{len(clauses):04d}", doc_id=doc.doc_id, section_path=section_path,
                heading=f"{cur_head[0]} {cur_head[1]}".strip(), page_start=cur_page_start, page_end=page_end, text=piece,
                norm_strength=doc.norm_strength.value, jurisdiction=doc.jurisdiction.value, effective_date=doc.effective_date,
                normative_sentences=norm[:12],
            ))
            if start + max_chars >= len(text):
                break
            start += max_chars - overlap
            k += 1

    for pno, page in enumerate(pages, start=1):
        for line in page.splitlines():
            h = _is_heading(line)
            if h:
                flush(pno)
                cur_lines = []
                cur_head = h
                cur_page_start = pno
                depth = h[0].count(".") if re.match(r"\d", h[0]) else (0 if re.match(r"[IVX]+$", h[0]) else 1)
                stack = stack[:depth] + [f"{h[0]} {h[1]}".strip()]
            else:
                cur_lines.append(line)
    flush(len(pages))
    return clauses
