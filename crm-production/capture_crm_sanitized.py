import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "crm-production" / "raw" / "sanitized"
STATE = ROOT / ".video-browser" / "crm-state.json"

ROUTES = {
    "01-dashboard": "/teach/",
    "02-trainers": "/teach/index.php?view=teachers",
    "03-groups": "/teach/index.php?view=groups",
    "04-students": "/teach/index.php?view=students",
    "05-leads": "/teach/index.php?view=leads&action=list",
    "06-reports": "/teach/index.php?view=export_constructor",
    "07-settings": "/teach/index.php?view=franchises_settings",
    "08-group-schedule": "/teach/index.php?view=group&group_id=20736",
    "09-settings-packages": "/teach/index.php?view=franchises_settings",
}

SANITIZE_JS = r"""
() => {
  const replacements = [
    [/Anna Test 2/gi, 'Demo Center'],
    [/Anna test USA/gi, 'Demo Learning Center'],
    [/Anna Teacher test/gi, 'Teacher 1'],
    [/Test Teacher/gi, 'Teacher 2'],
    [/Anna test USA/gi, 'Demo Learning Center'],
    [/Antonina Zaika/gi, 'Teacher 3'],
    [/Olha Test trainer/gi, 'Teacher 4'],
    [/Nandani Dixit/gi, 'Teacher 5'],
    [/Test Test/gi, 'Teacher 6'],
    [/Test Student/gi, 'Student 2'],
    [/Тест Student/gi, 'Student 2'],
    [/Тест/g, 'Student 1'],
    [/\bID\s*-\s*\d+/g, 'Demo Account'],
    [/\bID:\s*\d+/g, 'ID: DEMO'],
    [/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, 'contact@demo-center.com'],
    [/12345678/g, '+1 555 0100'],
  ];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    let value = node.nodeValue || '';
    for (const [pattern, replacement] of replacements) value = value.replace(pattern, replacement);
    if (value !== node.nodeValue) node.nodeValue = value;
  }

  document.querySelectorAll('input[type="text"], input[type="email"]').forEach((input) => {
    if (/email/i.test(input.value)) input.value = 'contact@demo-center.com';
  });

}
"""


def base_url():
    for raw_line in (ROOT / "amakids-local" / ".env.crm.local").read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("CRM_PLATFORM_URL="):
            parsed = urlsplit(raw_line.split("=", 1)[1].strip().strip("\"").strip("'"))
            return f"{parsed.scheme}://{parsed.netloc}"
    raise RuntimeError("Missing CRM URL")


async def route_specific_sanitization(page, name):
    if name == "02-trainers":
        rows = page.locator("table tbody tr")
        for index in range(await rows.count()):
            cells = rows.nth(index).locator("td")
            if await cells.count() >= 7:
                await cells.nth(1).evaluate("(e, v) => e.textContent = v", f"T-{index + 1:03d}")
                await cells.nth(2).evaluate("(e, v) => e.textContent = v", f"Teacher {index + 1}")
                await cells.nth(5).evaluate(
                    "(e, v) => e.innerHTML = v",
                    f"teacher{index + 1}@demo-center.com<br>+1 555 01{index + 1:02d}",
                )
    elif name == "03-groups":
        rows = page.locator("table tbody tr")
        for index in range(await rows.count()):
            cells = rows.nth(index).locator("td")
            if await cells.count() >= 6:
                await cells.nth(0).evaluate("(e, v) => e.textContent = v", f"G-{index + 1:03d}")
                await cells.nth(1).evaluate(
                    "(e, v) => e.innerHTML = v",
                    f"<b>{['English A1', 'Mental Math', 'Memory Skills'][index % 3]} • Group {index + 1}</b><br>Demo Learning Center<br>{6 + index} students",
                )
                await cells.nth(5).evaluate("(e, v) => e.textContent = v", f"Teacher {(index % 4) + 1}")
    elif name == "04-students":
        rows = page.locator("table tbody tr")
        for index in range(await rows.count()):
            cells = rows.nth(index).locator("td")
            if await cells.count() >= 6:
                await cells.nth(1).evaluate("(e, v) => e.textContent = v", f"S-{index + 1:03d}")
                await cells.nth(2).evaluate("(e, v) => e.textContent = v", f"Student {index + 1}")
                await cells.nth(3).evaluate(
                    "(e, v) => e.innerHTML = v",
                    f"Parent {index + 1}<br>student{index + 1}@example.com<br>No unread messages",
                )
                await cells.nth(5).evaluate(
                    "(e, v) => e.innerHTML = v",
                    f"Group: English A1<br>Trainer: Teacher {(index % 4) + 1}",
                )
    elif name == "05-leads":
        await page.evaluate(
            """() => document.querySelectorAll('option').forEach((o) => {
              if (/Anna|test/i.test(o.textContent)) o.textContent = 'Demo Learning Center';
            })"""
        )
    elif name in ("07-settings", "09-settings-packages"):
        inputs = page.locator("input")
        for index in range(await inputs.count()):
            item = inputs.nth(index)
            value = await item.input_value()
            if "@" in value:
                await item.fill("contact@demo-center.com")
    elif name == "08-group-schedule":
        await page.locator("h1, h2, h3").filter(has_text='Group "English').first.evaluate(
            "e => e.childNodes[0].nodeValue = 'Group \"English A1 • Group 1\"'"
        )
        await page.evaluate(
            """() => {
              const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
              let node;
              while ((node = walker.nextNode())) {
                node.nodeValue = (node.nodeValue || '')
                  .replace(/Group \"English\s*\"/g, 'Group "English A1 • Group 1"')
                  .replace(/English\(Level 1\)/g, 'English • Level 1');
              }
            }"""
        )


async def main():
    RAW.mkdir(parents=True, exist_ok=True)
    origin = base_url()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=str(STATE), viewport={"width": 1440, "height": 900}, locale="en-US"
        )
        page = await context.new_page()
        selected = set(sys.argv[1:])
        routes = {name: route for name, route in ROUTES.items() if not selected or name in selected}
        for name, route in routes.items():
            await page.goto(origin + route, wait_until="domcontentloaded", timeout=90_000)
            await page.wait_for_timeout(5_000)
            await page.evaluate(SANITIZE_JS)
            await route_specific_sanitization(page, name)
            await page.evaluate(SANITIZE_JS)
            if name == "09-settings-packages":
                package_heading = page.get_by_text("Settings for package discounts", exact=False).first
                await package_heading.scroll_into_view_if_needed()
                await package_heading.evaluate(
                    "e => window.scrollBy(0, e.getBoundingClientRect().top - 120)"
                )
                await page.wait_for_timeout(700)
            await page.wait_for_timeout(1_200)
            await page.evaluate(SANITIZE_JS)
            await page.screenshot(path=str(RAW / f"{name}.png"), full_page=False)
            print("Captured", name)
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
