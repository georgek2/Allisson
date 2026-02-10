# Allisson Tests

This directory contains test suites for the Allisson agent system.

## Available Tests

### Twitter/X Automation Tests

**File:** `test_twitter_automation.py`

Complete test suite for Twitter/X automation:

```bash
# Run all tests (automated)
python tests/test_twitter_automation.py

# Run with visible browser (for debugging)
python tests/test_twitter_automation.py --visible
```

**What it tests:**

1. ✅ Environment setup (credentials, Chrome installation)
2. ✅ Browser automation basics (start, navigate, interact)
3. ✅ Twitter login (with session persistence)
4. ✅ Tweet posting (with error handling)
5. ✅ Hannah agent integration (full workflow)

**Output:**

- Success screenshots saved to `media/screenshots/`
- Error screenshots and HTML dumps for debugging
- Console logs for troubleshooting

### Test Results

After running tests, check:

```
media/screenshots/
├── twitter_login_page.png          # Login started
├── twitter_username_entered.png    # Username filled
├── twitter_password_entered.png    # Password filled
├── twitter_logged_in.png           # Login completed
├── twitter_before_compose.png      # Before tweet composition
├── twitter_content_entered.png     # Content filled
├── twitter_post_success.png        # Tweet posted
└── twitter_error_*.png             # Error screenshots (if failed)
```

## Running Tests

### Quick Test

```bash
cd /home/gmnak2/Allisson
python tests/test_twitter_automation.py
```

### Visible Browser Debugging

See the browser in action:

```bash
python tests/test_twitter_automation.py --visible
```

This runs with `headless=False`, showing:
- Login process
- Tweet composition
- Post submission

### Individual Component Tests

**Test TwitterAutomation class:**

```python
import asyncio
from integrations.social_media import TwitterAutomation

async def test():
    twitter = TwitterAutomation()
    await twitter.start_browser()
    await twitter.login("username", "password", "email")
    result = await twitter.post_tweet("Test tweet!")
    await twitter.close_browser()
    return result

asyncio.run(test())
```

**Test HannahAgent:**

```python
import asyncio
from agents.hannah import HannahAgent

async def test():
    hannah = HannahAgent()
    result = await hannah.execute("Post a tweet about Python")
    return result

asyncio.run(test())
```

**Test AllissonAgent:**

```python
import asyncio
from agents.allisson import AllissonAgent

async def test():
    allisson = AllissonAgent()
    result = await allisson.execute("Post a tweet about AI")
    return result

asyncio.run(test())
```

## Troubleshooting

### Tests Fail With "Could not find password input field"

1. Run with `--visible` to see what's happening
2. Check screenshots in `media/screenshots/twitter_error_*.png`
3. Verify credentials in `.env` are correct
4. Check if Twitter is showing unusual prompts

### Tests Fail With "Browser failed to launch"

```bash
# Verify Chrome installation
which google-chrome-stable

# If not found, install it:
# macOS: brew install google-chrome
# Ubuntu: sudo apt-get install google-chrome-stable
```

### Tests Timeout

- Network might be slow
- Twitter might be rate-limiting
- Try again after a few minutes
- Increase timeout values in code

### Console Shows "CSP violations"

This is normal - Twitter uses Content Security Policy and we're injecting scripts. It doesn't affect functionality.

## Debugging Tips

1. **Enable verbose logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check saved HTML on error:**
   ```
   media/screenshots/twitter_error_page.html
   ```

3. **Review console messages:**
   ```python
   print(twitter.console_messages)
   ```

4. **Inspect with visible browser:**
   ```bash
   python tests/test_twitter_automation.py --visible
   ```

## Test Coverage

| Component | Test Status | Coverage |
|-----------|------------|----------|
| TwitterAutomation.login() | ✅ | Full |
| TwitterAutomation.post_tweet() | ✅ | Full |
| TwitterAutomation.post_thread() | ⚠️ | Manual |
| HannahAgent.execute() | ✅ | Full |
| SocialMediaManager | ✅ | Full |

## Adding New Tests

1. Create test function in `test_twitter_automation.py`
2. Use async/await pattern
3. Add logging for debugging
4. Save screenshots on failure
5. Update this README

Example:

```python
async def test_my_feature():
    """Test new feature"""
    print("\n🧪 Testing new feature...")
    
    from integrations.social_media import TwitterAutomation
    
    twitter = TwitterAutomation()
    try:
        await twitter.start_browser()
        # Your test here
        print("✅ Feature works!")
        return True
    finally:
        await twitter.close_browser()
```

## CI/CD Integration

For automated testing in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Test Twitter Automation
  run: |
    python tests/test_twitter_automation.py
  env:
    TWITTER_USERNAME: ${{ secrets.TWITTER_USERNAME }}
    TWITTER_PASSWORD: ${{ secrets.TWITTER_PASSWORD }}
    TWITTER_EMAIL: ${{ secrets.TWITTER_EMAIL }}
    GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

