"""
QUICK TEST - Fixed Twitter Posting
===================================

Run this to test Twitter posting with updated selectors.
Browser will be VISIBLE so you can see what's happening.

If it fails, check the screenshots in: media/screenshots/
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.twitter import TwitterAutomationFixed


async def quick_test():
    """Quick test of Twitter posting"""
    
    load_dotenv()
    
    print("\n" + "=" * 70)
    print("🚀 QUICK TWITTER TEST - AI Software Development Tweet")
    print("=" * 70)
    
    # Check credentials
    username = os.getenv('TWITTER_USERNAME')
    password = os.getenv('TWITTER_PASSWORD')
    email = os.getenv('TWITTER_EMAIL')
    
    if not username or not password:
        print("\n❌ ERROR: Twitter credentials not found in .env")
        print("\nAdd these to your .env file:")
        print("   TWITTER_USERNAME=your_username")
        print("   TWITTER_PASSWORD=your_password")
        print("   TWITTER_EMAIL=your_email@example.com")
        return
    
    print(f"\n✅ Credentials found for: {username}")
    print("\n📋 What will happen:")
    print("   1. Browser will open (VISIBLE mode)")
    print("   2. Navigate to Twitter login")
    print("   3. Enter your credentials")
    print("   4. Post tweet about AI & software development")
    print("   5. Save screenshots at each step")
    print("   6. Wait 10 seconds so you can see the result")
    print("\n💡 Tip: Watch the browser window to see what's happening!")
    print("\n⏳ Starting in 3 seconds...")
    await asyncio.sleep(3)
    
    twitter = TwitterAutomationFixed()
    
    try:
        # Start browser in VISIBLE mode
        print("\n🌐 Opening browser...")
        # Request launching system Chrome for more consistent behavior
        # Pass CHROME_PATH env var if set
        chrome_path = os.getenv('CHROME_PATH')
        await twitter.start_browser(headless=False, use_chrome=True, chrome_path=chrome_path)
        
        # Login
        print("🔐 Logging in to Twitter...")
        print("   (This may take 30-60 seconds)")
        login_success = await twitter.login(
            username=username,
            password=password,
            email=email
        )
        
        if not login_success:
            print("\n❌ Login failed!")
            print("\n📸 Check screenshots in: media/screenshots/")
            print("   Look for files starting with: twitter_error_")
            print("\n💡 Common issues:")
            print("   - Wrong username/password")
            print("   - Twitter asking for 2FA (not supported yet)")
            print("   - Twitter asking for email verification (set TWITTER_EMAIL)")
            return
        
        print("\n✅ Login successful!")
        
        # Post tweet
        print("\n📝 Posting tweet about AI...")
        tweet_content = "AI is revolutionizing software development! From intelligent code completion to automated testing, developers are 10x more productive. The future is here! 🚀 #AI #SoftwareDevelopment #TechInnovation"
        
        result = await twitter.post_tweet(tweet_content)
        
        print("\n" + "=" * 70)
        print("📊 RESULT")
        print("=" * 70)
        
        if result['success']:
            print("\n🎉 SUCCESS! Tweet posted!")
            print(f"\n📱 Platform: {result['platform']}")
            print(f"🔗 URL: {result['url']}")
            print(f"\n📝 Content:")
            print(f'   "{tweet_content}"')
            print("\n✅ Go check your Twitter profile to see the tweet!")
        else:
            print("\n❌ FAILED to post tweet")
            print(f"   Error: {result.get('error')}")
            print("\n📸 Check screenshots in: media/screenshots/")
        
        # Wait so user can see the result
        print("\n⏳ Browser will close in 10 seconds...")
        print("   (Check Twitter now to verify the tweet posted!)")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\n📸 Check screenshots in: media/screenshots/")
        
    finally:
        await twitter.close_browser()
        print("\n👋 Browser closed")
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)
    print("\n📸 All screenshots saved in: media/screenshots/")
    print("   Files are numbered (01, 02, 03...) showing each step")
    print("\n")


if __name__ == "__main__":
    asyncio.run(quick_test())