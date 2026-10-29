import asyncio
import re
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "video-production" / "raw" / "final-takes"
STATE = ROOT / ".video-browser" / "state.json"
VIEWPORT = {"width": 1440, "height": 900}


def base_url():
    for line in (ROOT / "amakids-local" / ".env.local").read_text(encoding="utf-8").splitlines():
        if line.startswith("PLATFORM_URL="):
            parsed = urlsplit(line.split("=", 1)[1].strip().strip("\"").strip("'"))
            return f"{parsed.scheme}://{parsed.netloc}"
    raise RuntimeError("Missing PLATFORM_URL")


SANITIZE_JS = r"""
(() => {
  const replace = () => {
    const walker = document.createTreeWalker(document.body || document.documentElement, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.nodeValue) {
        const updated = node.nodeValue
          .replace(/TestPlus/g, 'Alex')
          .replace(/\bTest\b/g, 'Alex');
        if (updated !== node.nodeValue) node.nodeValue = updated;
      }
    }
  };
  const boot = () => {
    replace();
    new MutationObserver(replace).observe(document.body, {subtree: true, childList: true, characterData: true});
    document.addEventListener('click', (event) => {
      const dot = document.createElement('div');
      Object.assign(dot.style, {
        position: 'fixed', left: `${event.clientX - 12}px`, top: `${event.clientY - 12}px`,
        width: '24px', height: '24px', borderRadius: '50%', border: '3px solid #f8007f',
        zIndex: 2147483647, pointerEvents: 'none', opacity: '0.9', transition: 'all .45s ease-out'
      });
      document.body.appendChild(dot);
      requestAnimationFrame(() => { dot.style.transform = 'scale(2.2)'; dot.style.opacity = '0'; });
      setTimeout(() => dot.remove(), 500);
    }, true);
  };
  if (document.body) boot(); else document.addEventListener('DOMContentLoaded', boot, {once:true});
})();
"""


async def close_overlays(page):
    await page.keyboard.press("Escape")
    candidates = page.locator(
        '[class*="modal"] [class*="close"], [class*="popup"] [class*="close"], button[aria-label="Close"]'
    )
    for index in range(await candidates.count()):
        candidate = candidates.nth(index)
        if await candidate.is_visible():
            try:
                await candidate.click(timeout=1_500)
                await page.wait_for_timeout(500)
            except Exception:
                pass


async def new_recording(browser, name, authenticated=True):
    RAW.mkdir(parents=True, exist_ok=True)
    options = {
        "viewport": VIEWPORT,
        "locale": "en-US",
        "record_video_dir": str(RAW / "tmp"),
        "record_video_size": VIEWPORT,
    }
    if authenticated:
        options["storage_state"] = str(STATE)
    context = await browser.new_context(**options)
    await context.add_init_script(SANITIZE_JS)
    page = await context.new_page()
    return context, page, RAW / f"{name}.webm"


async def finish_recording(context, page, destination):
    video = page.video
    await page.close()
    await context.close()
    await video.save_as(str(destination))
    print("Saved", destination.name)


