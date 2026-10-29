from playwright.sync_api import sync_playwright
import sys, pathlib

root = pathlib.Path(sys.argv[1]).resolve()
scale = int(sys.argv[2]) if len(sys.argv) > 2 else 2
files = sorted(root.rglob("*.html"))

with sync_playwright() as p:
    try:
        browser = p.chromium.launch()
    except Exception:
        browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(device_scale_factor=scale)
    for src in files:
        out = src.with_suffix(".png")
        page.goto(f"file:///{src.as_posix()}")
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        page.locator("svg").first.screenshot(path=str(out), omit_background=True)
        print("PNG", out.relative_to(root))
    browser.close()
