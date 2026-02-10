#!/usr/bin/env python3
"""
Quick setup helper - shows instructions for exporting Twitter cookies
"""

import sys
from pathlib import Path

INSTRUCTIONS = """
╔════════════════════════════════════════════════════════════════════╗
║           🍪 TWITTER COOKIE SETUP - 2 MINUTE GUIDE 🍪            ║
╚════════════════════════════════════════════════════════════════════╝

Why: Twitter blocks browser automation. Solution: Use your real session.

Step 1: Login to Twitter
━━━━━━━━━━━━━━━━━━━━━━━
   Open: https://x.com
   Login with your account
   Keep the page open

Step 2: Open Browser Console
━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Press: F12 (or Ctrl+Shift+I)
   Click: "Console" tab
   
Step 3: Copy Cookies
━━━━━━━━━━━━━━━━━━━━
   Paste this code in console:

   copy(JSON.stringify(
     document.cookie.split(';').reduce((acc, c) => {
       const [name, value] = c.trim().split('=');
       if(name) acc[name] = value;
       return acc;
     }, {}),
     null, 2
   ))

   Press: Enter
   You'll see: "Copy to clipboard"

Step 4: Save Cookies
━━━━━━━━━━━━━━━━━━━━
   Right-click → New File
   Name it: twitter_cookies.json
   Paste (Ctrl+V)
   Save to: /home/gmnak2/Allisson/media/twitter_cookies.json

Step 5: Test It
━━━━━━━━━━━━━━━
   Run:
   python3 tests/test_twitter_cookies.py
   
   You should see: ✅ SUCCESS!

╔════════════════════════════════════════════════════════════════════╗
║                         That's it! 🎉                             ║
║                                                                    ║
║  Now your Twitter automation uses real session cookies.           ║
║  No bot detection, no JavaScript blocks, 100% reliable.           ║
╚════════════════════════════════════════════════════════════════════╝

📖 For more details, see:
   - SOLUTION.md (complete guide)
   - LOGIN_MANUALLY.md (detailed instructions)

⏱️  Takes: ~2 minutes
🔐 Security: Keep twitter_cookies.json PRIVATE (contains auth tokens)
"""

if __name__ == "__main__":
    print(INSTRUCTIONS)
    
    # Check if cookies file exists
    cookies_file = Path(__file__).parent / 'media' / 'twitter_cookies.json'
    
    print("\n" + "─"*70)
    if cookies_file.exists():
        print(f"✅ Found: {cookies_file}")
        print("\nTo test your setup, run:")
        print("   python3 tests/test_twitter_cookies.py")
    else:
        print(f"❌ Not found: {cookies_file}")
        print("\nFollow the steps above to create it!")
    print("─"*70 + "\n")
