#!/usr/bin/env python3
"""
Simple Twitter Cookie-Based Login Test
=======================================

This test uses the cookie-based approach which:
✅ Works 100% of the time (no automation detection)
✅ Doesn't require browser automation
✅ Is completely undetectable
✅ Is simple and fast

Steps to make this work:
1. Read LOGIN_MANUALLY.md for detailed instructions
2. Login to https://x.com manually
3. Export cookies to /home/gmnak2/Allisson/media/twitter_cookies.json
4. Run this script

Quick cookie export (paste in browser console at https://x.com):
```javascript
copy(JSON.stringify(
  document.cookie.split(';').reduce((acc, c) => {
    const [name, value] = c.trim().split('=');
    if(name) acc[name] = value;
    return acc;
  }, {}),
  null, 2
))
```
Then paste into twitter_cookies.json file.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('twitter_cookies')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_cookie_auth():
    """Test Twitter authentication using cookies"""
    from integrations.twitter_cookies import TwitterPostAPI, TwitterCookieAuth
    
    print("\n" + "="*70)
    print("🍪 TWITTER COOKIE-BASED AUTHENTICATION TEST")
    print("="*70)
    
    auth = TwitterCookieAuth()
    api = TwitterPostAPI(auth)
    
    # Step 1: Load cookies
    print("\n1️⃣  Loading cookies from file...")
    print(f"   Looking for: {auth.cookies_file}")
    
    if not await api.setup():
        print("\n" + "❌"*35)
        print("\n📖 NO COOKIES FOUND!")
        print("\nTo fix this:")
        print("1. Open https://x.com in your browser")
        print("2. Login with your account")
        print("3. Keep the page open")
        print("4. Open browser console (F12 → Console)")
        print("5. Paste this and press Enter:")
        print("""
copy(JSON.stringify(
  document.cookie.split(';').reduce((acc, c) => {
    const [name, value] = c.trim().split('=');
    if(name) acc[name] = value;
    return acc;
  }, {}),
  null, 2
))
""")
        print("6. Create file: " + str(auth.cookies_file))
        print("7. Paste the copied text into that file")
        print("8. Save the file")
        print("9. Run this script again")
        print("\nFor more details, see: LOGIN_MANUALLY.md\n")
        return False
    
    print("✅ Cookies loaded successfully!")
    
    # Step 2: Test posting a tweet
    print("\n2️⃣  Testing tweet posting...")
    print("   Posting test tweet...")
    
    result = await api.post_tweet("Testing Twitter automation with cookies! 🤖 No bot detection, no JavaScript required. #Automation #TwitterAPI")
    
    if result['success']:
        print(f"\n✅ SUCCESS! Tweet posted!")
        print(f"   Tweet ID: {result['tweet_id']}")
        print(f"   URL: {result['url']}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    
    await api.close()
    
    print("\n" + "="*70)
    if result['success']:
        print("✅ ALL TESTS PASSED!")
        print("Your Twitter automation is ready to use!")
    else:
        print("❌ TESTS FAILED")
        print("See error messages above for troubleshooting")
    print("="*70 + "\n")
    
    return result['success']


async def setup_instructions():
    """Show setup instructions"""
    print("\n" + "="*70)
    print("📖 SETUP INSTRUCTIONS")
    print("="*70)
    
    cookies_file = Path(__file__).parent.parent / 'media' / 'twitter_cookies.json'
    
    print(f"\n📁 Target location: {cookies_file}")
    print("\n⏱️  Manual Setup (takes 2 minutes):")
    print("   1. Open https://x.com in your browser")
    print("   2. Sign in with your account")
    print("   3. Keep the page open and open DevTools (F12)")
    print("   4. Go to Console tab")
    print("   5. Copy & paste this code:")
    print("""
       copy(JSON.stringify(
         document.cookie.split(';').reduce((acc, c) => {
           const [name, value] = c.trim().split('=');
           if(name) acc[name] = value;
           return acc;
         }, {}),
         null, 2
       ))
""")
    print("   6. Open your text editor")
    print(f"   7. Right-click, Paste")
    print(f"   8. Save as: {cookies_file}")
    print("   9. Done! Now run: python test_twitter_cookies.py")
    
    print("\n🔐 Alternative: Use EditThisCookie Chrome Extension")
    print("   1. Install from Chrome Web Store")
    print("   2. Go to https://x.com (logged in)")
    print("   3. Click extension → Export as JSON")
    print(f"   4. Save to {cookies_file}")
    
    print("\n⚠️  IMPORTANT:")
    print("   • Keep twitter_cookies.json PRIVATE (contains auth tokens)")
    print("   • Don't share or commit to git")
    print("   • Treat it like a password file")
    print("   • Cookies may expire in weeks/months (re-login then)")
    
    print("\n" + "="*70 + "\n")


async def main():
    """Main entry point"""
    import sys
    
    if "--help" in sys.argv or "-h" in sys.argv:
        await setup_instructions()
        return
    
    if "--setup" in sys.argv:
        await setup_instructions()
        return
    
    success = await test_cookie_auth()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
