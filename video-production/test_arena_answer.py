import asyncio
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".video-browser" / "state.json"


def base_url():
    for line in (ROOT / "amakids-local" / ".env.local").read_text(encoding="utf-8").splitlines():
        if line.startswith("PLATFORM_URL="):
            parsed = urlsplit(line.split("=", 1)[1].strip().strip("\"").strip("'"))
            return f"{parsed.scheme}://{parsed.netloc}"
    raise RuntimeError("Missing URL")


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(STATE), viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        await page.goto(base_url() + "/apps/arena/game/ma-rocket", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)
        await page.get_by_text("Play together", exact=True).click()
        await page.locator('input[placeholder="Player 2"]').fill("Mia")
        await page.get_by_text("Start!", exact=True).click()
        await page.wait_for_timeout(6_000)
        player = page.get_by_text("Test", exact=True)
        print(
            await player.evaluate(
                "e => { let a=e, out=[]; for(let i=0;i<8&&a;i++,a=a.parentElement){let r=a.getBoundingClientRect();out.push({i,c:a.className,t:(a.innerText||'').trim().slice(0,600),x:r.x,y:r.y,w:r.width,h:r.height})} return out }"
            )
        )
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
