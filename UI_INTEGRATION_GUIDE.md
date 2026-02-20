# 🖥️ Allisson Empire — UI Integration Guide

**Goal:** Plug the React UI into your Django project so the frontend  
talks to your agents through real API endpoints.

---

## 📐 The Architecture We're Building

```
Browser (React UI)
    │
    │  HTTP (REST)          WebSocket (real-time)
    ▼                              ▼
api/views.py              api/consumers.py
    │                              │
    ▼                              ▼
agents/allisson.py  ◄──────────────┘
    │
    ▼
agents/hannah.py, lucy.py, mike.py ...
    │
    ▼
core/models.py (Task, AgentLog, etc.)
```

**Two communication channels:**
- **REST API** → Send commands, get project/task data
- **WebSocket** → Real-time task updates in the Live Tasks sidebar

---

## 🗂️ Files You Will Create / Modify

```
allisson_empire/
│
├── api/
│   ├── views.py          ← CREATE: REST API endpoints
│   ├── urls.py           ← CREATE: URL routes for API
│   └── consumers.py      ← CREATE: WebSocket handler
│
├── config/
│   ├── urls.py           ← MODIFY: Add api URLs + serve frontend
│   └── asgi.py           ← MODIFY: Add WebSocket routing
│
├── frontend/
│   ├── templates/
│   │   └── index.html    ← CREATE: Shell page that loads React
│   └── static/
│       └── (React build will go here later)
│
└── allisson-empire-ui.jsx ← Your existing React component
```

---

## STEP 1 — Create the API Endpoints

**File: `api/views.py`**

This is the bridge between your React UI and your agents.  
Each function here is one URL the frontend can call.

```python
# api/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync
import json

from agents.allisson import AllissonAgent
from core.models import Task, AgentLog


# ─── EXECUTE A COMMAND ────────────────────────────────────────────────────────
# Called when user types in the chat bar or clicks "Add Task"
# URL: POST /api/execute/

@csrf_exempt
@require_http_methods(["POST"])
def execute_command(request):
    """
    Receives a command from the UI and sends it to Allisson.
    
    Request body (JSON):
        { "command": "Post a tweet about AI trends" }
    
    Response (JSON):
        { "success": true, "task_id": 42, "result": {...} }
    """
    try:
        body = json.loads(request.body)
        command = body.get("command", "").strip()

        if not command:
            return JsonResponse({"success": False, "error": "Command is required"}, status=400)

        # Run Allisson (async agent) from sync Django view
        allisson = AllissonAgent()
        result = async_to_sync(allisson.execute)(
            command=command,
            user_id=request.user.id if request.user.is_authenticated else None
        )

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ─── GET ALL TASKS ────────────────────────────────────────────────────────────
# Called by the Live Tasks sidebar to show current/recent tasks
# URL: GET /api/tasks/

@require_http_methods(["GET"])
def get_tasks(request):
    """
    Returns all tasks, optionally filtered by status or agent.
    
    Query params:
        ?status=executing    → only running tasks
        ?agent=hannah        → only Hannah's tasks
        ?limit=20            → max results (default 20)
    
    Response:
        { "tasks": [ { "id": 1, "agent_name": "Hannah", ... }, ... ] }
    """
    status_filter = request.GET.get("status")
    agent_filter  = request.GET.get("agent")
    limit         = int(request.GET.get("limit", 20))

    tasks = Task.objects.all()

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if agent_filter:
        tasks = tasks.filter(agent_name__iexact=agent_filter)

    tasks = tasks[:limit]

    return JsonResponse({
        "tasks": [
            {
                "id":         t.id,
                "agent_name": t.agent_name,
                "command":    t.command,
                "status":     t.status,
                "priority":   t.priority,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "result":     t.result,
            }
            for t in tasks
        ]
    })


# ─── GET AGENT STATS ──────────────────────────────────────────────────────────
# Called by the Agent Results section
# URL: GET /api/agents/stats/

@require_http_methods(["GET"])
def get_agent_stats(request):
    """
    Returns task counts for every agent.
    
    Response:
        {
          "agents": {
            "Hannah": { "completed": 14, "ongoing": 3, "failed": 1 },
            "Lucy":   { "completed": 8, "ongoing": 1, "failed": 0 },
            ...
          }
        }
    """
    from django.db.models import Count, Q

    stats = (
        Task.objects
        .values("agent_name")
        .annotate(
            completed=Count("id", filter=Q(status="completed")),
            ongoing=Count("id", filter=Q(status__in=["executing", "plan_created", "intent_parsed"])),
            failed=Count("id", filter=Q(status="failed")),
        )
    )

    return JsonResponse({
        "agents": {
            row["agent_name"]: {
                "completed": row["completed"],
                "ongoing":   row["ongoing"],
                "failed":    row["failed"],
            }
            for row in stats
        }
    })


# ─── CREATE PROJECT ───────────────────────────────────────────────────────────
# Called when user submits the "New Project" modal form
# URL: POST /api/projects/

@csrf_exempt
@require_http_methods(["POST"])
def create_project(request):
    """
    Packages the New Project form into a command for Allisson.
    
    Request body:
        {
          "agent":      "hannah",
          "objective":  "Grow Twitter following to 10k",
          "context":    "Currently at 2k followers, posting daily",
          "guidelines": "Keep tone casual and fun, use memes"
        }
    """
    try:
        body = json.loads(request.body)

        # Build a natural language command from the form fields
        # This gets sent to Allisson who routes it to the right agent
        command = f"""
        New Project for {body.get('agent', 'the team')}:
        
        Objective: {body.get('objective', '')}
        
        Context: {body.get('context', '')}
        
        Guidelines: {body.get('guidelines', '')}
        
        Please create a project plan and begin execution.
        """.strip()

        allisson = AllissonAgent()
        result = async_to_sync(allisson.execute)(
            command=command,
            user_id=request.user.id if request.user.is_authenticated else None
        )

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ─── SYSTEM STATUS ────────────────────────────────────────────────────────────
# Called by the Status Brief section on load
# URL: GET /api/status/

@require_http_methods(["GET"])
def get_status(request):
    """
    Returns a summary for Allisson's status brief at the top of the UI.
    Asks Allisson directly for the empire status.
    """
    try:
        allisson = AllissonAgent()
        result = async_to_sync(allisson.execute)("What's the system status?")
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
```

