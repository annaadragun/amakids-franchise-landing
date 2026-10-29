import asyncio
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw"
STATE = ROOT / ".video-browser" / "state.json"


def load_env(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"").strip("'"))


async def main() -> None:
    load_env(ROOT / "amakids-local" / ".env.local")
    platform_url = os.environ["PLATFORM_URL"]
    RAW.mkdir(parents=True, exist_ok=True)
    STATE.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            record_video_dir=str(RAW / "probe-video"),
            record_video_size={"width": 1440, "height": 900},
        )
        page = await context.new_page()
        page.on(
            "request",
            lambda request: print(
                f"Request: {request.method} {urlsplit(request.url).path}"
            )
            if request.method in {"POST", "PUT", "PATCH"}
            else None,
        )
        page.on(
            "response",
            lambda response: print(
                f"Response: {response.status} {urlsplit(response.url).path}"
            )
            if response.request.method in {"POST", "PUT", "PATCH"}
            else None,
        )
        await page.goto(platform_url, wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(4_000)
        await page.screenshot(path=str(RAW / "01-login.png"), full_page=True)

        inputs = await page.locator("input").evaluate_all(
            "els => els.map(e => ({type:e.type, name:e.name, placeholder:e.placeholder, autocomplete:e.autocomplete}))"
        )
        buttons = await page.locator("button, input[type=submit], [role=button]").all_inner_texts()
        print(f"Loaded host: {urlsplit(page.url).netloc}")
        print(f"Title: {await page.title()}")
        print(f"Inputs: {inputs}")
        print(f"Buttons: {[b.strip() for b in buttons if b.strip()][:20]}")

        login_form = page.locator('form:has(input[name="password"]):visible').first
        print(
            "Login form:",
            await login_form.evaluate(
                "f => ({method:f.method, action:f.getAttribute('action'), classes:f.className})"
            ),
        )

        await page.locator('input[name="login"]:visible').fill(os.environ["DEMO_LOGIN"])
        await page.locator('input[name="password"]:visible').fill(os.environ["DEMO_PASSWORD"])
        await page.get_by_role("button", name="Log in", exact=True).click(force=True)
        try:
            await page.wait_for_function("window.location.pathname !== '/'", timeout=45_000)
            await page.wait_for_load_state("domcontentloaded", timeout=45_000)
            await page.wait_for_timeout(5_000)
        except Exception:
            await page.wait_for_timeout(8_000)
        await page.screenshot(path=str(RAW / "02-dashboard.png"), full_page=True)

        visible_text = await page.locator("body").inner_text()
        error_text = await page.locator(
            '.error:visible, .alert:visible, [class*="error"]:visible, [class*="invalid"]:visible'
        ).all_inner_texts()
        safe_lines = []
        for line in visible_text.splitlines():
            cleaned = " ".join(line.split())
            if cleaned and len(cleaned) <= 80:
                safe_lines.append(cleaned)
        print(f"After login path: {urlsplit(page.url).path}")
        print(f"Visible errors: {[e.strip() for e in error_text if e.strip()][:20]}")
        print(f"Visible labels: {safe_lines[:120]}")

        await context.storage_state(path=str(STATE))
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
