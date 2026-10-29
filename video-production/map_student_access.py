import asyncio
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


async def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    origin = state["origins"][0]["origin"]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        await page.goto(origin + "/teach/", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(3_000)

        links = await page.locator("a:visible").evaluate_all(
            "els => els.map(a => ({text:(a.innerText||'').trim().replace(/\\s+/g,' '), href:a.href}))"
        )
        safe = []
        keywords = ("schül", "student", "spiel", "game", "english", "englisch", "arena", "liga", "league")
        for link in links:
            text = link["text"]
            path = urlsplit(link["href"]).path
            if text and any(word in text.lower() for word in keywords):
                safe.append({"text": text[:80], "path": path})
        print("Relevant links:", safe[:80])

        de = page.get_by_text("DE", exact=True)
        print("DE controls:", await de.count())
        if await de.count():
            print("DE element:", await de.first.evaluate("e => e.closest('.lang-switcher').outerHTML.slice(0, 2400)"))
            await de.first.click()
            await page.wait_for_timeout(1_000)
            menu_texts = await page.locator("a:visible, li:visible").all_inner_texts()
            print(
                "Language choices:",
                [" ".join(t.split()) for t in menu_texts if " ".join(t.split()) in {"EN", "English", "Englisch", "DE", "Deutsch"}],
            )
            await page.screenshot(path=str(RAW / "03-language-menu.png"), full_page=False)

        await page.goto(origin + "/apps/student/", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(5_000)
        app_labels = [" ".join(t.split()) for t in (await page.locator("body").inner_text()).splitlines()]
        print("Student app path:", urlsplit(page.url).path)
        print("Student app labels:", [t for t in app_labels if t][:100])
        await page.screenshot(path=str(RAW / "04-student-app.png"), full_page=True)

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
