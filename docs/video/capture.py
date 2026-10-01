"""배포 Space·덱·카드 화면 캡처 — shots.json → shots/*.png, clips/*.webm

실행: py -3.14 docs/video/capture.py [--only id1,id2]
- 수치를 읽는 장면은 저장 결과(?demo=N&cached=1)에서 찍는다. 라이브는 record=true로 녹화만 한다.
- shot: "viewport"(1920x1080) | "tall"(본문 높이 전체, build.py의 scroll 화면용)
- 캡처는 device_scale_factor=2(3840 폭)로 찍어 확대해도 글자가 뭉개지지 않게 한다.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from playwright.async_api import Page, async_playwright

HERE = Path(__file__).resolve().parent
BASE = "https://haribear99-doseverdict.hf.space/"
W, H = 1920, 1080


async def ready(pg: Page) -> None:
    await pg.wait_for_selector('[data-testid="stMain"]', timeout=240000)
    # Streamlit 실행 중 표시가 사라질 때까지
    for _ in range(240):
        busy = await pg.locator('[data-testid="stStatusWidget"]').count()
        if not busy:
            break
        await pg.wait_for_timeout(500)
    await pg.wait_for_timeout(1500)


async def step(pg: Page, s: list) -> None:
    op, *arg = s
    if op == "tab":
        await pg.get_by_role("tab", name=arg[0], exact=True).first.click()
    elif op == "click_text":
        await pg.get_by_text(arg[0], exact=False).first.click()
    elif op == "click_button":
        await pg.get_by_role("button", name=arg[0]).first.click()
    elif op == "expand":  # expander 요약 줄 텍스트로 펼치기(이미 펼쳐져 있으면 그대로)
        loc = pg.locator("details summary", has_text=arg[0]).first
        det = loc.locator("xpath=..")
        if await det.get_attribute("open") is None:
            await loc.click()
    elif op == "collapse":
        loc = pg.locator("details summary", has_text=arg[0]).first
        det = loc.locator("xpath=..")
        if await det.get_attribute("open") is not None:
            await loc.click()
    elif op == "scroll_to":  # 해당 텍스트를 화면 위쪽(offset px)으로
        off = arg[1] if len(arg) > 1 else 120
        await pg.get_by_text(arg[0], exact=False).first.evaluate(
            "(el, off) => { const m = document.querySelector('[data-testid=stMain]');"
            " const r = el.getBoundingClientRect(); m.scrollBy(0, r.top - off); }", off)
    elif op == "scroll_y":
        await pg.evaluate("y => document.querySelector('[data-testid=stMain]').scrollTo(0, y)", arg[0])
    elif op == "wait":
        await pg.wait_for_timeout(arg[0])
    elif op == "ready":
        await ready(pg)
    elif op == "hide_sidebar":
        await pg.add_style_tag(content='[data-testid="stSidebar"]{display:none!important}')
    elif op == "eval":
        await pg.evaluate(arg[0])
    else:
        raise ValueError(op)
    await pg.wait_for_timeout(700)


async def shoot(b, spec: dict) -> None:
    sid = spec["id"]
    rec = spec.get("record")
    ctx_kw = dict(viewport={"width": W, "height": H}, device_scale_factor=1 if rec else spec.get("dsf", 2))
    if rec:
        (HERE / "clips").mkdir(exist_ok=True)
        ctx_kw.update(record_video_dir=str(HERE / "clips" / f"_{sid}"), record_video_size={"width": W, "height": H})
    ctx = await b.new_context(**ctx_kw)
    pg = await ctx.new_page()
    url = spec["url"]
    url = url if url.startswith(("http", "file:")) else BASE + url
    t0 = time.time()
    await pg.goto(url, timeout=240000)
    if spec.get("hide_sidebar_early"):
        await pg.add_style_tag(content='[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"]{display:none!important}')
    if spec.get("streamlit", True):
        await ready(pg)
    marks = {}
    for s in spec.get("steps", []):
        await step(pg, s)
        marks[str(s)] = round(time.time() - t0, 1)
    if rec:
        until = spec.get("until")
        if until:
            await pg.get_by_text(until, exact=False).first.wait_for(timeout=spec.get("max", 400) * 1000)
            marks["until"] = round(time.time() - t0, 1)
        for s in spec.get("after", []):
            await step(pg, s)
            marks[str(s)] = round(time.time() - t0, 1)
        await pg.wait_for_timeout(spec.get("tail", 3000))
        await ctx.close()
        vids = sorted((HERE / "clips" / f"_{sid}").glob("*.webm"), key=lambda p: p.stat().st_mtime)
        dst = HERE / "clips" / f"{sid}.webm"
        dst.unlink(missing_ok=True)
        vids[-1].rename(dst)
        (HERE / "clips" / f"{sid}.marks.json").write_text(json.dumps(marks, ensure_ascii=False, indent=1), encoding="utf-8")
        print(sid, "clip", marks)
        return
    out = HERE / "shots" / f"{sid}.png"
    out.parent.mkdir(exist_ok=True)
    if spec.get("shot", "viewport") == "tall":
        # Streamlit은 안쪽 컨테이너가 스크롤하므로 가장 긴 scrollHeight를 쓴다. 늘린 뒤 다시 재서 수렴시킨다
        for _ in range(3):
            h = await pg.evaluate("Math.max(...[...document.querySelectorAll('*')].map(e => e.scrollHeight))")
            await pg.set_viewport_size({"width": W, "height": int(min(h, 16000))})
            await pg.wait_for_timeout(1500)
        for s in spec.get("after_resize", []):
            await step(pg, s)
    if spec.get("element"):
        await pg.locator(spec["element"]).first.screenshot(path=str(out))
    else:
        await pg.screenshot(path=str(out))
    # 이름 붙인 텍스트의 위치(CSS px, 캡처 좌표)를 남겨 build.py가 강조 박스를 그리게 한다
    marks = {}
    ox = oy = 0
    if spec.get("element"):  # 요소 캡처는 요소 왼쪽 위를 원점으로
        eb = await pg.locator(spec["element"]).first.bounding_box()
        ox, oy = eb["x"], eb["y"]
    for name, text in spec.get("marks", {}).items():
        try:
            loc = pg.locator(text[4:]).first if text.startswith("css=") else pg.get_by_text(text, exact=False).first
            bb = await loc.bounding_box(timeout=3000)
            if bb:
                marks[name] = [round(bb["x"] - ox), round(bb["y"] - oy), round(bb["width"]), round(bb["height"])]
        except Exception as e:
            print(sid, "mark miss", name, repr(e)[:80])
    (HERE / "shots" / f"{sid}.marks.json").write_text(json.dumps(marks, ensure_ascii=False, indent=1), encoding="utf-8")
    print(sid, "png", out.name, len(marks), "marks")
    await ctx.close()


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", default=str(HERE / "shots.json"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    specs = json.loads(Path(a.specs).read_text(encoding="utf-8"))
    only = set(filter(None, a.only.split(",")))
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for spec in specs:
            if only and spec["id"] not in only:
                continue
            try:
                await shoot(b, spec)
            except Exception as e:  # 한 장면 실패가 전체를 막지 않게
                print(spec["id"], "FAIL", repr(e)[:300])
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
