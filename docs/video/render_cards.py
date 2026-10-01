"""cards/*.html → cards/png/*.png (3840x2160). 실행: py -3.14 docs/video/render_cards.py [이름...]"""
import asyncio, sys
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent


async def main(names):
    files = [HERE / "cards" / f"{n}.html" for n in names] if names else sorted((HERE / "cards").glob("*.html"))
    (HERE / "cards" / "png").mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        for f in files:
            await pg.goto(f.as_uri())
            await pg.evaluate("document.fonts.ready")
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(HERE / "cards" / "png" / f"{f.stem}.png"))
            print(f.stem)
        await b.close()

asyncio.run(main(sys.argv[1:]))
