import asyncio
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "crm-production" / "raw" / "originals"
STATE = ROOT / ".video-browser" / "crm-state.json"

ROUTES = {
    "01-dashboard": "/teach/",
    "02-trainers": "/teach/index.php?view=teachers",
    "03-groups": "/teach/index.php?view=groups",
    "04-students": "/teach/index.php?view=students",
    "05-leads": "/teach/index.php?view=leads&action=list",
    "06-planner": "/teach/index.php?view=planner",
    "07-reports": "/teach/index.php?view=export_constructor",
    "08-settings": "/teach/index.php?view=franchises_settings",
}


def base_url():
    for raw_line in (ROOT / "amakids-local" / ".env.crm.local").read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("CRM_PLATFORM_URL="):
            parsed = urlsplit(raw_line.split("=", 1)[1].strip().strip("\"").strip("'"))
            return f"{parsed.scheme}://{parsed.netloc}"
    raise RuntimeError("Missing CRM URL")


async def main():
    RAW.mkdir(parents=True, exist_ok=True)
    origin = base_url()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        for name, route in ROUTES.items():
            await page.goto(origin + route, wait_until="domcontentloaded", timeout=90_000)
            await page.wait_for_timeout(4_000)
            await page.screenshot(path=str(RAW / f"{name}.png"), full_page=False)
            headings = await page.locator("h1:visible, h2:visible, h3:visible, legend:visible").all_inner_texts()
            print(name, [" ".join(item.split()) for item in headings if " ".join(item.split())][:12])
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
