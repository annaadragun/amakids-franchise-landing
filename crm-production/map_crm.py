import asyncio
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".video-browser" / "crm-state.json"


def load_env():
    for raw_line in (ROOT / "amakids-local" / ".env.crm.local").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip("\"").strip("'")


async def main():
    load_env()
    parsed = urlsplit(os.environ["CRM_PLATFORM_URL"])
    origin = f"{parsed.scheme}://{parsed.netloc}"
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        await page.goto(origin + "/teach/", wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)
        for label in ("Franchisee", "Trainers", "Groups", "Students", "Leads"):
            item = page.get_by_text(label, exact=True)
            if not await item.count():
                continue
            await item.first.hover()
            await page.wait_for_timeout(400)
            links = await page.locator("a:visible").evaluate_all(
                "els => els.map(a => ({text:(a.innerText||'').trim().replace(/\\s+/g,' '), href:a.href}))"
            )
            safe = []
            for link in links:
                text = link["text"]
                parsed_link = urlsplit(link["href"])
                path = parsed_link.path
                route = path + (f"?{parsed_link.query}" if parsed_link.query else "")
                if text and len(text) < 80 and path.startswith("/teach"):
                    safe.append({"text": text, "route": route})
            print(label, safe[:40])
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
