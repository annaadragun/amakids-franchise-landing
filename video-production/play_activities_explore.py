import asyncio
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def base_url():
    for line in (ROOT / "amakids-local" / ".env.local").read_text(encoding="utf-8").splitlines():
        if line.startswith("PLATFORM_URL="):
            parsed = urlsplit(line.split("=", 1)[1].strip().strip("\"").strip("'"))
            return f"{parsed.scheme}://{parsed.netloc}"
    raise RuntimeError("Missing PLATFORM_URL")


def clean(text, limit=160):
    values = [" ".join(line.split()) for line in text.splitlines()]
    return [value for value in values if value][:limit]


async def metadata(page, name):
    await page.wait_for_timeout(6_000)
    await page.screenshot(path=str(RAW / f"play-{name}.png"), full_page=False)
    print(name, "path:", urlsplit(page.url).path)
    print(name, "labels:", clean(await page.locator("body").inner_text()))
    print(
        name,
        "inputs:",
        await page.locator("input:visible").evaluate_all(
            "els => els.map(e => ({type:e.type, placeholder:e.placeholder, value:e.value, classes:e.className}))"
        ),
    )
    print(name, "buttons:", clean("\n".join(await page.locator("button:visible").all_inner_texts())))
    print(name, "canvas:", await page.locator("canvas:visible").count())


async def main():
    base = base_url()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()

        await page.goto(base + "/apps/english/level/general/abSea", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)
        plays = page.get_by_text("Play", exact=True)
        print("homework setup path:", urlsplit(page.url).path)
        print("homework setup labels:", clean(await page.locator("body").inner_text()))
        print("homework play controls:", await plays.count())
        next_button = page.get_by_text("Next", exact=True)
        if await next_button.count():
            await next_button.last.click()
            await page.wait_for_timeout(3_000)
            print("homework after Next:", clean(await page.locator("body").inner_text()))
            plays = page.get_by_text("Play", exact=True)
        if await plays.count():
            await plays.last.click()
            await metadata(page, "homework-game")

        await page.goto(base + "/apps/arena/game/ma-rocket", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)
        together = page.get_by_text("Play together", exact=True)
        if await together.count():
            await together.first.click()
            await metadata(page, "arena-game")
            player_two = page.locator('input[placeholder="Player 2"]')
            if await player_two.count():
                await player_two.fill("Mia")
            start = page.get_by_text("Start!", exact=True)
            if await start.count():
                await start.click()
                await metadata(page, "arena-started")

        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
