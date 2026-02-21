# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("execute/",       views.execute_command, name="execute"),
    path("tasks/",         views.get_tasks,        name="tasks"),
    path("agents/stats/",  views.get_agent_stats,  name="agent_stats"),
    path("projects/",      views.create_project,   name="create_project"),
    path("status/",        views.get_status,       name="status"),
]

