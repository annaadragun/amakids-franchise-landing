import asyncio
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def platform_origin():
    for line in (ROOT / "amakids-local" / ".env.local").read_text(encoding="utf-8").splitlines():
        if line.startswith("PLATFORM_URL="):
            value = line.split("=", 1)[1].strip().strip("\"").strip("'")
            parts = urlsplit(value)
            return f"{parts.scheme}://{parts.netloc}"
    raise RuntimeError("PLATFORM_URL is missing")


def labels(text, limit=180):
    values = [" ".join(line.split()) for line in text.splitlines()]
    return [value for value in values if value][:limit]


async def close_modal(page):
    await page.keyboard.press("Escape")
    for selector in ('[class*="modal"] [class*="close"]', '[class*="popup"] [class*="close"]'):
        items = page.locator(selector)
        for index in range(await items.count()):
            if await items.nth(index).is_visible():
                try:
                    await items.nth(index).click(timeout=1_000)
                except Exception:
                    pass


async def enter_flow(page, origin, enter_index, name):
    await page.goto(origin + "/apps/student/", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(5_000)
    await close_modal(page)
    enters = page.get_by_text("Enter", exact=True)
    print("Enter count:", await enters.count())
    for index in range(await enters.count()):
        print("Enter", index, "parent class:", await enters.nth(index).evaluate("e => e.parentElement.parentElement.className"))
    await enters.nth(enter_index).click()
    await page.wait_for_timeout(9_000)
    await close_modal(page)
    await page.screenshot(path=str(RAW / f"learning-{name}.png"), full_page=False)
    print(name, "path:", urlsplit(page.url).path)
    print(name, "labels:", labels(await page.locator("body").inner_text()))


async def main():
    origin = platform_origin()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        await enter_flow(page, origin, 0, "english")
        await enter_flow(page, origin, 1, "challenge")
        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
