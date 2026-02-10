# Twitter/X Manual Login Setup

Twitter/X now blocks automated login attempts using browser automation (Playwright, Selenium, etc.). They detect the browser automation and deliberately return "JavaScript not available" errors.

**The Solution:** Login manually ONCE, save the session cookies, then the script uses those cookies forever.

## Step 1: Login to Twitter Manually

Open your browser (Chrome, Firefox, etc.) and go to https://x.com and **login normally**. Don't close the browser yet.

## Step 2: Export Cookies Using Browser DevTools

### Using Chrome/Edge/Chromium:
1. Open DevTools: Press `F12` or `Ctrl+Shift+I`
2. Go to **Application** tab
3. Left sidebar → **Cookies** → **https://x.com**
4. **Right-click the cookie list** → **Export as HAR**
5. Save as `twitter_cookies.har`

### Or Use This Browser Extension (Easier):
- Install [EditThisCookie](https://www.editthiscookie.com/) or [Cookie Editor](https://chrome.google.com/webstore/detail/cookie-editor/)
- Go to x.com (while logged in)
- Click extension icon
- **Export as JSON**
- Save as `twitter_cookies.json`

### Or Use the Script Below:
Open browser console (F12) and run:
```javascript
// Copy this and paste in browser DevTools Console while at https://x.com

copy(JSON.stringify(
  document.cookie.split(';').reduce((acc, c) => {
    const [name, value] = c.trim().split('=');
    acc[name] = value;
    return acc;
  }, {}),
  null, 2
))

// Then paste into a file named 'twitter_cookies.json' in /home/gmnak2/Allisson/media/
```

## Step 3: Save Cookies File

Place your exported cookies in:
```
/home/gmnak2/Allisson/media/twitter_cookies.json
```

The file should look like:
```json
{
  "auth_token": "your_auth_token_here",
  "ct0": "your_csrf_token",
  "personalization_id": "your_id",
  ...other cookies...
}
```

## Step 4: Run the Script

Now the script will use these cookies instead of trying to login automatically:

```bash
cd /home/gmnak2/Allisson
python3 -m tests.test_twitter_automation
```

The script will:
1. Check for saved cookies
2. If found, use them to authenticate
3. Post tweets without any browser automation detection
4. Work reliably without triggering bot detection

## Why This Works

- **No automation detection** - You logged in manually
- **No JavaScript required** - Cookies are sent directly with HTTP requests
- **No rate limiting** - Using a real, authenticated session
- **Simple and reliable** - Just HTTP requests with proper headers

## Important Notes

⚠️ **Keep your cookies file private!** It contains your authentication tokens.
- Don't share `twitter_cookies.json`
- Don't commit it to git
- Treat it like a password file

🔄 **Cookies expire** - You may need to re-login manually every few weeks or months depending on Twitter's session timeout.

## Troubleshooting

**"Cookies not found" error:**
- Make sure the file is at `/home/gmnak2/Allisson/media/twitter_cookies.json`
- Make sure you're logged in to x.com before exporting

**"Tweet posting fails":**
- Cookies may have expired - Re-login manually and re-export
- Check that you exported all cookies, not just a few

**"Still getting bot detection":**
- Try logging out of x.com and logging back in (mobile app if possible)
- Wait a few hours before trying the script
- Check Twitter's help for account status
