"""
Twitter/X Automation using Session Cookies
===========================================

This module provides a simple, undetectable way to post to Twitter/X
by using saved session cookies instead of browser automation.

WHY THIS WORKS:
- No automation detection (no browser)
- No JavaScript needed
- Uses real authenticated session
- Simple HTTP requests
- Reliable and fast

SETUP:
1. Login to https://x.com manually in your browser
2. Export cookies as JSON file to: /home/gmnak2/Allisson/media/twitter_cookies.json
3. Run the script

See LOGIN_MANUALLY.md for detailed instructions.
"""

import json
import logging
import asyncio
import aiohttp
import random
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('allisson')


class TwitterCookieAuth:
    """
    Authenticate to Twitter/X using saved session cookies.
    
    This is the PRIMARY approach - no browser automation needed!
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.cookies_file = self.base_dir / 'media' / 'twitter_cookies.json'
        self.cookies = None
        self.session = None
        self.user_id = None
        
    async def load_cookies(self) -> bool:
        """
        Load cookies from file saved from manual login.
        
        Returns:
            True if cookies loaded successfully, False otherwise
        """
        if not self.cookies_file.exists():
            logger.error(f"❌ Cookies file not found: {self.cookies_file}")
            logger.error("📖 See LOGIN_MANUALLY.md for instructions on exporting cookies")
            return False
        
        try:
            with open(self.cookies_file, 'r') as f:
                self.cookies = json.load(f)
            
            # Check for essential cookies
            essential = ['auth_token', 'ct0']
            missing = [c for c in essential if c not in self.cookies]
            
            if missing:
                logger.warning(f"⚠️  Missing essential cookies: {missing}")
                logger.warning("     Try re-exporting from https://x.com")
            
            logger.info(f"✅ Loaded {len(self.cookies)} cookies from {self.cookies_file.name}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in cookies file: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load cookies: {e}")
            return False
    
    async def create_session(self) -> bool:
        """
        Create authenticated aiohttp session using cookies.
        
        Returns:
            True if session created successfully
        """
        if not self.cookies:
            logger.error("Cookies not loaded. Call load_cookies() first")
            return False
        
        try:
            # Create connector and session
            connector = aiohttp.TCPConnector()
            self.session = aiohttp.ClientSession(connector=connector)
            
            # Add cookies to session - they'll be sent with every request
            for name, value in self.cookies.items():
                self.session.cookie_jar.update_cookies({name: value})
            
            logger.info("✅ Created authenticated session with cookies")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def close_session(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            logger.info("Session closed")


class TwitterPostAPI:
    """
    Post tweets using authenticated session (no browser automation).
    """
    
    def __init__(self, cookies_auth: TwitterCookieAuth):
        self.auth = cookies_auth
        self.session = None
        self.tweet_url = 'https://x.com/i/api/1.1/statuses/update.json'
        self.api_host = 'https://x.com'
        
    async def setup(self) -> bool:
        """Initialize authenticated session."""
        if not await self.auth.load_cookies():
            return False
        if not await self.auth.create_session():
            return False
        self.session = self.auth.session
        return True
    
    async def post_tweet(self, text: str, in_reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a tweet using authenticated session.
        
        Args:
            text: Tweet text (max 280 characters)
            in_reply_to_id: Optional tweet ID to reply to
        
        Returns:
            Dict with success status and tweet details
        """
        try:
            if not self.session:
                logger.error("Session not initialized. Call setup() first")
                return {'success': False, 'error': 'Session not initialized'}
            
            # Validate tweet length
            if len(text) > 280:
                logger.error(f"Tweet too long: {len(text)} characters (max 280)")
                return {'success': False, 'error': 'Tweet exceeds 280 characters'}
            
            logger.info(f"📝 Posting tweet ({len(text)} chars)...")
            
            # Prepare tweet data - API format from X.com
            data = {
                'status': text,
                'include_entities': 'true',
                'include_ext_alt_text': 'true',
                'tweet_mode': 'extended',
            }
            
            if in_reply_to_id:
                data['in_reply_to_status_id'] = in_reply_to_id
            
            # Set proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://x.com/compose/tweet',
                'Origin': 'https://x.com',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            # Random delay to appear human-like
            await asyncio.sleep(random.uniform(2, 4))
            
            # POST the tweet
            async with self.session.post(
                self.tweet_url,
                data=data,
                headers=headers,
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                logger.debug(f"Response status: {resp.status}")
                
                if resp.status == 200:
                    response_data = await resp.json()
                    tweet_id = response_data.get('id_str')
                    logger.info(f"✅ Tweet posted! ID: {tweet_id}")
                    return {
                        'success': True,
                        'tweet_id': tweet_id,
                        'text': text,
                        'url': f'https://x.com/{response_data.get("user", {}).get("screen_name", "unknown")}/status/{tweet_id}',
                    }
                else:
                    resp_text = await resp.text()
                    logger.error(f"❌ Tweet posting failed (status {resp.status})")
                    logger.error(f"   Response: {resp_text[:200]}")
                    return {
                        'success': False,
                        'error': f'HTTP {resp.status}',
                        'details': resp_text[:500],
                    }
        
        except asyncio.TimeoutError:
            logger.error("Request timed out")
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close(self):
        """Close the session."""
        await self.auth.close_session()


# Simple usage example
async def demo():
    """Demo: Login and post a tweet using cookies"""
    auth = TwitterCookieAuth()
    api = TwitterPostAPI(auth)
    
    if not await api.setup():
        logger.error("Setup failed")
        return
    
    result = await api.post_tweet("Test tweet from cookie-based automation! 🚀")
    print(f"Result: {result}")
    
    await api.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo())
