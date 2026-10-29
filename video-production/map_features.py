import asyncio
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def labels(text: str, limit=140):
    cleaned = [" ".join(line.split()) for line in text.splitlines()]
    return [line for line in cleaned if line][:limit]


async def close_overlays(page):
    for selector in (
        '[class*="modal"] [class*="close"]',
        '[class*="popup"] [class*="close"]',
        'button[aria-label="Close"]',
    ):
        candidates = page.locator(selector)
        for index in range(await candidates.count()):
            candidate = candidates.nth(index)
            if await candidate.is_visible():
                try:
                    await candidate.click(timeout=1_500)
                    await page.wait_for_timeout(500)
                except Exception:
                    pass
    await page.keyboard.press("Escape")


async def inspect(page, url, filename):
    await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(6_000)
    await close_overlays(page)
    await page.screenshot(path=str(RAW / filename), full_page=False)
    print(filename, "path:", urlsplit(page.url).path)
    print(filename, "labels:", labels(await page.locator("body").inner_text()))


async def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    origin = state["origins"][0]["origin"]
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        await inspect(page, origin + "/apps/memorica/", "06-memory-games.png")
        await inspect(page, origin + "/apps/arena/", "07-arena.png")
        await inspect(page, origin + "/apps/student/", "08-course-home.png")

        play = page.get_by_text("Play", exact=True)
        print("Play controls:", await play.count())
        for index in range(await play.count()):
            if await play.nth(index).is_visible():
                await play.nth(index).click()
                await page.wait_for_timeout(7_000)
                await close_overlays(page)
                await page.screenshot(path=str(RAW / "09-course-play.png"), full_page=False)
                print("09-course-play.png path:", urlsplit(page.url).path)
                print("09-course-play.png labels:", labels(await page.locator("body").inner_text()))
                break

        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
