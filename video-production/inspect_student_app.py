import asyncio
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def useful_lines(text: str):
    return [" ".join(line.split()) for line in text.splitlines() if " ".join(line.split())]


async def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    origin = state["origins"][0]["origin"]
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        await page.goto(origin + "/apps/student/", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)

        scripts = await page.locator("script[src]").evaluate_all("els => els.map(s => s.src)")
        print("Script paths:", [urlsplit(src).path for src in scripts])
        print("Language-related scripts:", [urlsplit(src).path for src in scripts if "lang" in src.lower()])
        inline_scripts = await page.locator("script:not([src])").all_text_contents()
        for script in inline_scripts:
            if "langSwitcher" in script or "data-lang-code" in script:
                print("Language inline JS:", " ".join(script.split())[:4000])

        de_labels = page.get_by_text("DE", exact=True)
        visible_de = None
        for index in range(await de_labels.count()):
            if await de_labels.nth(index).is_visible():
                visible_de = de_labels.nth(index)
                print("Visible DE element:", await visible_de.evaluate("e => e.parentElement.outerHTML.slice(0, 1200)"))
                break
        if visible_de:
            await visible_de.click()
            await page.wait_for_timeout(500)
            dropdowns = page.locator('[class*="langSwitcher-stylesdropdown"]:visible')
            print("Language dropdowns:", await dropdowns.count())
            if await dropdowns.count():
                print("Language dropdown text:", useful_lines(await dropdowns.first.inner_text()))
            choices = page.get_by_text("UK", exact=True)
            print("UK choices:", await choices.count())
            visible_english = None
            for index in range(await choices.count()):
                if await choices.nth(index).is_visible():
                    visible_english = choices.nth(index)
                    break
            if visible_english:
                await visible_english.click()
                try:
                    await page.wait_for_load_state("networkidle", timeout=30_000)
                except Exception:
                    await page.wait_for_timeout(5_000)

        close_candidates = page.locator(
            '[class*="modal"] [class*="close"], [class*="popup"] [class*="close"], button[aria-label="Close"]'
        )
        for i in range(await close_candidates.count()):
            candidate = close_candidates.nth(i)
            if await candidate.is_visible():
                try:
                    await candidate.click(timeout=2_000)
                    break
                except Exception:
                    pass
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(2_000)
        await page.screenshot(path=str(RAW / "05-student-home-en.png"), full_page=False)

        links = await page.locator("a:visible").evaluate_all(
            "els => els.map(a => ({text:(a.innerText||'').trim().replace(/\\s+/g,' '), href:a.href}))"
        )
        print("Current path:", urlsplit(page.url).path)
        print("Home labels:", useful_lines(await page.locator("body").inner_text())[:100])
        print(
            "Visible links:",
            [{"text": x["text"][:80], "path": urlsplit(x["href"]).path} for x in links if x["text"]][:100],
        )

        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
