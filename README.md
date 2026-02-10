# Allisson Empire 🎯

**AI-Powered Agent System with Free Social Media Automation**

Allisson is a multi-agent AI system that orchestrates specialized agents to automate tasks across multiple domains. The CEO agent (Allisson) routes commands to specialist agents (Hannah, Lucy, Mike, Joseph, Melvin, Steve) who execute domain-specific tasks.

## 🌟 Key Features

### ✅ Social Media Automation (Twitter/X, LinkedIn)
- **Free automation** - Uses Playwright browser automation, no API costs
- **Session persistence** - Subsequent logins use saved sessions
- **Human-like behavior** - Anti-detection measures built-in
- **Content generation** - Integrated with Groq LLM for AI-powered content
- **Thread support** - Post Twitter threads automatically
- **Image uploads** - Attach images to posts
- **Error recovery** - Comprehensive debugging with screenshots

### 🤖 Multi-Agent Architecture
- **CEO Agent (Allisson)** - Routes commands to specialists
- **Social Media Manager (Hannah)** - Twitter, LinkedIn, Facebook
- **Research Director (Lucy)** - Web research, analysis
- **Financial Analyst (Mike)** - Investment tracking, market analysis
- **Health Coordinator (Joseph)** - Fitness, nutrition, wellness
- **Freelancing Manager (Melvin)** - Gig hunting, content writing
- **Quality Monitor (Steve)** - Performance review, optimization

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <repository>
cd Allisson
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```env
# Twitter Credentials
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email@example.com

# Groq API (for content generation)
GROQ_API_KEY=your_groq_api_key

# Optional: Chrome Path
CHROME_PATH=/usr/bin/google-chrome-stable
```

### 3. Install Chrome

**macOS:**
```bash
brew install google-chrome
```

**Ubuntu:**
```bash
sudo apt-get install google-chrome-stable
```

### 4. Test Twitter Automation

```bash
python tests/test_twitter_automation.py
```

## 📖 Usage

### Post a Tweet via Allisson

```python
import asyncio
from agents.allisson import AllissonAgent

async def main():
    allisson = AllissonAgent()
    result = await allisson.execute("Post a tweet about AI trends")
    print(result)

asyncio.run(main())
```

### Post a Tweet via Hannah

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
        await twitter.start_browser()
        await twitter.login("username", "password", "email")
        result = await twitter.post_tweet("Hello from automation! 🤖")
        print(result)
    finally:
        await twitter.close_browser()

asyncio.run(main())
```

## 📚 Documentation

- **[Twitter/X Automation Guide](TWITTER_AUTOMATION.md)** - Complete guide to using Twitter automation
- **[Tests README](tests/README.md)** - Testing and debugging guide
- **[Architecture](docs/ARCHITECTURE.md)** - System design and agent structure

## 🧪 Testing

### Run All Tests

```bash
python tests/test_twitter_automation.py
```

### Debug with Visible Browser

```bash
python tests/test_twitter_automation.py --visible
```

### Check Results

```
media/screenshots/
├── twitter_login_page.png
├── twitter_post_success.png
└── twitter_error_*.png
```

## 🔧 Project Structure

```
Allisson/
├── agents/                 # Specialist agents
│   ├── allisson.py        # CEO agent (main interface)
│   ├── hannah.py          # Social media manager
│   ├── base.py            # Base agent class
│   └── ...
├── integrations/          # External integrations
│   ├── social_media.py    # Twitter, LinkedIn automation
│   └── twitter.py         # Additional Twitter utilities
├── api/                   # Django API
├── core/                  # Core functionality
├── tests/                 # Test suites
│   └── test_twitter_automation.py
├── media/                 # Screenshots, sessions, logs
│   ├── screenshots/
│   ├── sessions/
│   └── media/
├── TWITTER_AUTOMATION.md  # Twitter guide
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (create this)
```

## 🎯 Common Workflows

### 1. Post a Tweet

```python
await allisson.execute("Post a tweet about Python development")
```

### 2. Create a Twitter Thread

```python
await hannah.execute(
    command="Create a thread about AI/ML",
    context={"num_tweets": 5}
)
```

### 3. Post with Context

```python
await hannah.execute(
    command="Post about remote work",
    context={
        "tone": "inspirational",
        "hashtags": ["remotework", "productivity"]
    }
)
```

## 🔐 Security Notes

1. **Never commit `.env`** - Add to `.gitignore`
2. **Disable 2FA** - Automation needs direct login access
3. **Rate limiting** - Twitter rate-limits frequent posts
4. **Terms of Service** - Use responsibly per Twitter's ToS
5. **Session files** - Keep `media/sessions/` private

## 🐛 Troubleshooting

### "Browser failed to launch"
- Verify Chrome is installed: `which google-chrome-stable`
- Set explicit path: `CHROME_PATH=/usr/bin/google-chrome-stable`

### "Login failed"
- Check credentials in `.env`
- Run with `--visible` to see what's happening
- Check screenshots in `media/screenshots/twitter_error_*.png`

### "Could not find tweet button"
- Twitter UI may have changed
- Update selectors in `integrations/social_media.py`
- Report the issue with screenshots

### "Rate limited"
- Wait a few hours before posting again
- Reduce post frequency
- Twitter may have detected too many posts

## 📊 Features Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Twitter Login | ✅ | Session persistence |
| Tweet Posting | ✅ | Up to 280 characters |
| Image Uploads | ✅ | PNG, JPG, GIF |
| Thread Creation | ✅ | Multiple tweets |
| LinkedIn Posting | ⚠️ | Basic implementation |
| Facebook Posting | 📋 | Coming soon |
| Content Generation | ✅ | Via Groq LLM |
| Error Recovery | ✅ | Screenshots, logs |
| Anti-Detection | ✅ | Webdriver hiding, delays |

## 🚦 Status

| Component | Status | Last Updated |
|-----------|--------|--------------|
| Twitter Automation | ✅ Active | Feb 2024 |
| Hannah Agent | ✅ Active | Feb 2024 |
| Allisson CEO Agent | ✅ Active | Feb 2024 |
| LinkedIn Integration | ⚠️ Beta | Feb 2024 |
| Tests | ✅ Comprehensive | Feb 2024 |

## 📦 Requirements

- **Python 3.8+**
- **Playwright** - Browser automation
- **Groq SDK** - LLM access
- **Django** - Web framework
- **Asyncio** - Async operations
- **python-dotenv** - Environment variables

See [requirements.txt](requirements.txt) for full list.

## 🤝 Contributing

Improvements welcome! Areas for contribution:

- [ ] Update selectors if Twitter UI changes
- [ ] Add more agent types
- [ ] Expand platform support (Facebook, Instagram, TikTok)
- [ ] Improve content generation
- [ ] Better error messages
- [ ] Performance optimization

## 📄 License

[Your License Here]

## 🙋 Support

- **Issues:** Check [Troubleshooting](#-troubleshooting) section
- **Documentation:** See [Documentation](#-documentation)
- **Tests:** Run `python tests/test_twitter_automation.py`
- **Debugging:** Use `--visible` flag or check screenshots

## 🎓 Learning Resources

- **Playwright Docs:** https://playwright.dev/python/
- **Groq API:** https://groq.com/
- **Twitter API:** https://developer.twitter.com/
- **Async Python:** https://docs.python.org/3/library/asyncio.html

---

**Made with ❤️ by the Allisson Team**

