"""
Test script for Twitter/X automation
====================================

This script tests the TwitterAutomation class and the full Hannah agent integration.
"""

import asyncio
import os
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('allisson')


async def test_twitter_automation():
    """Test basic Twitter automation"""
    from integrations.social_media import TwitterAutomation
    
    print("\n" + "="*70)
    print("🧪 Testing Twitter Automation")
    print("="*70)
    
    twitter = TwitterAutomation()
    
    try:
        # Start browser
        print("\n1️⃣  Starting browser...")
        await twitter.start_browser(headless=True)  # Set to False to see browser
        
        # Login
        print("2️⃣  Logging in to Twitter...")
        from dotenv import load_dotenv
        load_dotenv()
        
        success = await twitter.login(
            username=os.getenv('TWITTER_USERNAME'),
            password=os.getenv('TWITTER_PASSWORD'),
            email=os.getenv('TWITTER_EMAIL')
        )
        
        if not success:
            print("❌ Login failed - check screenshots in media/screenshots/")
            print("   Look for twitter_error_*.png files for debugging info")
            return False
        
        print("✅ Login successful!")
        
        # Post a test tweet
        print("3️⃣  Posting a test tweet...")
        result = await twitter.post_tweet(
            "Test tweet from Playwright automation! 🤖 #automation"
        )
        
        if result['success']:
            print(f"✅ Tweet posted successfully!")
            print(f"   URL: {result['url']}")
            return True
        else:
            print(f"❌ Tweet posting failed: {result.get('error')}")
            print("   Check screenshots in media/screenshots/twitter_error_*.png")
            return False
    
    finally:
        await twitter.close_browser()


async def test_hannah_agent():
    """Test Hannah agent for Twitter posting"""
    from agents.hannah import HannahAgent
    
    print("\n" + "="*70)
    print("🧪 Testing Hannah Agent")
    print("="*70)
    
    hannah = HannahAgent()
    
    print("\n1️⃣  Generating tweet content...")
    result = await hannah.execute(
        command="Post a tweet about artificial intelligence",
        context={"tone": "informative"}
    )
    
    if result.get('success'):
        print("✅ Hannah agent execution successful!")
        print(f"   Task ID: {result.get('task_id')}")
        print(f"   Execution time: {result.get('execution_time'):.2f}s")
        
        # Show final result
        final = result.get('result', {})
        if isinstance(final, dict) and 'final_output' in final:
            output = final['final_output']
            if output.get('success'):
                print(f"✅ Tweet posted: {output.get('url')}")
                return True
    
    print(f"❌ Hannah agent execution failed")
    print(f"   Result: {result}")
    return False


async def test_twitter_with_visibility():
    """Test Twitter automation with visible browser"""
    from integrations.social_media import TwitterAutomation
    
    print("\n" + "="*70)
    print("🧪 Testing Twitter Automation (VISIBLE BROWSER)")
    print("="*70)
    print("\n⚠️  This test shows the browser in action for debugging.")
    print("   The browser will open automatically. Watch the login process.")
    
    twitter = TwitterAutomation()
    
    try:
        # Start browser in VISIBLE mode
        print("\n1️⃣  Starting visible browser...")
        await twitter.start_browser(headless=False)
        
        # Login
        print("2️⃣  Logging in to Twitter (you can see the browser)...")
        from dotenv import load_dotenv
        load_dotenv()
        
        success = await twitter.login(
            username=os.getenv('TWITTER_USERNAME'),
            password=os.getenv('TWITTER_PASSWORD'),
            email=os.getenv('TWITTER_EMAIL')
        )
        
        if not success:
            print("❌ Login failed")
            return False
        
        print("✅ Login successful!")
        
        # Wait for user to see the result
        print("⏳ Keeping browser open for 10 seconds...")
        await asyncio.sleep(10)
        
        return True
    
    finally:
        await twitter.close_browser()


async def test_environment_setup():
    """Verify environment setup"""
    print("\n" + "="*70)
    print("🔍 Checking Environment Setup")
    print("="*70)
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    checks = {
        "TWITTER_USERNAME": os.getenv('TWITTER_USERNAME'),
        "TWITTER_PASSWORD": os.getenv('TWITTER_PASSWORD'),
        "TWITTER_EMAIL": os.getenv('TWITTER_EMAIL'),
        "GROQ_API_KEY": os.getenv('GROQ_API_KEY'),
        "CHROME_PATH": os.getenv('CHROME_PATH'),
    }
    
    all_good = True
    for var, value in checks.items():
        if var in ['TWITTER_USERNAME', 'TWITTER_PASSWORD', 'TWITTER_EMAIL', 'GROQ_API_KEY']:
            status = "✅" if value else "❌"
            if not value:
                all_good = False
            print(f"{status} {var}: {'SET' if value else 'NOT SET'}")
        else:
            status = "✅" if value else "⚠️"
            print(f"{status} {var}: {value or 'Using default'}")
    
    # Check Chrome
    import shutil
    chrome_path = shutil.which('google-chrome-stable') or shutil.which('google-chrome')
    if chrome_path:
        print(f"✅ Chrome found at: {chrome_path}")
    else:
        print("❌ Chrome not found - install Google Chrome first")
        all_good = False
    
    return all_good


async def main():
    """Run all tests"""
    
    print("\n" + "="*70)
    print("🚀 TWITTER AUTOMATION TEST SUITE")
    print("="*70)
    
    # First, check environment
    print("\nRunning environment checks...")
    env_ok = await test_environment_setup()
    
    if not env_ok:
        print("\n❌ Environment setup incomplete. Fix the issues above and try again.")
        return
    
    # Test basic automation
    print("\nRunning basic automation test...")
    automation_ok = await test_twitter_automation()
    
    if automation_ok:
        print("\n✅ Basic automation test PASSED")
    else:
        print("\n❌ Basic automation test FAILED")
        print("   Check media/screenshots/ for debugging info")
        return
    
    # Test Hannah agent
    print("\nRunning Hannah agent test...")
    hannah_ok = await test_hannah_agent()
    
    if hannah_ok:
        print("\n✅ Hannah agent test PASSED")
    else:
        print("\n❌ Hannah agent test FAILED")
    
    print("\n" + "="*70)
    print("✅ TEST SUITE COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. If tests passed: You're ready to use Twitter automation!")
    print("2. If tests failed: Check media/screenshots/ for debugging info")
    print("3. Run with visible browser: python tests/test_twitter_automation.py --visible")
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if "--visible" in sys.argv:
        print("\n🔍 Running with VISIBLE browser for debugging...")
        asyncio.run(test_twitter_with_visibility())
    else:
        asyncio.run(main())
