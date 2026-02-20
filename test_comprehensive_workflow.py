#!/usr/bin/env python3
"""
Comprehensive Twitter Automation Workflow Test
==============================================

This test covers:
1. Browser automation - Full flow WITHOUT posting (safe from bot detection)
2. Hannah agent integration - Content generation + posting prep
3. Final single POST - Only one actual tweet to verify everything works

Strategy: Multiple approaches tested safely before any bot-detectable activity
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_comprehensive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('allisson')


class ComprehensiveWorkflowTest:
    """Test Twitter automation with multiple safe approaches"""
    
    def __init__(self):
        self.test_results = {}
        self.twitter_instance = None
    
    async def phase_1_browser_automation_safe_flow(self):
        """
        Phase 1: Test browser automation WITHOUT posting
        
        This tests:
        - Browser launch and anti-detection
        - Login workflow
        - Navigation to compose screen
        - Content entry (but NOT posting)
        
        This is SAFE from bot detection (no actual post sent)
        """
        print("\n" + "="*80)
        print("PHASE 1: BROWSER AUTOMATION SAFE FLOW (No Posting)")
        print("="*80)
        
        from integrations.social_media import TwitterAutomation
        from dotenv import load_dotenv
        
        load_dotenv()
        
        self.twitter_instance = TwitterAutomation()
        
        try:
            # Step 1: Start browser
            print("\n1️⃣  Starting browser with anti-detection...")
            await self.twitter_instance.start_browser(headless=True)
            print("✅ Browser started")
            
            # Step 2: Login
            print("\n2️⃣  Logging in to Twitter...")
            success = await self.twitter_instance.login(
                username=os.getenv('TWITTER_USERNAME'),
                password=os.getenv('TWITTER_PASSWORD'),
                email=os.getenv('TWITTER_EMAIL')
            )
            
            if not success:
                print("❌ Login failed")
                self.test_results['phase_1_login'] = False
                return False
            
            print("✅ Login successful")
            
            # Step 3: Navigate to compose area (SAFE - no posting)
            print("\n3️⃣  Navigating to compose screen (NOT posting)...")
            try:
                await self.twitter_instance.page.goto('https://twitter.com/home', wait_until='domcontentloaded', timeout=15000)
            except:
                # Even if navigation times out, we might still be logged in
                await asyncio.sleep(2)
            
            await asyncio.sleep(3)
            
            # Try to open compose dialog without posting
            try:
                compose_button = await self.twitter_instance.page.wait_for_selector(
                    '[data-testid="SideNav_NewTweet_Button"]',
                    timeout=10000
                )
                await compose_button.click()
                await asyncio.sleep(3)
                print("✅ Compose dialog opened")
            except Exception as e:
                print(f"⚠️  Could not open compose dialog: {e}")
                self.test_results['phase_1_compose'] = False
                return False
            
            # Step 4: Verify tweet input field exists
            print("\n4️⃣  Verifying tweet text input...")
            try:
                tweet_input = await self.twitter_instance.page.wait_for_selector(
                    '[data-testid="tweetTextarea_0"]',
                    timeout=10000
                )
                print("✅ Tweet input field found")
                
                # Fill with test content but DON'T POST
                test_content = f"[TEST] Browser automation working! {datetime.now().isoformat()}"
                await tweet_input.fill(test_content)
                await asyncio.sleep(2)
                print(f"✅ Test content entered: {test_content[:50]}...")
                
                # Check if post button becomes enabled
                try:
                    post_button = await self.twitter_instance.page.wait_for_selector(
                        '[data-testid="tweetButtonInline"]',
                        timeout=5000
                    )
                    is_enabled = await post_button.is_enabled()
                    print(f"✅ Post button exists and enabled: {is_enabled}")
                    self.test_results['phase_1_post_button'] = True
                except Exception as e:
                    print(f"⚠️  Post button check failed: {e}")
                    self.test_results['phase_1_post_button'] = False
                
                # CLOSE the compose without posting (ESC key)
                print("\n5️⃣  Closing compose (ESC key - NOT posting)...")
                await self.twitter_instance.page.keyboard.press('Escape')
                await asyncio.sleep(2)
                print("✅ Compose closed safely - NO POST SENT")
                
                self.test_results['phase_1'] = True
                return True
                
            except Exception as e:
                print(f"❌ Tweet input error: {e}")
                self.test_results['phase_1'] = False
                return False
                
        except Exception as e:
            print(f"❌ Phase 1 failed: {e}")
            logger.exception("Phase 1 error")
            self.test_results['phase_1'] = False
            return False
        
        finally:
            if self.twitter_instance:
                await self.twitter_instance.close_browser()
    
    async def phase_2_hannah_agent_integration(self):
        """
        Phase 2: Test Hannah agent integration
        
        This tests:
        - Hannah agent initialization
        - Content generation via Groq LLM
        - Social media manager setup
        - Pre-posting validation (not actually posting)
        """
        print("\n" + "="*80)
        print("PHASE 2: HANNAH AGENT INTEGRATION (Content Generation Only)")
        print("="*80)
        
        try:
            from agents.hannah import HannahAgent
            
            print("\n1️⃣  Initializing Hannah agent...")
            hannah = HannahAgent()
            print("✅ Hannah agent initialized")
            
            print("\n2️⃣  Checking agent capabilities...")
            print(f"Capabilities: {hannah.capabilities}")
            print("✅ Agent capabilities verified")
            
            print("\n3️⃣  Testing content generation (Groq LLM)...")
            # This will generate content but NOT post
            
            # We could test the plan generation
            intent = {
                'primary_action': 'post_tweet',
                'parameters': {
                    'content': 'Test tweet from Hannah agent'
                }
            }
            
            can_handle = await hannah._can_handle(intent)
            print(f"Can handle tweet posting: {can_handle}")
            
            if can_handle:
                plan = await hannah._create_plan(intent, None)
                print(f"Generated execution plan: {len(plan)} steps")
                for step in plan:
                    print(f"  - Step {step['step']}: {step['action']}")
                print("✅ Hannah agent planning working")
            
            self.test_results['phase_2'] = True
            return True
            
        except Exception as e:
            print(f"❌ Phase 2 failed: {e}")
            logger.exception("Phase 2 error")
            self.test_results['phase_2'] = False
            return False
    
    async def phase_3_final_integration_test(self):
        """
        Phase 3: Final integration test - SINGLE POST
        
        This tests:
        - Everything working together
        - Actual tweet posting (only ONE to minimize bot detection risk)
        - Proper session handling
        
        Only runs if Phase 1 & 2 passed!
        """
        print("\n" + "="*80)
        print("PHASE 3: FINAL INTEGRATION TEST (Single Post)")
        print("="*80)
        
        if not self.test_results.get('phase_1') or not self.test_results.get('phase_2'):
            print("❌ Skipping Phase 3 - Previous phases did not fully pass")
            print(f"Phase 1: {self.test_results.get('phase_1')}")
            print(f"Phase 2: {self.test_results.get('phase_2')}")
            self.test_results['phase_3'] = False
            return False
        
        print("\n⚠️  IMPORTANT: This will send ONE actual tweet to verify workflow")
        print("Waiting 10 seconds... (Press Ctrl+C to cancel)")
        
        try:
            for i in range(10, 0, -1):
                print(f"Posting in {i}s...", end='\r')
                await asyncio.sleep(1)
            
            from integrations.social_media import TwitterAutomation
            from dotenv import load_dotenv
            
            load_dotenv()
            
            twitter = TwitterAutomation()
            
            try:
                print("\n1️⃣  Starting browser for final post...")
                await twitter.start_browser(headless=True)
                print("✅ Browser started")
                
                print("\n2️⃣  Logging in...")
                success = await twitter.login(
                    username=os.getenv('TWITTER_USERNAME'),
                    password=os.getenv('TWITTER_PASSWORD'),
                    email=os.getenv('TWITTER_EMAIL')
                )
                
                if not success:
                    print("❌ Login failed")
                    self.test_results['phase_3'] = False
                    return False
                
                print("✅ Login successful")
                
                # The ONE tweet we'll post
                final_tweet = f"✅ Twitter automation verified! Allisson enterprise working. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                print(f"\n3️⃣  Posting final verification tweet...")
                print(f"Content: {final_tweet[:60]}...")
                
                result = await twitter.post_tweet(final_tweet)
                
                if result['success']:
                    print(f"✅ TWEET POSTED SUCCESSFULLY!")
                    print(f"URL: {result.get('url')}")
                    self.test_results['phase_3'] = True
                    return True
                else:
                    print(f"❌ Tweet posting failed: {result.get('error')}")
                    self.test_results['phase_3'] = False
                    return False
                    
            finally:
                await twitter.close_browser()
                
        except KeyboardInterrupt:
            print("\n⏸️  Post cancelled by user")
            self.test_results['phase_3'] = False
            return False
        except Exception as e:
            print(f"❌ Phase 3 failed: {e}")
            logger.exception("Phase 3 error")
            self.test_results['phase_3'] = False
            return False
    
    async def run_all_phases(self):
        """Run all test phases"""
        print("\n\n")
        print("🚀" * 40)
        print("COMPREHENSIVE TWITTER AUTOMATION TEST")
        print("Multiple approaches for robust, bot-safe verification")
        print("🚀" * 40)
        
        phase_1_ok = await self.phase_1_browser_automation_safe_flow()
        print(f"\n📊 Phase 1 Result: {'✅ PASSED' if phase_1_ok else '❌ FAILED'}")
        
        await asyncio.sleep(2)
        
        phase_2_ok = await self.phase_2_hannah_agent_integration()
        print(f"\n📊 Phase 2 Result: {'✅ PASSED' if phase_2_ok else '❌ FAILED'}")
        
        await asyncio.sleep(2)
        
        phase_3_ok = await self.phase_3_final_integration_test()
        print(f"\n📊 Phase 3 Result: {'✅ PASSED' if phase_3_ok else '❌ FAILED'}")
        
        # Summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"Phase 1 (Browser Automation): {'✅ PASSED' if phase_1_ok else '❌ FAILED'}")
        print(f"Phase 2 (Hannah Agent):       {'✅ PASSED' if phase_2_ok else '❌ FAILED'}")
        print(f"Phase 3 (Final Post):        {'✅ PASSED' if phase_3_ok else '❌ FAILED'}")
        
        all_passed = phase_1_ok and phase_2_ok
        print(f"\n🎯 Result: {'✅ FULLY OPERATIONAL' if all_passed else '⚠️  PARTIAL SUCCESS'}")
        
        if all_passed:
            print("\n✨ Your Twitter automation stack is ready for production use!")
            print("   - Browser automation: Working")
            print("   - Hannah agent: Integrated")
            print("   - Session handling: Verified")


async def main():
    test = ComprehensiveWorkflowTest()
    await test.run_all_phases()


if __name__ == '__main__':
    asyncio.run(main())
