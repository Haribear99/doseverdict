"""발표자료 PDF 출력: docs/slides/deck.html → docs/slides/deck.pdf (headless Chrome, 1920×1080 한 장당 1쪽).

사용: python docs/slides/render.py [--preview DIR]
  --preview DIR  PDF 각 쪽을 PNG로 DIR에 저장(눈 검수용, pymupdf 필요)
Chrome 경로는 환경변수 CHROME으로 바꿀 수 있다.
"""
import argparse
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=pathlib.Path)
    args = ap.parse_args()

    pdf = HERE / "deck.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=15000", f"--print-to-pdf={pdf}", (HERE / "deck.html").as_uri()],
                   check=True, capture_output=True)

    import pymupdf
    doc = pymupdf.open(pdf)
    print(f"{pdf.name}: {doc.page_count}쪽, {doc[0].rect.width:.0f}×{doc[0].rect.height:.0f}pt")
    if args.preview:
        args.preview.mkdir(parents=True, exist_ok=True)
        for i, page in enumerate(doc):
            page.get_pixmap(dpi=72).save(args.preview / f"p{i + 1:02d}.png")
        print(f"미리보기 {doc.page_count}장 → {args.preview}")


if __name__ == "__main__":
    main()
