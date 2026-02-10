# Allisson Architecture

## System Overview

Allisson is a multi-agent AI orchestration system built on:

1. **Agent Framework** - Base class for all agents with common capabilities
2. **Specialist Agents** - Domain-specific agents (Hannah, Lucy, Mike, etc.)
3. **CEO Agent** - Allisson routes commands to appropriate specialists
4. **Integration Layer** - Platform-specific automation (Twitter, LinkedIn, etc.)
5. **LLM Integration** - Groq API for content generation and decision making

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│              (CLI, Web UI, API, etc.)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ALLISSON CEO AGENT                          │
│     (Command Router, Intent Parser, Orchestrator)       │
└────┬────────┬────────┬────────┬────────┬────────────────┘
     │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼
   ┌──┐    ┌──┐    ┌──┐    ┌──┐    ┌──┐
   │HS│    │LU│    │MI│    │JO│    │ME│
   │EA│    │CY│    │KE│    │SE│    │LV│
   │NN│    │  │    │  │    │PH│    │IN│
   │AH│    │  │    │  │    │  │    │ │
   └──┘    └──┘    └──┘    └──┘    └──┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌────────┬──────────┬──────────┬──────────┬────────┐
│SOCIAL  │RESEARCH  │FINANCIAL │HEALTH   │FREELANCE
│MEDIA   │&ANALYSIS │ANALYSIS  │&FITNESS │MANAGEMENT
│AUTO    │TOOLS     │TOOLS     │TOOLS    │TOOLS
└────────┴──────────┴──────────┴──────────┴────────┘
     │
     ▼
┌──────────────────────────────────────────────────┐
│            EXTERNAL INTEGRATIONS                  │
├──────────────────────────────────────────────────┤
│ • Twitter/X (Playwright)                         │
│ • LinkedIn (Playwright)                          │
│ • Facebook (Coming soon)                         │
│ • Groq LLM API                                   │
│ • Web Scrapers                                   │
└──────────────────────────────────────────────────┘
```

## Agent Hierarchy

### BaseAgent
Abstract base class for all agents. Provides:

```python
class BaseAgent(ABC):
    execute()              # Main execution pipeline
    _parse_intent()        # NLP intent extraction
    _can_handle()         # Capability check
    _create_plan()        # Planning step
    _execute_plan()       # Plan execution
    _delegate()           # Task delegation
    _create_task()        # Task tracking
    _update_task()        # Progress updates
```

### AllissonAgent (CEO)
Routes all commands to appropriate specialists:

```
Command Input
    ↓
