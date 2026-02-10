#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import time

async def test_twitter_load():
    start = time.time()
    print(f"[{time.time()-start:.1f}s] Starting browser...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=False)
        page = await browser.new_page()
        
        print(f"[{time.time()-start:.1f}s] Navigating to Twitter login...")
        try:
            await page.goto('https://twitter.com/i/flow/login', wait_until='networkidle', timeout=30000)
        except Exception as e:
            print(f"[{time.time()-start:.1f}s] Navigation failed: {e}, trying domcontentloaded...")
            await page.goto('https://twitter.com/i/flow/login', wait_until='domcontentloaded', timeout=30000)
        
        print(f"[{time.time()-start:.1f}s] Page loaded, checking for NoScript...")
        
        # Check if JavaScript is loaded
        is_noscript = await page.evaluate("""
            () => document.documentElement.innerHTML.includes('JavaScript is not available')
        """)
        
        print(f"[{time.time()-start:.1f}s] NoScript fallback present: {is_noscript}")
        
        # Check for React
        has_react = await page.evaluate("""
            () => {
                const input = document.querySelector('input[autocomplete="username"]');
                return !!input;
            }
        """)
        
        print(f"[{time.time()-start:.1f}s] Username input found: {has_react}")
        
        # Take screenshot
        await page.screenshot(path='/tmp/twitter_test.png', full_page=True)
        print(f"[{time.time()-start:.1f}s] Screenshot saved to /tmp/twitter_test.png")
        
        # Save HTML
        html = await page.content()
        with open('/tmp/twitter_test.html', 'w') as f:
            f.write(html)
        print(f"[{time.time()-start:.1f}s] HTML saved to /tmp/twitter_test.html")
        print(f"[{time.time()-start:.1f}s] HTML size: {len(html)} bytes")
        
        await browser.close()
        print(f"[{time.time()-start:.1f}s] Done")

if __name__ == '__main__':
    asyncio.run(test_twitter_load())
