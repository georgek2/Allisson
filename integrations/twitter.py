"""
FIXED Twitter Automation with Updated Selectors (2024)
=======================================================

Twitter frequently updates their HTML, so selectors need periodic updates.
This version has more robust selectors and better error handling.
"""

import asyncio
import os
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from pathlib import Path

logger = logging.getLogger('allisson')


class TwitterAutomationFixed:
    """
    Updated Twitter/X automation with current selectors (Feb 2024).
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self.platform = "twitter"
        
        # Directories
        base_dir = Path(__file__).resolve().parent.parent
        self.sessions_dir = base_dir / 'media' / 'sessions'
        self.screenshots_dir = base_dir / 'media' / 'screenshots'
        
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.sessions_dir / f'{self.platform}_session.json'
        self.console_messages = []
    
    async def start_browser(self, headless: bool = False, use_chrome: bool = True, chrome_path: Optional[str] = None):
        """Start browser - default to VISIBLE mode for debugging.

        If `use_chrome` is True, attempt to launch the system Chrome/Chromium binary.
        You can also pass an explicit `chrome_path` or set the `CHROME_PATH` env var.
        """
        playwright = await async_playwright().start()

        # Determine executable path for system Chrome if requested
        exec_path = None
        if use_chrome:
            import shutil
            # Use provided chrome_path, environment variable, or try common locations
            # Prioritize Google Chrome only; exclude plain Chromium
            env_path = os.getenv('CHROME_PATH')
            candidates = [chrome_path, env_path, '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/opt/google/chrome/google-chrome']
            for c in [p for p in candidates if p]:
                try:
                    # shutil.which works for names in PATH; os.path.exists checks full paths
                    if shutil.which(c) or os.path.exists(c):
                        exec_path = c
                        break
                except Exception:
                    continue

        launch_kwargs = dict(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )

        # Prefer Playwright channel='chrome' when requesting system Chrome
        last_exc = None
        if use_chrome:
            # Try channel launch first (more compatible with Playwright)
            try:
                ch_kwargs = dict(launch_kwargs)
                ch_kwargs['channel'] = 'chrome'
                # channel should not include executable_path
                ch_kwargs.pop('executable_path', None)
                print(f"[DEBUG] Attempting launch with Playwright channel='chrome' (no executable_path)")
                self.browser = await playwright.chromium.launch(**ch_kwargs)
            except Exception as e_chan:
                last_exc = e_chan
                print(f"[DEBUG] channel='chrome' launch failed: {e_chan}")
                # If exec_path was resolved, try launching directly with it
                if exec_path:
                    try:
                        launch_kwargs['executable_path'] = exec_path
                        print(f"[DEBUG] Attempting launch with executable_path: {exec_path}")
                        self.browser = await playwright.chromium.launch(**launch_kwargs)
                    except Exception as e_exec:
                        last_exc = e_exec
                        print(f"[DEBUG] executable_path launch failed: {e_exec}")
                # Do NOT fall back to bundled Chromium: fail explicitly so the user fixes Chrome setup
                if not getattr(self, 'browser', None):
                    print("[DEBUG] No system Chrome available and bundled Chromium fallback disabled")
        else:
            # Script configured to NOT use system Chrome; we require explicit system Chrome only
            raise RuntimeError("Chromium use is disabled in this script. Set use_chrome=True and ensure CHROME_PATH or Playwright channel='chrome' is available.")

        # Print debug info to console so it's visible even if logging not configured
        import sys as _sys
        print(f"[DEBUG] python executable: {_sys.executable}")
        print(f"[DEBUG] CHROME_PATH env: {os.getenv('CHROME_PATH')}")
        print(f"[DEBUG] resolved exec_path: {exec_path}")
        print(f"[DEBUG] launch kwargs (no args): { {k:v for k,v in launch_kwargs.items() if k!='args'} }")

        if not getattr(self, 'browser', None):
            # Nothing started
            raise RuntimeError(
                "Failed to launch system Chrome. Ensure Google Chrome/Chromium is installed, CHROME_PATH is set to the binary path, or Playwright's 'chrome' channel is available."
            )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        ua = None
        try:
            ua = await self.page.evaluate("() => navigator.userAgent")
        except Exception:
            pass
        print(f"[DEBUG] Browser started. navigator.userAgent: {ua}")
        logger.info("Browser started successfully")
        # Collect console messages for debugging
        try:
            self.console_messages = []
            def _on_console(msg):
                try:
                    self.console_messages.append(f"{msg.type}: {msg.text}")
                except Exception:
                    pass
            self.page.on("console", _on_console)
        except Exception:
            pass
    
    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
    
    async def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        import random
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def save_screenshot(self, filename: str):
        if self.page:
            screenshot_path = self.screenshots_dir / filename
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        return None
    
    async def login(self, username: str, password: str, email: Optional[str] = None) -> bool:
        """
        Login to Twitter with UPDATED selectors and better error handling.
        """
        try:
            logger.info("Starting Twitter login...")
            
            # Try to use saved session first
            if self.session_file.exists():
                logger.info("Loading saved session...")
                try:
                    await self.context.storage_state(path=str(self.session_file))
                    await self.page.goto('https://twitter.com/home', wait_until='networkidle', timeout=30000)
                    
                    # Check if we're actually logged in
                    await asyncio.sleep(4)
                    if 'home' in self.page.url or 'twitter.com' in self.page.url:
                        # Verify by looking for compose button
                        try:
                            await self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
                            logger.info("✅ Logged in using saved session")
                            return True
                        except:
                            logger.info("Session expired, will login fresh")
                except Exception as e:
                    logger.info(f"Session load failed: {e}, will login fresh")
            
            # Fresh login required
            logger.info("Starting fresh login...")
            
            # Navigate to login page with reasonable timeout
            logger.info("Navigating to Twitter login...")
            try:
                await self.page.goto('https://twitter.com/i/flow/login', wait_until='networkidle', timeout=45000)
            except Exception as e:
                logger.warning(f"Network idle timeout: {e}, continuing with page in current state...")
            
            # Wait for username input to appear - using selector only (no eval due to CSP)
            logger.info("Waiting for login form to load...")
            try:
                await self.page.wait_for_selector('input[autocomplete="username"]', timeout=15000)
                logger.info("✅ Login form loaded")
            except Exception as e:
                logger.warning(f"Login form timeout: {e}, attempting to continue...")
                # Take screenshot to see what's on the page
                await self.save_screenshot('twitter_01_partial_load.png')
            
            await self.human_delay(1, 2)
            await self.save_screenshot('twitter_01_login_page.png')
            
            # Step 1: Enter username/email/phone
            logger.info("Step 1: Entering username...")
            try:
                # Wait for input field - Twitter uses different selectors
                username_input = await self.page.wait_for_selector(
                    'input[autocomplete="username"]',
                    timeout=20000
                )
                await username_input.click()
                await self.human_delay(0.5, 1)
                await username_input.type(username, delay=50)  # Type with 50ms delay between keys
                await self.human_delay(1, 2)
                await self.save_screenshot('twitter_02_username_entered.png')
                
                # Look for Next button with aria-label
                logger.info("Looking for Next button...")
                next_button = None
                buttons = await self.page.query_selector_all('button')
                for btn in buttons:
                    try:
                        aria_label = await btn.get_attribute('aria-label')
                        if aria_label and 'next' in aria_label.lower():
                            logger.info(f"Found Next button with aria-label: {aria_label}")
                            next_button = btn
                            break
                    except:
                        pass
                
                if next_button:
                    await next_button.click()
                    logger.info("Clicked Next button")
                else:
                    logger.info("No Next button found, pressing Enter...")
                    await self.page.keyboard.press('Enter')
                
                # Wait for page to transition after clicking Next
                logger.info("Waiting for page to transition after username entry...")
                await self.human_delay(3, 4)
                
                # Wait for either password field OR url change
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=8000)
                except Exception as e:
                    logger.debug(f"Network idle wait timed out (OK): {e}")
                
                await self.human_delay(1, 2)
                await self.save_screenshot('twitter_03_after_username.png')
                
            except PlaywrightTimeout:
                logger.error("Could not find username input field")
                await self.save_screenshot('twitter_error_no_username_field.png')
                return False
            except Exception as e:
                logger.error(f"Error in username entry: {e}")
                await self.save_screenshot('twitter_error_username_entry.png')
                return False
            
            # Step 2: Check if Twitter asks for email/phone verification
            logger.info("Step 2: Checking for verification...")
            try:
                # Twitter sometimes asks "Enter your phone number or email"
                verification_input = await self.page.wait_for_selector(
                    'input[data-testid="ocfEnterTextTextInput"]',
                    timeout=5000
                )
                if verification_input and email:
                    logger.info("Twitter asking for email verification...")
                    await verification_input.fill(email)
                    await self.human_delay(1, 2)
                    await self.save_screenshot('twitter_04_email_entered.png')
                    await self.page.keyboard.press('Enter')
                    await self.human_delay(3, 5)
            except PlaywrightTimeout:
                logger.info("No email verification needed")
                pass
            
            # Step 3: Enter password
            logger.info("Step 3: Entering password...")
            try:
                # Try multiple common selectors for the password field (broader search)
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[autocomplete="current-password"]',
                    'input[data-testid="password"]',
                    'input[aria-label="Password"]',
                    'input[aria-label*="password" i]',
                    'input[placeholder*="password" i]',
                    'input[id*="password" i]',
                ]

                password_input = None
                for sel in password_selectors:
                    try:
                        logger.info(f"  Trying selector: {sel}")
                        password_input = await self.page.wait_for_selector(sel, timeout=2000)
                        if password_input:
                            logger.info(f"✅ Found password input using selector: {sel}")
                            break
                    except PlaywrightTimeout:
                        continue
                    except Exception as e:
                        logger.debug(f"  Selector failed: {e}")
                        continue

                # If password field still not found, try clicking any visible "Next"/"Log in" button and retry
                if not password_input:
                    logger.info("Password field not found immediately; checking page state...")
                    
                    # Log current URL and page details
                    logger.info(f"Current URL: {self.page.url}")
                    
                    # Try to find and click "Next" button using text content
                    try:
                        all_buttons = await self.page.query_selector_all('button')
                        logger.info(f"Found {len(all_buttons)} buttons on page")
                        
                        for i, btn in enumerate(all_buttons[:20]):  # Check first 20 buttons
                            try:
                                btn_text = await btn.text_content()
                                if btn_text:
                                    logger.debug(f"  Button {i}: '{btn_text.strip()}'")
                                    if btn_text.strip().lower() in ['next', 'continue']:
                                        logger.info(f"Clicking button with text: {btn_text.strip()}")
                                        await btn.click()
                                        await self.human_delay(3, 5)
                                        break
                            except Exception as e_btn:
                                logger.debug(f"Error checking button {i}: {e_btn}")
                    except Exception as e:
                        logger.debug(f"Error finding buttons: {e}")

                    # After attempting Next, retry finding the password field with longer timeout
                    logger.info("Retrying password field detection after button click...")
                    for sel in password_selectors:
                        try:
                            password_input = await self.page.wait_for_selector(sel, timeout=5000)
                            if password_input:
                                logger.info(f"Found password input after clicking button using selector: {sel}")
                                break
                        except PlaywrightTimeout:
                            continue

                if not password_input:
                    logger.error("Password input not found after retries")
                    await self.save_screenshot('twitter_error_no_password_field.png')
                    # Save full page HTML for debugging
                    try:
                        page_html = await self.page.content()
                        html_path = self.screenshots_dir / 'twitter_error_page.html'
                        html_path.write_text(page_html, encoding='utf-8')
                        logger.info(f"Saved page HTML: {html_path}")
                    except Exception as e_html:
                        logger.warning(f"Failed to save page HTML: {e_html}")

                    # Save console messages
                    try:
                        log_path = self.screenshots_dir / 'twitter_error_console.log'
                        with open(log_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(self.console_messages or []))
                        logger.info(f"Saved console log: {log_path}")
                    except Exception as e_log:
                        logger.warning(f"Failed to save console log: {e_log}")

                    print(f"[DEBUG] Saved debugging files: {html_path} {log_path}")
                    return False

                await password_input.click()
                await self.human_delay(0.5, 1)
                await password_input.fill(password)
                await self.human_delay(1, 2)
                await self.save_screenshot('twitter_05_password_entered.png')

                # Click login or press Enter
                await self.page.keyboard.press('Enter')
                
            except PlaywrightTimeout:
                logger.error("Could not find password input field")
                await self.save_screenshot('twitter_error_no_password_field.png')
                return False
            
            # Step 4: Wait for login to complete
            logger.info("Step 4: Waiting for login to complete...")
            try:
                # Wait for home page URL
                await self.page.wait_for_url('**/home', timeout=30000)
                await self.human_delay(3, 5)
                await self.save_screenshot('twitter_06_logged_in.png')
                
                # Verify we're actually on home page
                if 'home' in self.page.url:
                    # Save session for future use
                    await self.context.storage_state(path=str(self.session_file))
                    logger.info("✅ Twitter login successful - Session saved")
                    return True
                else:
                    logger.error("Login completed but not on home page")
                    await self.save_screenshot('twitter_error_wrong_page.png')
                    return False
                    
            except PlaywrightTimeout:
                logger.error("Timeout waiting for home page")
                await self.save_screenshot('twitter_error_login_timeout.png')
                return False
            
        except Exception as e:
            logger.error(f"Twitter login failed: {str(e)}")
            await self.save_screenshot('twitter_login_error.png')
            return False
    
    async def post_tweet(self, content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a tweet with UPDATED selectors.
        """
        try:
            logger.info(f"Posting tweet: {content[:50]}...")
            
            # Make sure we're on home page
            if 'home' not in self.page.url:
                logger.info("Navigating to home page...")
                await self.page.goto('https://twitter.com/home', wait_until='networkidle', timeout=30000)
                await self.human_delay(2, 3)
            
            await self.save_screenshot('twitter_07_before_compose.png')
            
            # Method 1: Try clicking the compose button in sidebar
            try:
                logger.info("Method 1: Looking for compose button...")
                compose_button = await self.page.wait_for_selector(
                    '[data-testid="SideNav_NewTweet_Button"]',
                    timeout=10000
                )
                await compose_button.click()
                await self.human_delay(2, 3)
                await self.save_screenshot('twitter_08_compose_clicked.png')
            except:
                logger.info("Method 1 failed, trying Method 2...")
                
                # Method 2: Try clicking in the "What's happening" box
                try:
                    tweet_box = await self.page.wait_for_selector(
                        '[data-testid="tweetTextarea_0"]',
                        timeout=10000
                    )
                    await tweet_box.click()
                    await self.human_delay(1, 2)
                except:
                    logger.error("Could not find tweet compose area")
                    await self.save_screenshot('twitter_error_no_compose.png')
                    return {
                        'success': False,
                        'platform': 'twitter',
                        'error': 'Could not find tweet compose area'
                    }
            
            # Type the tweet content
            logger.info("Typing tweet content...")
            tweet_input = await self.page.wait_for_selector(
                '[data-testid="tweetTextarea_0"]',
                timeout=15000
            )
            await tweet_input.fill(content)
            await self.human_delay(2, 3)
            await self.save_screenshot('twitter_09_content_entered.png')
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                logger.info(f"Uploading image: {image_path}")
                try:
                    file_input = await self.page.query_selector('input[type="file"][accept*="image"]')
                    if file_input:
                        await file_input.set_input_files(image_path)
                        await self.human_delay(3, 4)
                        await self.save_screenshot('twitter_10_image_uploaded.png')
                except Exception as e:
                    logger.warning(f"Image upload failed: {e}")
            
            # Click the Post button
            logger.info("Clicking Post button...")
            try:
                # Try multiple possible selectors for the post button
                post_button = None
                
                # Try selector 1
                try:
                    post_button = await self.page.wait_for_selector(
                        '[data-testid="tweetButtonInline"]',
                        timeout=5000
                    )
                except:
                    pass
                
                # Try selector 2 if first failed
                if not post_button:
                    try:
                        post_button = await self.page.wait_for_selector(
                            '[data-testid="tweetButton"]',
                            timeout=5000
                        )
                    except:
                        pass
                
                if not post_button:
                    logger.error("Could not find Post button")
                    await self.save_screenshot('twitter_error_no_post_button.png')
                    return {
                        'success': False,
                        'platform': 'twitter',
                        'error': 'Could not find Post button'
                    }
                
                await post_button.click()
                logger.info("Post button clicked!")
                
            except Exception as e:
                logger.error(f"Error clicking post button: {e}")
                await self.save_screenshot('twitter_error_post_click.png')
                return {
                    'success': False,
                    'platform': 'twitter',
                    'error': f'Error clicking post: {str(e)}'
                }
            
            # Wait for post to complete
            await self.human_delay(4, 6)
            await self.save_screenshot('twitter_11_post_success.png')
            
            # Try to get tweet URL
            tweet_url = "Posted successfully"
            try:
                current_url = self.page.url
                if '/status/' in current_url:
                    tweet_url = current_url
            except:
                pass
            
            logger.info(f"✅ Tweet posted successfully: {tweet_url}")
            
            return {
                'success': True,
                'platform': 'twitter',
                'content': content,
                'url': tweet_url,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            await self.save_screenshot('twitter_post_error.png')
            return {
                'success': False,
                'platform': 'twitter',
                'error': str(e)
            }


# Quick test function
async def test_twitter_post():
    """Test the fixed Twitter automation"""
    
    print("\n" + "=" * 70)
    print("🧪 Testing Fixed Twitter Automation")
    print("=" * 70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    twitter = TwitterAutomationFixed()
    
    try:
        # Start in VISUAL mode so you can see what's happening (require system Chrome)
        await twitter.start_browser(headless=False, use_chrome=True)
    
        # Login
        print("\n📝 Logging in...")
        success = await twitter.login(
            username=os.getenv('TWITTER_USERNAME'),
            password=os.getenv('TWITTER_PASSWORD'),
            email=os.getenv('TWITTER_EMAIL')
        )
        
        if not success:
            print("❌ Login failed - check screenshots in media/screenshots/")
            return
        
        print("✅ Login successful!")
        
        # Post tweet
        print("\n📱 Posting tweet...")
        result = await twitter.post_tweet(
            "AI is revolutionizing software development! From intelligent code completion to automated testing, the future is here. 🚀 #AI #SoftwareDevelopment #Tech"
        )
        
        if result['success']:
            print(f"✅ Tweet posted!")
            print(f"   URL: {result['url']}")
        else:
            print(f"❌ Posting failed: {result.get('error')}")
        
        # Wait so you can see the result
        print("\n⏳ Waiting 10 seconds so you can see the result...")
        await asyncio.sleep(10)
    
    finally:
        await twitter.close_browser()
    
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_twitter_post())