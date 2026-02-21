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

