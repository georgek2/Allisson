# Twitter/X Automation Guide

## Overview

The Allisson Empire uses **Playwright-based browser automation** to post to Twitter/X without relying on paid APIs. This is fully integrated with the Hannah agent, which handles all social media operations.

## Architecture

### Components

1. **TwitterAutomation Class** (`integrations/social_media.py`)
   - Core Playwright automation for Twitter/X
   - Handles login with session persistence
   - Posts tweets, threads, and manages interactions
   - Updated selectors for Feb 2024 Twitter UI

2. **HannahAgent** (`agents/hannah.py`)
   - High-level agent for social media tasks
   - Generates content using Groq LLM
   - Orchestrates Twitter automation via SocialMediaManager
   - Handles multi-step workflows

3. **SocialMediaManager** (`integrations/social_media.py`)
   - Unified interface for all social platforms (Twitter, LinkedIn)
   - Manages browser lifecycle
   - Supports credentials-based authentication

## Setup

### 1. Environment Variables

Create a `.env` file in the project root with:

```env
# Twitter Credentials
TWITTER_USERNAME=your_username_or_email
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email@example.com

# Groq API (for content generation)
GROQ_API_KEY=your_groq_api_key

# Optional: Chrome Path
CHROME_PATH=/usr/bin/google-chrome-stable
```

### 2. Install System Chrome

**macOS:**
```bash
brew install google-chrome
```

**Ubuntu/Debian:**
```bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install google-chrome-stable
```

**Windows:**
- Download from: https://www.google.com/chrome/
- Or use: `choco install googlechrome` (if using Chocolatey)

### 3. Verify Chrome Installation

```bash
which google-chrome-stable
# or
which google-chrome
```

## Usage

### Via Allisson Agent (Recommended)

```python
import asyncio
from agents.allisson import AllissonAgent

async def main():
    allisson = AllissonAgent()
    
    # Post a tweet
    result = await allisson.execute(
        "Post a tweet about AI trends"
    )
    
    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")

asyncio.run(main())
```

### Via Hannah Agent (Direct)

```python
import asyncio
from agents.hannah import HannahAgent

async def main():
    hannah = HannahAgent()
    
    result = await hannah.execute(
        command="Post a tweet about machine learning",
        context={"tone": "professional"}
    )
    
    print(result)

asyncio.run(main())
```

### Direct Twitter Automation

```python
import asyncio
from integrations.social_media import TwitterAutomation

async def main():
    twitter = TwitterAutomation()
    
    try:
        # Start browser
        await twitter.start_browser(headless=False)  # Set to False to see browser
        
        # Login
        success = await twitter.login(
            username="your_username",
            password="your_password",
            email="your_email@example.com"
        )
        
        if success:
            # Post a tweet
            result = await twitter.post_tweet(
                "This is my first tweet via Playwright! #automation"
            )
            print(result)
    
    finally:
        await twitter.close_browser()

asyncio.run(main())
```

## Features

### Login
- Automatic session persistence (subsequent logins use saved cookies)
- Handles email verification if needed
- Robust selector-based login process
- Anti-detection measures (User-Agent spoofing, etc.)

### Posting
- Tweet posting (up to 280 characters)
- Image uploads
- Thread creation (multiple tweets in sequence)
- Content generation via Groq LLM

### Anti-Detection
- Disabled webdriver property
- Custom User-Agent
- Realistic viewport and timezone
- Human-like delays between actions
- Gradual typing with 50ms key delays

## Screenshot Debugging

All failures capture screenshots for debugging. Check these locations:

```
media/screenshots/
├── twitter_login_page.png          # Login page
├── twitter_username_entered.png    # After username
├── twitter_password_entered.png    # After password
├── twitter_logged_in.png           # After login
├── twitter_before_compose.png      # Before composing
├── twitter_content_entered.png     # After typing content
├── twitter_post_success.png        # After posting
├── twitter_error_*.png             # Error screenshots
└── twitter_error_page.html         # Page source on error
```

## Selectors

Updated selectors for Twitter/X (Feb 2024):

| Element | Selector |
|---------|----------|
| Username Input | `input[autocomplete="username"]` |
| Password Input | `input[name="password"]` |
| Tweet Textarea | `[data-testid="tweetTextarea_0"]` |
| Compose Button | `[data-testid="SideNav_NewTweet_Button"]` |
| Post Button | `[data-testid="tweetButtonInline"]` or `[data-testid="tweetButton"]` |
| Verification Email | `input[data-testid="ocfEnterTextTextInput"]` |

## Common Issues

### Issue: "Could not find password input field"

**Solution:**
1. Check screenshots in `media/screenshots/twitter_error_*.png`
2. Verify credentials are correct
3. Check if Twitter is asking for additional verification
4. Try with `headless=False` to see what's happening

### Issue: "Browser failed to launch"

**Solution:**
```bash
# Check Chrome installation
which google-chrome-stable

# Or set explicit path
export CHROME_PATH=/usr/bin/google-chrome-stable
```

### Issue: "Login successful but not on home page"

**Solution:**
- Twitter might be showing a 2FA prompt
- Screenshots will help identify the issue
- Check console logs in `media/screenshots/twitter_error_console.log`

### Issue: "Timeout waiting for home page"

**Solution:**
- Network might be slow
- Twitter might have rate-limited
- Try again after a few minutes
- Increase timeout in `twitter.login()`

## Advanced Usage

### Custom Delays

```python
# Adjust human-like delays
await twitter.human_delay(min_seconds=2.0, max_seconds=4.0)
```

### Headless Mode

```python
# Run visible (for debugging)
await twitter.start_browser(headless=False)

# Run hidden (for production)
await twitter.start_browser(headless=True)
```

### Chrome Path

```python
# Use specific Chrome installation
await twitter.start_browser(
    use_chrome=True,
    chrome_path="/usr/bin/google-chrome"
)
```

## Performance

- **First login:** ~30-45 seconds (includes navigation and interactions)
- **Subsequent logins:** ~10-15 seconds (uses saved session)
- **Tweet posting:** ~10-15 seconds (after login)
- **Thread posting:** ~20-30 seconds (depends on thread size)

## Security Notes

1. **Credentials:** Store in `.env`, never commit to git
2. **2FA:** Disable 2FA on your Twitter account for automation (use app passwords if available)
3. **Rate Limiting:** Twitter may rate-limit frequent posts
4. **Terms of Service:** Use responsibly and comply with Twitter's ToS

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('allisson')
logger.setLevel(logging.DEBUG)
```

### Inspect Page Source

When debugging fails, check the saved HTML:

```python
# Automatically saved on error
# media/screenshots/twitter_error_page.html
```

### Console Messages

```python
# Check collected console messages
print(twitter.console_messages)
```

## Testing

Test the Twitter automation:

```bash
python -m pytest tests/test_twitter_automation.py

# Or run the quick test
python integrations/twitter.py
```

## Updates

The selectors in this implementation are updated for **Feb 2024**. If you notice:

- Login failing with new selectors needed
- Tweet posting failing with new button locations
- Any UI changes affecting automation

Update the selectors in:
- `TwitterAutomation.login()` - Update input selectors
- `TwitterAutomation.post_tweet()` - Update button selectors
- Add new selectors as needed

## Support

For issues or improvements:

1. Check screenshots in `media/screenshots/`
2. Review console logs in `media/screenshots/twitter_error_console.log`
3. Test with `headless=False` to see browser in real-time
4. Verify credentials are correct
5. Check if Twitter has changed their UI

