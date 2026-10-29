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
    raise RuntimeError("Missing URL")


async def drag_letter(page, letter, target_x, target_y=402):
    item = page.get_by_text(letter, exact=True)
    box = await item.bounding_box()
    if not box:
        raise RuntimeError(f"Letter {letter} is not visible")
    start_x = box["x"] + box["width"] / 2
    start_y = box["y"] + box["height"] / 2
    await page.mouse.move(start_x, start_y)
    await page.mouse.down()
    await page.mouse.move(target_x, target_y, steps=18)
    await page.mouse.up()
    await page.wait_for_timeout(400)


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        await page.goto(base_url() + "/apps/english/level/general/abSea", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)
        next_button = page.get_by_text("Next", exact=True)
        if await next_button.count():
            await next_button.last.click()
            await page.wait_for_timeout(2_000)
        play = page.get_by_text("Play", exact=True)
        if await play.count():
            await play.last.click()
            await page.wait_for_timeout(3_000)

        first_a = page.get_by_text("A", exact=True)
        if await first_a.count():
            print("A ancestors:", await first_a.first.evaluate("e => e.parentElement.parentElement.outerHTML.slice(0, 3000)"))
        print("Draggable elements:", await page.locator('[draggable="true"]').count())
        print(
            "Top empty candidates:",
            await page.locator("div:visible").evaluate_all(
                "els => els.filter(e => !e.innerText.trim() && e.getBoundingClientRect().y > 300 && e.getBoundingClientRect().y < 480 && e.getBoundingClientRect().width > 60 && e.getBoundingClientRect().width < 140).slice(0,20).map(e => ({c:e.className,x:Math.round(e.getBoundingClientRect().x),y:Math.round(e.getBoundingClientRect().y),w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height)}))"
            ),
        )

        for letter in "ABCDEF":
            await page.get_by_text(letter, exact=True).click()
            await page.wait_for_timeout(350)
        await page.wait_for_timeout(4_000)
        await page.screenshot(path=str(RAW / "homework-after-row.png"), full_page=False)
        text = [" ".join(line.split()) for line in (await page.locator("body").inner_text()).splitlines()]
        print([line for line in text if line])
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
