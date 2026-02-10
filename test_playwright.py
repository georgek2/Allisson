# test_playwright_basic.py
import asyncio
from playwright.async_api import async_playwright

async def test():
    print("🧪 Testing Playwright installation...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.google.com')
        title = await page.title()
        print(f"✅ Success! Page title: {title}")
        await browser.close()

asyncio.run(test())