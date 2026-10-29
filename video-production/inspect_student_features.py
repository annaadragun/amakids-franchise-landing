import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def labels(text: str, limit=120):
    values = [" ".join(line.split()) for line in text.splitlines()]
    return [value for value in values if value][:limit]


async def close_overlays(page):
    await page.keyboard.press("Escape")
    candidates = page.locator(
        '[class*="modal"] [class*="close"], [class*="popup"] [class*="close"], button[aria-label="Close"]'
    )
    for i in range(await candidates.count()):
        item = candidates.nth(i)
        if await item.is_visible():
            try:
                await item.click(timeout=1_500)
            except Exception:
                pass
    await page.wait_for_timeout(700)


async def capture(page, name):
    await page.wait_for_timeout(4_000)
    await close_overlays(page)
    await page.screenshot(path=str(RAW / f"feature-{name}.png"), full_page=False)
    print(name, "path:", urlsplit(page.url).path)
    print(name, "labels:", labels(await page.locator("body").inner_text()))


async def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    for raw_line in (ROOT / "amakids-local" / ".env.local").read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("PLATFORM_URL="):
            os.environ["PLATFORM_URL"] = raw_line.split("=", 1)[1].strip().strip("\"").strip("'")
    parts = urlsplit(os.environ["PLATFORM_URL"])
    origin = f"{parts.scheme}://{parts.netloc}"
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()

        await page.goto(origin + "/apps/student/", wait_until="domcontentloaded", timeout=90_000)
        await capture(page, "home")
        links = await page.locator("a:visible").evaluate_all(
            "els => els.map(a => ({text:(a.innerText||'').trim().replace(/\\s+/g,' '), href:a.href}))"
        )
        keep = ("league", "medal", "arena", "english", "challenge", "history")
        print(
            "Feature links:",
            [{"text": x["text"], "path": urlsplit(x["href"]).path} for x in links if any(k in x["text"].lower() for k in keep)],
        )
        for needle in ("English", "Challenge"):
            loc = page.get_by_text(needle, exact=True)
            if await loc.count():
                print(needle, "container:", await loc.first.evaluate("e => e.parentElement.parentElement.outerHTML.slice(0, 4000)"))

        for text, name in (("AMAkids League", "league"), ("Medals", "medals"), ("Arena", "arena")):
            await page.goto(origin + "/apps/student/", wait_until="domcontentloaded", timeout=90_000)
            await page.wait_for_timeout(3_000)
            await close_overlays(page)
            item = page.get_by_text(text, exact=True)
            if await item.count():
                await item.first.click()
                await capture(page, name)

        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