async def record_login(browser, base):
    context, page, output = await new_recording(browser, "01-login", authenticated=False)
    await page.goto(base + "/", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(4_000)
    await finish_recording(context, page, output)


async def record_dashboard(browser, base):
    context, page, output = await new_recording(browser, "02-dashboard")
    await page.goto(base + "/apps/student/", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(5_000)
    await close_overlays(page)
    await page.mouse.move(420, 210, steps=15)
    await page.wait_for_timeout(2_000)
    await page.mouse.move(820, 210, steps=15)
    await page.wait_for_timeout(2_000)
    await page.mouse.move(460, 610, steps=15)
    await page.wait_for_timeout(2_000)
    await finish_recording(context, page, output)


async def record_learning(browser, base):
    context, page, output = await new_recording(browser, "03-learning")
    await page.goto(base + "/apps/english/level", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(4_000)
    web_book = page.get_by_text("Web Book", exact=True)
    await web_book.click()
    await page.wait_for_timeout(5_000)
    await page.mouse.wheel(0, 520)
    await page.wait_for_timeout(2_000)
    await page.mouse.wheel(0, 520)
    await page.wait_for_timeout(2_000)
    await page.mouse.wheel(0, -420)
    await page.wait_for_timeout(2_000)
    await finish_recording(context, page, output)


async def record_homework(browser, base):
    context, page, output = await new_recording(browser, "04-homework")
    await page.goto(base + "/apps/english/level/homework", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(4_000)
    play = page.get_by_text("Play", exact=True)
    await play.first.click()
    await page.wait_for_timeout(3_000)
    next_button = page.get_by_text("Next", exact=True)
    if await next_button.count():
        await next_button.last.click()
        await page.wait_for_timeout(3_000)
    play = page.get_by_text("Play", exact=True)
    if await play.count():
        await play.last.click()
        await page.wait_for_timeout(3_000)

    for _round in range(3):
        for letter in "ABCDEF":
            await page.get_by_text(letter, exact=True).click()
            await page.wait_for_timeout(300)
        await page.wait_for_timeout(1_700)
    await page.wait_for_timeout(5_000)
    await finish_recording(context, page, output)


async def record_motivation(browser, base):
    context, page, output = await new_recording(browser, "05-motivation")
    await page.goto(base + "/apps/student/tournament", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(5_000)
    await page.mouse.wheel(0, 430)
    await page.wait_for_timeout(2_000)
    await page.goto(base + "/apps/student/achievements", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(5_000)
    await page.mouse.wheel(0, 520)
    await page.wait_for_timeout(2_000)
    await page.mouse.wheel(0, 520)
    await page.wait_for_timeout(2_000)
    await finish_recording(context, page, output)


def parse_arena_sum(panel_text):
    lines = [line.strip() for line in panel_text.splitlines() if line.strip()]
    numbers = lines[4:9]
    values = [int(value.replace("−", "-").replace("+", "")) for value in numbers]
    return sum(values)


async def answer_panel(panel, answer):
    if answer < 0:
        raise RuntimeError("Unexpected negative Arena answer")
    for digit in str(answer):
        await panel.get_by_role("button", name=digit, exact=True).click()
        await asyncio.sleep(0.22)
    await panel.locator("button").last.click(timeout=5_000)


async def record_arena(browser, base):
    context, page, output = await new_recording(browser, "06-arena")
    await page.goto(base + "/apps/arena/", wait_until="domcontentloaded", timeout=90_000)
    await page.wait_for_timeout(5_000)
    english_game = page.get_by_text("Catch the Word!", exact=True)
    if await english_game.count():
        await english_game.scroll_into_view_if_needed()
        await page.wait_for_timeout(3_000)
    rocket = page.get_by_text("Rocket Count", exact=True)
    await rocket.scroll_into_view_if_needed()
    await page.wait_for_timeout(2_000)
    await rocket.click()
    await page.wait_for_timeout(4_000)
    await page.get_by_text("Play together", exact=True).click()
    await page.wait_for_timeout(3_000)
    player_two = page.locator('input[placeholder="Player 2"]')
    await player_two.fill("Mia")
    await page.wait_for_timeout(1_000)
    await page.get_by_text("Start!", exact=True).click()
    await page.wait_for_timeout(6_000)

    for _round in range(2):
        panels = page.locator(".pan")
        if await panels.count() < 2:
            break
        answers = [parse_arena_sum(await panels.nth(index).inner_text()) for index in range(2)]
        await answer_panel(panels.nth(0), answers[0])
        await page.wait_for_timeout(500)
        await answer_panel(panels.nth(1), answers[1])
        await page.wait_for_timeout(2_000)
    await page.wait_for_timeout(3_000)
    await finish_recording(context, page, output)


async def main():
    base = base_url()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        await record_arena(browser, base)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
