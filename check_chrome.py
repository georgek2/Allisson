#!/usr/bin/env python3
"""
Diagnostic script to verify Chrome installation and setup.
Run this before post_tweet.py to confirm Chrome is available.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

print("\n" + "=" * 70)
print("🔍 Chrome Installation & Playwright Setup Diagnostics")
print("=" * 70)

# Check 1: CHROME_PATH environment variable
print("\n1️⃣  Checking CHROME_PATH environment variable...")
chrome_path_env = os.getenv('CHROME_PATH')
if chrome_path_env:
    print(f"   ✅ CHROME_PATH is set: {chrome_path_env}")
else:
    print("   ⚠️  CHROME_PATH not set (will auto-detect)")

# Check 2: Try to find Chrome in common locations
print("\n2️⃣  Searching for Google Chrome binary...")
candidates = [
    chrome_path_env,
    '/usr/bin/google-chrome-stable',
    '/usr/bin/google-chrome',
    '/opt/google/chrome/google-chrome',
    shutil.which('google-chrome-stable'),
    shutil.which('google-chrome'),
]

found_path = None
for cand in [c for c in candidates if c]:
    if os.path.exists(cand):
        found_path = cand
        print(f"   ✅ Found Chrome at: {cand}")
        try:
            version = subprocess.check_output([cand, '--version'], text=True).strip()
            print(f"      Version: {version}")
        except Exception as e:
            print(f"      (Could not get version: {e})")
        break

if not found_path:
    print("   ❌ Google Chrome not found!")
    print("\n   Install Chrome:")
    print("      sudo apt update && sudo apt install -y google-chrome-stable")
    sys.exit(1)

# Check 3: Verify Playwright is installed
print("\n3️⃣  Checking Playwright installation...")
try:
    import playwright
    try:
        from playwright import __version__ as pw_version
        version_str = pw_version
    except ImportError:
        version_str = "installed (version unknown)"
    print(f"   ✅ Playwright {version_str}")
except ImportError:
    print("   ❌ Playwright not installed!")
    print("      pip install -r requirements.txt")
    sys.exit(1)

# Check 4: Verify Playwright can access Chrome
print("\n4️⃣  Testing Playwright + Chrome compatibility...")
try:
    import asyncio
    from playwright.async_api import async_playwright
    
    async def test_chrome():
        try:
            playwright_obj = await async_playwright().start()
            print("      Attempting to launch Chrome via Playwright...")
            # Try channel='chrome' first
            try:
                browser = await playwright_obj.chromium.launch(channel='chrome', headless=False)
                print(f"   ✅ Playwright channel='chrome' works!")
                await browser.close()
                return True
            except Exception as e:
                print(f"      channel='chrome' failed: {e}")
                # Try executable_path
                if found_path:
                    try:
                        browser = await playwright_obj.chromium.launch(executable_path=found_path, headless=True)
                        print(f"   ✅ Playwright executable_path works!")
                        await browser.close()
                        return True
                    except Exception as e2:
                        print(f"      executable_path failed: {e2}")
            finally:
                await playwright_obj.stop()
        except Exception as e:
            print(f"   ❌ Playwright test failed: {e}")
            return False
    
    success = asyncio.run(test_chrome())
    if not success:
        print("\n   ⚠️  Playwright can't launch Chrome. Run:")
        print("      python -m playwright install --with-deps")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error during Playwright test: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ All checks passed! Chrome is ready.")
print("=" * 70)
print("\nYou can now run:")
print("   python post_tweet.py")
print("\nOr set CHROME_PATH explicitly:")
print(f"   export CHROME_PATH={found_path}")
print("   python post_tweet.py")
print("")
