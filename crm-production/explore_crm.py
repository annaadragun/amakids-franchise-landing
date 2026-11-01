import asyncio
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "crm-production" / "raw"
STATE = ROOT / ".video-browser" / "crm-state.json"


def load_env():
    for raw_line in (ROOT / "amakids-local" / ".env.crm.local").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip("\"").strip("'")


async def main():
    load_env()
    RAW.mkdir(parents=True, exist_ok=True)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900}, locale="en-US")
        page = await context.new_page()
        await page.goto(os.environ["CRM_PLATFORM_URL"], wait_until="domcontentloaded", timeout=90_000)
        await page.locator('input[name="login"]:visible').fill(os.environ["CRM_LOGIN"])
        await page.locator('input[name="password"]:visible').fill(os.environ["CRM_PASSWORD"])
        await page.get_by_role("button", name="Log in", exact=True).click(force=True)
        try:
            await page.wait_for_function("window.location.pathname !== '/'", timeout=45_000)
            await page.wait_for_timeout(6_000)
        except Exception:
            await page.wait_for_timeout(8_000)

        print("Result path:", urlsplit(page.url).path)
        print("Result host:", urlsplit(page.url).netloc)
        nav = await page.locator("nav a:visible, header a:visible, .navbar a:visible").all_inner_texts()
        print("Navigation labels:", [" ".join(item.split()) for item in nav if " ".join(item.split())][:40])
        await page.screenshot(path=str(RAW / "00-dashboard-original.png"), full_page=False)
        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
