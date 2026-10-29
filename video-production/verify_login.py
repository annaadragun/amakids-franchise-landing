import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip("\"").strip("'")


def redact(value):
    private = ("pass", "token", "login", "email", "phone", "cookie", "session")
    if isinstance(value, dict):
        return {
            key: "[redacted]" if any(word in key.lower() for word in private) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


async def main() -> None:
    load_env(ROOT / "amakids-local" / ".env.local")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(locale="en-US")
        await page.goto(os.environ["PLATFORM_URL"], wait_until="domcontentloaded", timeout=90_000)
        await page.locator('input[name="login"]:visible').fill(os.environ["DEMO_LOGIN"])
        await page.locator('input[name="password"]:visible').fill(os.environ["DEMO_PASSWORD"])
        async with page.expect_response(
            lambda response: response.request.method == "POST"
            and urlsplit(response.url).path.endswith("/views/smartum/ajax/ajax.php"),
            timeout=30_000,
        ) as response_info:
            await page.get_by_role("button", name="Log in", exact=True).click(force=True)
        response = await response_info.value
        try:
            body = await response.text()
        except Exception:
            retry = await page.context.request.post(
                response.url,
                form=response.request.post_data_json,
                headers={"Referer": os.environ["PLATFORM_URL"]},
            )
            body = await retry.text()
        print("HTTP status:", response.status)
        try:
            print("Response:", json.dumps(redact(json.loads(body)), ensure_ascii=False))
        except Exception:
            print("Response type: non-JSON")
            print("Response length:", len(body))
        await page.wait_for_timeout(3_000)
        print("Result path:", urlsplit(page.url).path)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
