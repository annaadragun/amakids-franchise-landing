import asyncio
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def origin():
    for line in (ROOT / "amakids-local" / ".env.local").read_text(encoding="utf-8").splitlines():
        if line.startswith("PLATFORM_URL="):
            parsed = urlsplit(line.split("=", 1)[1].strip().strip("\"").strip("'"))
            return f"{parsed.scheme}://{parsed.netloc}"
    raise RuntimeError("Missing platform URL")


def clean(text, limit=180):
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return [line for line in lines if line][:limit]


async def snap(page, name):
    await page.wait_for_timeout(5_000)
    await page.screenshot(path=str(RAW / f"activity-{name}.png"), full_page=False)
    print(name, "path:", urlsplit(page.url).path)
    print(name, "labels:", clean(await page.locator("body").inner_text()))
    print(name, "iframes:", len(page.frames))


async def main():
    base = origin()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()

        await page.goto(base + "/apps/english/level", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(5_000)
        await page.get_by_text("Web Book", exact=True).click()
        await snap(page, "webbook")

        await page.goto(base + "/apps/english/level/homework", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(5_000)
        play = page.get_by_text("Play", exact=True)
        print("Homework Play controls:", await play.count())
        if await play.count():
            await play.first.click()
            await snap(page, "homework-play")

        await page.goto(base + "/apps/arena/", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(6_000)
        rocket = page.get_by_text("Rocket Count", exact=True)
        print("Rocket Count controls:", await rocket.count())
        if await rocket.count():
            await rocket.first.click()
            await snap(page, "arena-rocket")

        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