---

## STEP 2 — Create API URL Routes

**File: `api/urls.py`** (create this — it doesn't exist yet)

```python
# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("execute/",       views.execute_command, name="execute"),
    path("tasks/",         views.get_tasks,        name="tasks"),
    path("agents/stats/",  views.get_agent_stats,  name="agent_stats"),
    path("projects/",      views.create_project,   name="create_project"),
    path("status/",        views.get_status,        name="status"),
]
```

---

## STEP 3 — Connect API URLs to Main Router

**File: `config/urls.py`** — MODIFY this file

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView   # ← ADD THIS

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # All API endpoints live under /api/
    path("api/", include("api.urls")),           # ← ADD THIS
    
    # Serve the React UI at the root URL "/"
    path("", TemplateView.as_view(template_name="index.html")),  # ← ADD THIS
]
```

---

## STEP 4 — Create the WebSocket Consumer (Real-time Live Tasks)

**File: `api/consumers.py`** (create this)

This pushes task updates to the browser the moment an agent  
changes a task's status — no page refresh needed.

```python
# api/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TaskConsumer(AsyncWebsocketConsumer):
    """
    WebSocket connection for real-time task updates.
    
    The React UI connects to ws://localhost:8000/ws/tasks/
    When an agent updates a task, we broadcast it here.
    """

    async def connect(self):
        # Join the shared "tasks" group
        await self.channel_layer.group_add("tasks", self.channel_name)
        await self.accept()
        print("✅ WebSocket client connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("tasks", self.channel_name)

    async def receive(self, text_data):
        # Client can send messages (e.g. "give me latest tasks")
        data = json.loads(text_data)
        print(f"WebSocket received: {data}")

    # This method is called by agents when a task changes
    async def task_update(self, event):
        """
        Broadcast task update to all connected browsers.
        Called like this from anywhere in your code:
        
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "tasks",
                {
                    "type": "task_update",
                    "task": {
                        "id": task.id,
                        "agent_name": task.agent_name,
                        "status": task.status,
                        "command": task.command,
                    }
                }
            )
        """
        await self.send(text_data=json.dumps({
            "type": "task_update",
            "task": event["task"]
        }))
```

---

## STEP 5 — Update ASGI to Enable WebSockets

**File: `config/asgi.py`** — MODIFY this file

```python
# config/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Import your WebSocket consumer
from api.consumers import TaskConsumer

application = ProtocolTypeRouter({
    # Regular HTTP requests → Django
    "http": get_asgi_application(),

    # WebSocket connections → Channels
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/tasks/", TaskConsumer.as_asgi()),
        ])
    ),
})
```

---

## STEP 6 — Create the HTML Shell

**File: `frontend/templates/index.html`** (create this)

This is the single HTML page that loads your React app.  
For now we'll serve the React component directly via CDN  
(no build step needed for development).

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Allisson Empire</title>
  {% load static %}
</head>
<body>
  <div id="root"></div>

  <!-- React via CDN (no build step needed for dev) -->
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <!-- Your React component -->
  <script type="text/babel" src="{% static 'allisson-empire-ui.jsx' %}"></script>

  <script type="text/babel">
    // Mount the app
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<AllissonEmpire />);
  </script>
</body>
</html>
```

---

## STEP 7 — Update the React Component to Call Real APIs

In your `allisson-empire-ui.jsx`, replace the mock data  
with real API calls. Here are the key changes to make:

### 7a. Load real status brief on mount

