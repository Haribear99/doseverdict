"""상세기술서 PDF 출력: docs/상세기술서.md → docs/상세기술서.pdf.

make-pdf(gstack)로 HTML을 만든 뒤 docs/report.css를 덧씌워 headless Chrome으로 인쇄한다(make-pdf에는 사용자 CSS 옵션이 없다).
출력 뒤 본문 글자 크기와 물결표 취소선을 검사한다 — 표 폭이 넘치면 Chrome이 문서 전체를 8~10pt로 축소한다(09-30 사례).

사용: python docs/render_report.py [--preview DIR]   (pymupdf 필요, Chrome 경로는 환경변수 CHROME, make-pdf 경로는 MAKE_PDF_BIN)
"""
import argparse
import collections
import os
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
MAKE_PDF = os.environ.get("MAKE_PDF_BIN", str(pathlib.Path.home() / ".claude/skills/gstack/make-pdf/dist/pdf.exe"))
SRC, OUT, CSS = HERE / "상세기술서.md", HERE / "상세기술서.pdf", HERE / "report.css"
COVER = HERE / "report_cover.html"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=pathlib.Path)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        html = pathlib.Path(tmp) / "report.html"
        subprocess.run([MAKE_PDF, "generate", "--to", "html", "--no-confidential", "--page-size", "a4", str(SRC), str(html)],
                       check=True, capture_output=True)
        page = html.read_text(encoding="utf-8")
        strike = page.count("<del>") + page.count("<s>")   # 이스케이프 안 한 물결표 범위(~)는 취소선이 된다
        # make-pdf의 화면용 <style>(@media screen) 뒤, </head> 바로 앞에 넣어 인쇄 규칙을 덮어쓴다
        page = page.replace("</head>", f"<style>\n{CSS.read_text(encoding='utf-8')}\n</style>\n</head>", 1)
        # 전면 표지(docs/report_cover.html)를 <body> 바로 뒤에 넣는다. 이미지 경로는 임시 폴더 밖이라 절대 URI로
        if COVER.exists():
            cover = COVER.read_text(encoding="utf-8").replace("{{FIGS}}", (HERE / "figs").as_uri())
            b = page.index("<body")
            b = page.index(">", b) + 1
            page = page[:b] + cover + page[b:]
        html.write_text(page, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=20000",
                        f"--print-to-pdf={OUT}", html.as_uri()], check=True, capture_output=True)

    import pymupdf
    doc = pymupdf.open(OUT)
    sizes: collections.Counter = collections.Counter()
    for pg in doc:
        for b in pg.get_text("dict")["blocks"]:
            for line in b.get("lines", []):
                for sp in line["spans"]:
                    sizes[round(sp["size"], 1)] += len(sp["text"].strip())
    body = sizes.most_common(1)[0][0]
    text = "".join(pg.get_text() for pg in doc)
    print(f"{OUT.name}: {doc.page_count}쪽, 본문 글자 크기 {body}pt(최다 빈도), 남은 ** {text.count('**')}개, 취소선 {strike}개")
    if strike:
        raise SystemExit(f"취소선 {strike}개 — md의 물결표 범위를 \~로 이스케이프할 것")
    if body < 11.5:
        raise SystemExit(f"본문이 {body}pt로 축소됐다 — 표 안의 긴 코드 이름이 폭을 넘는지 확인할 것")
    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        for i, pg in enumerate(doc):
            pg.get_pixmap(dpi=60).save(args.preview / f"p{i + 1:02d}.png")
        print(f"미리보기 {doc.page_count}장 → {args.preview}")


if __name__ == "__main__":
    main()
