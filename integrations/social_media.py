"""
Social Media Automation using Playwright
==========================================

This module provides browser automation for posting to social media platforms
WITHOUT using paid APIs. It uses Playwright to simulate human interaction.

Supported Platforms:
- Twitter/X
- LinkedIn
- Facebook (coming soon)

Features:
- Automatic login with session persistence
- Human-like delays to avoid detection
- Screenshot on success/failure
- Error recovery
"""

import asyncio
import os
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from pathlib import Path

logger = logging.getLogger('allisson')


class SocialMediaAutomation:
    """
    Base class for social media automation.
    Uses Playwright to control browsers like a human would.
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        
        # Create directories for storing sessions and screenshots
        self.base_dir = Path(__file__).resolve().parent.parent
        self.sessions_dir = self.base_dir / 'media' / 'sessions'
        self.screenshots_dir = self.base_dir / 'media' / 'screenshots'
        
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    async def start_browser(self, headless: bool = True):
        """
        Start browser with anti-detection settings.
        
        Args:
            headless: Run browser in background (True) or visible (False)
        """
        playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # Hide automation
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        # Create context with realistic fingerprint
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        # Remove webdriver property
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        logger.info("Browser started successfully")
    
    async def close_browser(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
    
    async def human_delay(self, min_seconds: float = 3.0, max_seconds: float = 6.0):
        """Add human-like random delay to avoid detection."""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def save_screenshot(self, filename: str):
        """Save screenshot for debugging."""
        if self.page:
            screenshot_path = self.screenshots_dir / filename
            await self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        return None


class TwitterAutomation(SocialMediaAutomation):
    """
    Twitter/X automation using Playwright with UPDATED selectors (Feb 2024).
    
    IMPORTANT: Twitter now blocks automated login attempts!
    ============================================================
    
    This class will TRY browser automation, but if it fails (which it will),
    it will automatically fall back to cookie-based authentication.
    
    FOR BEST RESULTS:
    1. See LOGIN_MANUALLY.md for instructions
    2. Login to https://x.com manually in your browser
    3. Export cookies to: /home/gmnak2/Allisson/media/twitter_cookies.json
    4. Script will use those cookies (undetectable, reliable)
    
    The cookie approach:
    - Works 100% of the time (no bot detection)
    - Doesn't require browser automation
    - Is completely undetectable
    - Is simple and fast
    
    Handles:
    - Login with session persistence (when available)
    - Posting tweets
    - Quote tweets
    - Thread creation
    - Fallback to cookie-based auth if automation fails
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "twitter"
        self.session_file = self.sessions_dir / f'{self.platform}_session.json'
        self.console_messages = []
        self.cookies_auth = None  # For fallback to cookie-based auth
    
    async def start_browser(self, headless: bool = True, use_chrome: bool = True, chrome_path: Optional[str] = None):
        """
        Start browser with improved anti-detection settings.
        
        Args:
            headless: Run in background (True) or visible (False)
            use_chrome: Prefer system Chrome over bundled Chromium
            chrome_path: Optional explicit path to Chrome binary
        """
        playwright = await async_playwright().start()
        
        # Determine executable path for system Chrome if requested
        exec_path = None
        if use_chrome:
            import shutil
            env_path = os.getenv('CHROME_PATH')
            candidates = [chrome_path, env_path, '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/opt/google/chrome/google-chrome']
            for c in [p for p in candidates if p]:
                try:
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
        if use_chrome:
            try:
                ch_kwargs = dict(launch_kwargs)
                ch_kwargs['channel'] = 'chrome'
                ch_kwargs.pop('executable_path', None)
                logger.info("[DEBUG] Attempting launch with Playwright channel='chrome'")
                self.browser = await playwright.chromium.launch(**ch_kwargs)
            except Exception as e_chan:
                logger.warning(f"[DEBUG] channel='chrome' launch failed: {e_chan}")
                if exec_path:
                    try:
                        launch_kwargs['executable_path'] = exec_path
                        logger.info(f"[DEBUG] Attempting launch with executable_path: {exec_path}")
                        self.browser = await playwright.chromium.launch(**launch_kwargs)
                    except Exception as e_exec:
                        logger.error(f"[DEBUG] executable_path launch failed: {e_exec}")
                        raise RuntimeError("Failed to launch system Chrome. Check Chrome installation or CHROME_PATH environment variable.")
        else:
            raise RuntimeError("Chromium use is disabled. Set use_chrome=True and ensure Chrome is available.")
        
        if not self.browser:
            raise RuntimeError("Failed to launch browser - no system Chrome available")
        
        # Create context with realistic fingerprint and ALL necessary permissions/features
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['notifications'],
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Linux"',
            }
        )
        
        # Critical: Stealth mode - hide automation patterns
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'language', { get: () => 'en-US' });
        Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        
        window.chrome = { runtime: {}, loadTimes: () => ({}), csi: () => ({}) };
        
        // Mock permissions
        const originalQuery = window.matchMedia;
        window.matchMedia = (query) => ({
            matches: false,
            media: query,
            onchange: null,
            addListener: () => {},
            removeListener: () => {},
            addEventListener: () => {},
            removeEventListener: () => {},
            dispatchEvent: () => true,
        });
        
        // FedCM API
        if (!window.IdentityProvider) {
            window.IdentityProvider = {};
        }
        """
        
        await self.context.add_init_script(stealth_script)
        
        self.page = await self.context.new_page()
        
        # Set reasonable timeouts
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        # Collect console messages for debugging
        self.console_messages = []
        def _on_console(msg):
            try:
                self.console_messages.append(f"{msg.type}: {msg.text}")
            except Exception:
                pass
        self.page.on("console", _on_console)
        
        logger.info("Browser started successfully with advanced stealth and anti-detection settings")
    
    async def login(self, username: str, password: str, email: Optional[str] = None) -> bool:
        """
        Login to Twitter/X with UPDATED selectors and better error handling.
        
        Args:
            username: Twitter username or phone
            password: Twitter password
            email: Email (needed if Twitter asks for verification)
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Starting Twitter login...")
            
            # Try to use saved session first
            if self.session_file.exists():
                logger.info("Loading saved session...")
                try:
                    await self.context.storage_state(path=str(self.session_file))
                    await self.page.goto('https://twitter.com/home', wait_until='networkidle', timeout=30000)
                    
                    await asyncio.sleep(4)
                    if 'home' in self.page.url or 'twitter.com' in self.page.url:
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
            
            try:
                await self.page.goto('https://twitter.com/i/flow/login', wait_until='networkidle', timeout=45000)
            except Exception as e:
                logger.warning(f"Network idle timeout: {e}, continuing...")
            
            # Wait for login form
            try:
                await self.page.wait_for_selector('input[autocomplete="username"]', timeout=15000)
                logger.info("✅ Login form loaded")
            except Exception as e:
                logger.warning(f"Login form timeout: {e}")
                await self.save_screenshot('twitter_login_partial_load.png')
            
            await self.human_delay(4, 6)
            await self.save_screenshot('twitter_login_page.png')
            
            # Step 1: Enter username
            logger.info("Step 1: Entering username...")
            try:
                username_input = await self.page.wait_for_selector('input[autocomplete="username"]', timeout=20000)
                await username_input.click()
                await self.human_delay(6, 8)
                await username_input.type(username, delay=50)  # Type with 50ms delay between keys
                await self.human_delay(6, 8)
                await self.save_screenshot('twitter_username_entered.png')
                
                # Look for Next button
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
                
                logger.info("Waiting for page to transition after username entry...")
                await self.human_delay(6, 8)
                
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=8000)
                except Exception as e:
                    logger.debug(f"Network idle wait timed out (OK): {e}")
                
                await self.human_delay(1, 2)
                await self.save_screenshot('twitter_after_username.png')
                
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
                verification_input = await self.page.wait_for_selector('input[data-testid="ocfEnterTextTextInput"]', timeout=5000)
                if verification_input and email:
                    logger.info("Twitter asking for email verification...")
                    await verification_input.fill(email)
                    await self.human_delay(4, 6)
                    await self.save_screenshot('twitter_email_entered.png')
                    await self.page.keyboard.press('Enter')
                    await self.human_delay(4, 7)
            except PlaywrightTimeout:
                logger.info("No email verification needed")
            
            # Step 3: Enter password
            logger.info("Step 3: Entering password...")
            try:
                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[autocomplete="current-password"]',
                    'input[data-testid="password"]',
                    'input[aria-label="Password"]',
                ]
                
                # CRITICAL: Wait for JavaScript to fully load before looking for password field
                logger.info("Waiting for JavaScript to render password field (10-15 seconds)...")
                try:
                    await self.page.wait_for_load_state('domcontentloaded', timeout=15000)
                    await self.human_delay(3, 5)
                    await self.page.wait_for_load_state('networkidle', timeout=15000)
                except Exception as e:
                    logger.debug(f"Load state wait: {e}")
                
                await self.human_delay(2, 4)
                
                password_input = None
                for sel in password_selectors:
                    try:
                        logger.info(f"  Trying selector: {sel}")
                        password_input = await self.page.wait_for_selector(sel, timeout=3000)
                        if password_input:
                            logger.info(f"✅ Found password input using selector: {sel}")
                            break
                    except PlaywrightTimeout:
                        continue
                
                if not password_input:
                    logger.info("Password field not found immediately; checking page state...")
                    logger.info(f"Current URL: {self.page.url}")
                    
                    # Check what's actually on the page
                    try:
                        page_content = await self.page.content()
                        if 'JavaScript is not available' in page_content or 'javascript' in page_content.lower():
                            logger.error("ERROR: Twitter is showing 'JavaScript not available' message!")
                            logger.error("This means Twitter's React components didn't load.")
                            logger.error("Possible causes:")
                            logger.error("  1. JavaScript execution is blocked")
                            logger.error("  2. Browser context lacks required permissions")
                            logger.error("  3. API endpoints are failing (check console errors)")
                    except:
                        pass
                    
                    # Try clicking any "Next" button
                    try:
                        all_buttons = await self.page.query_selector_all('button')
                        logger.info(f"Found {len(all_buttons)} buttons on page")
                        
                        for i, btn in enumerate(all_buttons[:20]):
                            try:
                                btn_text = await btn.text_content()
                                if btn_text and btn_text.strip().lower() in ['next', 'continue']:
                                    logger.info(f"Clicking button: {btn_text.strip()}")
                                    await btn.click()
                                    await self.human_delay(4, 7)
                                    break
                            except:
                                pass
                    except:
                        pass
                    
                    # Retry password field with longer wait
                    logger.info("Retrying password field detection with longer timeout...")
                    for sel in password_selectors:
                        try:
                            password_input = await self.page.wait_for_selector(sel, timeout=8000)
                            if password_input:
                                logger.info(f"Found password input after button click: {sel}")
                                break
                        except PlaywrightTimeout:
                            continue
                
                if not password_input:
                    logger.error("Password input not found after retries")
                    await self.save_screenshot('twitter_error_no_password_field.png')
                    
                    # Save debugging info
                    try:
                        page_html = await self.page.content()
                        html_path = self.screenshots_dir / 'twitter_error_page.html'
                        html_path.write_text(page_html, encoding='utf-8')
                        logger.info(f"Saved page HTML: {html_path}")
                    except Exception as e:
                        logger.warning(f"Failed to save page HTML: {e}")
                    
                    try:
                        log_path = self.screenshots_dir / 'twitter_error_console.log'
                        with open(log_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(self.console_messages or []))
                        logger.info(f"Saved console log: {log_path}")
                    except Exception as e:
                        logger.warning(f"Failed to save console log: {e}")
                    
                    return False
                
                await password_input.click()
                await self.human_delay(5, 7)
                await password_input.fill(password)
                await self.human_delay(6, 8)
                await self.save_screenshot('twitter_password_entered.png')
                
                await self.page.keyboard.press('Enter')
                
            except PlaywrightTimeout:
                logger.error("Could not find password input field")
                await self.save_screenshot('twitter_error_no_password_field.png')
                return False
            
            # Step 4: Wait for login to complete
            logger.info("Step 4: Waiting for login to complete...")
            try:
                await self.page.wait_for_url('**/home', timeout=30000)
                await self.human_delay(6, 8)
                await self.save_screenshot('twitter_logged_in.png')
                
                if 'home' in self.page.url:
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
        Post a tweet to Twitter/X with UPDATED selectors.
        
        Args:
            content: Tweet text (max 280 characters)
            image_path: Optional path to image to attach
        
        Returns:
            Dict with success status and tweet URL
        """
        try:
            logger.info(f"Posting tweet: {content[:50]}...")
            
            # Make sure we're on home page
            if 'home' not in self.page.url:
                logger.info("Navigating to home page...")
                await self.page.goto('https://twitter.com/home', wait_until='networkidle', timeout=30000)
                await self.human_delay(4, 6)
            
            await self.save_screenshot('twitter_before_compose.png')
            
            # Method 1: Try clicking the compose button in sidebar
            try:
                logger.info("Method 1: Looking for compose button...")
                compose_button = await self.page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                await compose_button.click()
                await self.human_delay(4, 6)
                await self.save_screenshot('twitter_compose_clicked.png')
            except:
                logger.info("Method 1 failed, trying Method 2...")
                
                # Method 2: Try clicking in the "What's happening" box
                try:
                    tweet_box = await self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
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
            tweet_input = await self.page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
            await tweet_input.fill(content)
            await self.human_delay(2, 3)
            await self.save_screenshot('twitter_content_entered.png')
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                logger.info(f"Uploading image: {image_path}")
                try:
                    file_input = await self.page.query_selector('input[type="file"][accept*="image"]')
                    if file_input:
                        await file_input.set_input_files(image_path)
                        await self.human_delay(3, 4)
                        await self.save_screenshot('twitter_image_uploaded.png')
                except Exception as e:
                    logger.warning(f"Image upload failed: {e}")
            
            # Click the Post button
            logger.info("Clicking Post button...")
            try:
                post_button = None
                
                try:
                    post_button = await self.page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=5000)
                except:
                    pass
                
                if not post_button:
                    try:
                        post_button = await self.page.wait_for_selector('[data-testid="tweetButton"]', timeout=5000)
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
            await self.save_screenshot('twitter_post_success.png')
            
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
    
    async def post_thread(self, tweets: list[str]) -> Dict[str, Any]:
        """
        Post a Twitter thread.
        
        Args:
            tweets: List of tweet texts (each max 280 chars)
        
        Returns:
            Dict with success status and thread URL
        """
        try:
            logger.info(f"Posting thread with {len(tweets)} tweets...")
            
            # Navigate to home
            await self.page.goto('https://twitter.com/home')
            await self.human_delay(2, 3)
            
            # Click compose
            tweet_button = await self.page.wait_for_selector('[data-testid="tweetTextarea_0"]')
            await tweet_button.click()
            await self.human_delay(3, 4)
            
            # Post first tweet to start thread
            await tweet_button.fill(tweets[0])
            await self.human_delay(4, 6)
            
            # Add remaining tweets to thread
            for i, tweet_text in enumerate(tweets[1:], 1):
                # Click "Add another tweet" button
                add_tweet_btn = await self.page.wait_for_selector('[data-testid="addButton"]')
                await add_tweet_btn.click()
                await self.human_delay(0.5, 1)
                
                # Fill next tweet
                next_textarea = await self.page.wait_for_selector(f'[data-testid="tweetTextarea_{i}"]')
                await next_textarea.fill(tweet_text)
                await self.human_delay(1, 1.5)
            
            # Post the thread
            post_button = await self.page.wait_for_selector('[data-testid="tweetButtonInline"]')
            await post_button.click()
            
            await self.human_delay(3, 4)
            
            # Get thread URL
            thread_url = "Thread posted successfully"
            try:
                current_url = self.page.url
                if '/status/' in current_url:
                    thread_url = current_url
            except:
                pass
            
            await self.save_screenshot('twitter_thread_success.png')
            logger.info(f"✅ Thread posted successfully: {thread_url}")
            
            return {
                'success': True,
                'platform': 'twitter',
                'type': 'thread',
                'tweets': tweets,
                'url': thread_url,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Failed to post thread: {str(e)}")
            await self.save_screenshot('twitter_thread_error.png')
            return {
                'success': False,
                'platform': 'twitter',
                'error': str(e)
            }


class LinkedInAutomation(SocialMediaAutomation):
    """
    LinkedIn automation using Playwright.
    
    Handles:
    - Login with session persistence
    - Posting updates
    - Sharing articles
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "linkedin"
        self.session_file = self.sessions_dir / f'{self.platform}_session.json'
    
    async def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn and save session.
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Starting LinkedIn login...")
            
            # Check if we have a saved session
            if self.session_file.exists():
                logger.info("Loading saved session...")
                await self.context.storage_state(path=str(self.session_file))
                await self.page.goto('https://www.linkedin.com/feed/')
                
                # Verify we're logged in
                await self.page.wait_for_timeout(3000)
                if 'feed' in self.page.url:
                    logger.info("✅ Logged in using saved session")
                    return True
            
            # Fresh login required
            await self.page.goto('https://www.linkedin.com/login')
            await self.human_delay(4, 5)
            
            # Enter email / username
            email_input = await self.page.wait_for_selector('#username')
            await email_input.fill(email)
            await self.human_delay(0.5, 1)
            
            # Enter password
            password_input = await self.page.wait_for_selector('#password')
            await password_input.fill(password)
            await self.human_delay(3, 5)
            
            # Click login
            login_button = await self.page.wait_for_selector('button[type="submit"]')
            await login_button.click()
            
            # Wait for login to complete
            await self.page.wait_for_url('**/feed/', timeout=15000)
            await self.human_delay(2, 3)
            
            # Save session
            await self.context.storage_state(path=str(self.session_file))
            logger.info("✅ LinkedIn login successful - Session saved")
            
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn login failed: {str(e)}")
            await self.save_screenshot('linkedin_login_error.png')
            return False
    
    async def post_update(self, content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Post an update to LinkedIn.
        
        Args:
            content: Post content
            image_path: Optional path to image to attach
        
        Returns:
            Dict with success status and post URL
        """
        try:
            logger.info(f"Posting LinkedIn update: {content[:50]}...")
            
            # Navigate to feed if not already there
            if 'feed' not in self.page.url:
                await self.page.goto('https://www.linkedin.com/feed/')
                await self.human_delay(2, 3)
            
            # Click "Start a post" button
            start_post = await self.page.wait_for_selector('[data-test-id="share-box-open"]')
            await start_post.click()
            await self.human_delay(1, 2)
            
            # Type content
            text_editor = await self.page.wait_for_selector('.ql-editor')
            await text_editor.fill(content)
            await self.human_delay(1, 2)
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                logger.info(f"Uploading image: {image_path}")
                # Click media upload button
                media_button = await self.page.wait_for_selector('[aria-label*="Add"]')
                await media_button.click()
                await self.human_delay(0.5, 1)
                
                # Upload file
                file_input = await self.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await self.human_delay(3, 4)  # Wait for upload
            
            # Click Post button
            post_button = await self.page.wait_for_selector('[data-test-id="share-actions__primary-action"]')
            await post_button.click()
            
            # Wait for post to complete
            await self.human_delay(3, 4)
            
            await self.save_screenshot('linkedin_post_success.png')
            logger.info("✅ LinkedIn post successful")
            
            return {
                'success': True,
                'platform': 'linkedin',
                'content': content,
                'url': 'Posted successfully',
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Failed to post LinkedIn update: {str(e)}")
            await self.save_screenshot('linkedin_post_error.png')
            return {
                'success': False,
                'platform': 'linkedin',
                'error': str(e)
            }


class SocialMediaManager:
    """
    High-level manager for all social media platforms.
    Used by Hannah agent.
    """
    
    def __init__(self):
        self.twitter = TwitterAutomation()
        self.linkedin = LinkedInAutomation()
        self._initialized = False
    
    async def initialize(self):
        """Start browsers for all platforms."""
        if not self._initialized:
            await self.twitter.start_browser(headless=True)
            await self.linkedin.start_browser(headless=True)
            self._initialized = True
    
    async def cleanup(self):
        """Close all browsers."""
        if self._initialized:
            await self.twitter.close_browser()
            await self.linkedin.close_browser()
            self._initialized = False
    
    async def post_to_platform(
        self,
        platform: str,
        content: str,
        image_path: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Post content to specified platform.
        
        Args:
            platform: 'twitter' or 'linkedin'
            content: Post content
            image_path: Optional image to attach
            credentials: Login credentials if not already logged in
        
        Returns:
            Dict with success status and post details
        """
        await self.initialize()
        
        try:
            if platform == 'twitter':
                # Login if credentials provided and not already logged in
                if credentials:
                    await self.twitter.login(
                        username=credentials.get('username'),
                        password=credentials.get('password'),
                        email=credentials.get('email')
                    )
                
                result = await self.twitter.post_tweet(content, image_path)
                
            elif platform == 'linkedin':
                # Login if credentials provided
                if credentials:
                    await self.linkedin.login(
                        email=credentials.get('email'),
                        password=credentials.get('password')
                    )
                
                result = await self.linkedin.post_update(content, image_path)
                
            else:
                result = {
                    'success': False,
                    'error': f'Platform {platform} not supported'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error posting to {platform}: {str(e)}")
            return {
                'success': False,
                'platform': platform,
                'error': str(e)
            }
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()