```jsx
// At the top of your AllissonEmpire component, replace the static string:

const [statusText, setStatusText] = useState("Loading empire status...");

useEffect(() => {
  fetch("/api/status/")
    .then(r => r.json())
    .then(data => {
      // Extract the status message from Allisson's response
      const msg = data?.result?.message || data?.result?.statistics
        ? `Total tasks: ${data.result.statistics?.total}. Completed: ${data.result.statistics?.completed}.`
        : "All systems operational.";
      setStatusText(msg);
    })
    .catch(() => setStatusText("Unable to reach empire systems."));
}, []);

// Then pass statusText into useTypingEffect:
const { displayed, done } = useTypingEffect(statusText);
```

### 7b. Load real agent stats

```jsx
// Replace MOCK_AGENT_RESULTS with a state variable:

const [agentStats, setAgentStats] = useState({});

useEffect(() => {
  fetch("/api/agents/stats/")
    .then(r => r.json())
    .then(data => setAgentStats(data.agents || {}));
}, []);

// Then in your agent chip, use agentStats[agent.name] instead of MOCK_AGENT_RESULTS[agent.id]
```

### 7c. Load real live tasks

```jsx
const [liveTasks, setLiveTasks] = useState([]);

useEffect(() => {
  // Initial load
  fetch("/api/tasks/?status=executing&limit=20")
    .then(r => r.json())
    .then(data => setLiveTasks(data.tasks || []));

  // WebSocket for real-time updates
  const ws = new WebSocket("ws://localhost:8000/ws/tasks/");
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "task_update") {
      // Add or update the task in state
      setLiveTasks(prev => {
        const exists = prev.find(t => t.id === data.task.id);
        if (exists) {
          return prev.map(t => t.id === data.task.id ? { ...t, ...data.task } : t);
        }
        return [data.task, ...prev].slice(0, 20); // max 20 shown
      });
    }
  };

  return () => ws.close();
}, []);
```

### 7d. Wire up the New Project modal submit

```jsx
// In NewProjectModal, change the Launch button onClick:

const handleSubmit = async () => {
  const response = await fetch("/api/projects/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(form),
  });
  const result = await response.json();
  console.log("Project created:", result);
  onClose();
};

// <button onClick={handleSubmit}>Launch Project ✦</button>
```

### 7e. Wire up the Add Task modal submit

```jsx
const handleSubmit = async () => {
  const response = await fetch("/api/execute/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command: `${form.task} (priority: ${form.priority})` }),
  });
  const result = await response.json();
  console.log("Task dispatched:", result);
  onClose();
};
```

---

## STEP 8 — Move the JSX File to Static Folder

```bash
# From your project root:
mkdir -p frontend/static
cp allisson-empire-ui.jsx frontend/static/allisson-empire-ui.jsx
```

---

## STEP 9 — Run Everything

You need 3 terminal windows:

```bash
# Terminal 1 — Django server (ASGI via Daphne for WebSocket support)
daphne -p 8000 config.asgi:application

# Terminal 2 — Redis (required for WebSocket channel layer)
redis-server

# Terminal 3 — (Optional) Celery for background tasks later
# celery -A config worker --loglevel=info
```

Then open `http://localhost:8000` in your browser.

---

## ✅ Integration Checklist

Work through this in order:

```
[ ] Step 1 — Create api/views.py with 5 endpoints
[ ] Step 2 — Create api/urls.py
[ ] Step 3 — Update config/urls.py (add api/ and root /)
[ ] Step 4 — Create api/consumers.py
[ ] Step 5 — Update config/asgi.py for WebSockets
[ ] Step 6 — Create frontend/templates/index.html
[ ] Step 7 — Update the React component (API calls)
[ ] Step 8 — Move JSX to frontend/static/
[ ] Step 9 — Run daphne + redis, open browser
```

---

## 🧪 Testing Each Endpoint (without the UI)

Use these curl commands to verify each endpoint works  
before connecting the frontend:

```bash
# Test 1: Execute a command
curl -X POST http://localhost:8000/api/execute/ \
  -H "Content-Type: application/json" \
  -d '{"command": "What is the system status?"}'

# Test 2: Get tasks
curl http://localhost:8000/api/tasks/

# Test 3: Get agent stats
curl http://localhost:8000/api/agents/stats/

# Test 4: Create a project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"agent":"hannah","objective":"Grow Twitter","context":"2k followers","guidelines":"Be casual"}'

# Test 5: Get status
curl http://localhost:8000/api/status/
```

---

## ⚠️ Common Issues & Fixes

| Problem | Fix |
|---|---|
| `CORS error` in browser | `CORS_ALLOW_ALL_ORIGINS = True` is already set in `base.py` ✅ |
| `WebSocket connection refused` | Make sure Redis is running (`redis-server`) |
| `TemplateDoesNotExist: index.html` | Check `frontend/templates/` folder exists and is in `TEMPLATES` `DIRS` in `base.py` |
| `async_to_sync` error in views | You're calling it correctly — `async_to_sync(allisson.execute)(command=...)` |
| React not loading | Check browser console for JSX path errors — file must be in `frontend/static/` |

---

**Once this is working, next step is to add a command input bar  
at the bottom of the UI to talk to Allisson in real time!** 🚀