Parse Intent (What's needed?)
    ↓
Find Matching Agent (Who can do it?)
    ↓
Execute via Agent (Get results)
    ↓
Return Results (To user)
```

### Specialist Agents

#### HannahAgent - Social Media Manager
- **Capabilities:** `post_tweet`, `post_linkedin`, `post_facebook`, `engage_twitter`, `create_thread`
- **Tools:** Playwright browser automation
- **Content:** Generated via Groq LLM
- **Flow:** Generate → Review → Post → Verify

#### LucyAgent - Research Director
- **Capabilities:** `web_research`, `analyze_data`, `create_report`, `fact_check`
- **Tools:** Web scrapers, analysis tools
- **Output:** Structured insights

#### MikeAgent - Financial Analyst
- **Capabilities:** `track_investments`, `analyze_market`, `research_stocks`
- **Tools:** Financial data APIs
- **Output:** Market analysis, recommendations

#### (Other agents follow similar pattern)

## Twitter Automation Flow

```
┌──────────────────────────────────────────────────────┐
│              Hannah Agent Execute                    │
│            "Post about AI trends"                    │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│         Step 1: Generate Content                      │
│    Prompt → Groq LLM → Tweet content                │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│         Step 2: Review Content                        │
│   Check length (≤280), appropriateness, etc.        │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│    Step 3: Post to Platform (Real Browser)           │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │   TwitterAutomation (Playwright)             │   │
│  │   ┌────────────────────────────────────────┐ │   │
│  │   │ 1. Start browser                       │ │   │
│  │   │ 2. Load saved session OR login fresh   │ │   │
│  │   │ 3. Navigate to compose                 │ │   │
│  │   │ 4. Fill tweet text                     │ │   │
│  │   │ 5. Optional: upload image              │ │   │
│  │   │ 6. Click post button                   │ │   │
│  │   │ 7. Wait for confirmation               │ │   │
│  │   │ 8. Extract tweet URL                   │ │   │
│  │   │ 9. Save session for next time          │ │   │
│  │   └────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────┘   │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│         Step 4: Verify & Return Result               │
│  Success: {url: "https://twitter.com/...", ...}    │
│  Error: {success: false, error: "..."}             │
└──────────────────────────────────────────────────────┘
```

## Data Flow - Twitter Posting

```
User Input
    │
    ├─ "Post a tweet about AI"
    │
    ▼
AllissonAgent.execute()
    │
    ├─ Parse Intent → action: "post_tweet"
    │
    ├─ Find Agent → HannahAgent
    │
    └─ Delegate → HannahAgent.execute()
       │
       ├─ Parse Intent Details
       │   └─ topic: "AI", platform: "twitter"
       │
       ├─ Create Plan
       │   ├─ generate_content
       │   ├─ review_content
       │   ├─ post_to_platform_real
       │   └─ verify_posted
       │
       ├─ Execute Plan
       │   │
       │   ├─ Generate Content
       │   │   └─ Groq LLM → "AI is revolutionizing..."
       │   │
       │   ├─ Review Content
       │   │   └─ Length check, safety check
       │   │
       │   ├─ Post to Platform
       │   │   │
       │   │   └─ TwitterAutomation
       │   │       ├─ Start browser
       │   │       ├─ Login (cached session)
       │   │       ├─ Navigate to Twitter
       │   │       ├─ Find compose area
       │   │       ├─ Type tweet (50ms delays)
       │   │       ├─ Click post
       │   │       ├─ Wait for success
       │   │       └─ Extract URL
       │   │
       │   └─ Verify
       │       └─ Confirm tweet visible
       │
       └─ Return Results
           └─ {success: true, url: "...", ...}
           
            ▼
Return to User
```

## Database Schema (Django Models)

### Task Model
```python
class Task:
    id              # Unique identifier
    command         # User's natural language command
    status          # pending, running, completed, failed
    result          # Task result (JSON)
    agent           # Which agent handled it
    user_id         # Which user requested it
    created_at      # When created
    completed_at    # When completed
    execution_time  # How long it took
```

### Session Model
```python
class Session:
    id              # Session ID
    platform        # "twitter", "linkedin", etc.
    auth_token      # Encrypted auth token
    cookies         # Serialized cookies
    user_id         # Associated user
    expires_at      # When session expires
    created_at      # When created
```

## Error Handling Strategy

```
User Error Input
    ↓
Try Execute
    ├─ Success → Return result
    └─ Failure → Capture error
       │
       ├─ Screenshot (visual debug)
       ├─ HTML dump (page source)
       ├─ Console log (JS errors)
       ├─ Stack trace (Python errors)
       │
       └─ Try Recovery
          ├─ Retry login
          ├─ Retry action
          └─ Delegate to different agent
             │
             └─ If still fails → Return error with debug info
```

## Session Persistence

```
Login Attempt
    │
    ├─ Check for saved session file
    │  └─ media/sessions/twitter_session.json
    │
    ├─ If exists
    │  ├─ Load cookies into browser context
    │  ├─ Navigate to platform
    │  └─ Verify still logged in
    │     ├─ Yes → Use session (10-15s)
    │     └─ No → Login fresh
    │
    └─ If not exists
       ├─ Navigate to login
       ├─ Enter credentials
       ├─ Wait for auth
       ├─ Save session to file (30-45s)
       └─ Use for future logins
```

## Security Architecture

### Credential Management
```
Environment Variables
    ↓
.env file (git ignored)
    ↓
Load at runtime via dotenv
    ↓
Never logged or stored in code
    ↓
Session files use cookies instead
```

### Anti-Detection Measures
```
Bot Detection Signals:
    ├─ Webdriver property
    │  └─ Hidden via JavaScript injection
    │
    ├─ User-Agent
    │  └─ Set to Chrome 120 (realistic)
    │
    ├─ Automation detection
    │  └─ Realistic viewport, timezone, locale
    │
    ├─ Timing patterns
    │  └─ Random delays between actions
    │  └─ Gradual typing (50ms per key)
    │
    └─ Behavior patterns
       └─ Human-like mouse movements
       └─ Scrolling before actions
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Fresh Login | 30-45s | Includes validation |
| Cached Login | 10-15s | Uses saved session |
| Tweet Posting | 10-15s | After login |
| Thread Posting | 20-30s | Depends on size |
| Content Generation | 2-5s | Via Groq API |

## Extension Points

### Adding New Agent
```python
class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
    
    async def _can_handle(self, intent):
        # Check if you can handle it
    
    async def _create_plan(self, intent, context):
        # Create execution plan
    
    async def _execute_plan(self, plan, task):
        # Execute plan steps
```

### Adding New Platform
```python
class FacebookAutomation(SocialMediaAutomation):
    async def login(self, ...):
        # Login logic
    
    async def post_update(self, content, ...):
        # Posting logic
```

### Adding New Capability
```python
# In HannahAgent
async def _new_capability(self, params):
    # Implement new feature
    
# Update capabilities list
self.capabilities.append('new_capability')
```

## Monitoring & Logging

```
Logging Strategy:
    ├─ INFO - Normal operations
    │  └─ "Agent X started"
    │  └─ "Posted tweet successfully"
    │
    ├─ DEBUG - Detailed operations
    │  └─ Selector matching
    │  └─ Browser interactions
    │
    ├─ WARNING - Non-critical issues
    │  └─ Session expired
    │  └─ Slow network
    │
    └─ ERROR - Failures
       └─ Login failed
       └─ Post failed
       └─ Browser crashed

Output:
    ├─ Console logs
    ├─ File logs (logs/ directory)
    ├─ Database logs (Task table)
    └─ Screenshot debug files
```

## Future Roadmap

```
Phase 1 (Current):
  ✅ Twitter automation
  ✅ Content generation
  ✅ Multi-agent routing
  
Phase 2 (Planned):
  ⏳ LinkedIn enhancement
  ⏳ Facebook integration
  ⏳ Instagram support
  
Phase 3 (Planned):
  ⏳ Engagement automation
  ⏳ Analytics dashboard
  ⏳ Scheduled posting
  
Phase 4 (Future):
  ⏳ Cross-platform campaigns
  ⏳ Team collaboration
  ⏳ API marketplace
```

---

This architecture is designed to be:
- **Scalable** - Easy to add new agents and integrations
- **Maintainable** - Clear separation of concerns
- **Extensible** - Plugin-style agent system
- **Reliable** - Error handling and recovery built-in
- **Debuggable** - Comprehensive logging and screenshots

