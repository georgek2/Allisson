from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class Task(models.Model):
    """Represents a task assigned to an agent"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('intent_parsed', 'Intent Parsed'),
        ('plan_created', 'Plan Created'),
        ('executing', 'Executing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('delegated', 'Delegated'),
    ]
    
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    agent_name = models.CharField(max_length=100)
    command = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    metadata = models.JSONField(default=dict)
    result = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_name', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent_name} - {self.command[:50]}"
    
    def duration(self):
        """Calculate task duration"""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None


class AgentLog(models.Model):
    """Logs every action taken by agents for monitoring and learning"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs')
    agent_name = models.CharField(max_length=100)
    action = models.TextField()
    result = models.JSONField()
    success = models.BooleanField(default=True)
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['agent_name', 'success']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.agent_name} - {self.action[:50]}"


class AgentFeedback(models.Model):
    """User feedback on agent performance for learning"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    agent_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    feedback = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.agent_name} - {self.rating} stars"


class AgentContext(models.Model):
    """Persistent context/memory for agents"""
    
    agent_name = models.CharField(max_length=100, unique=True)
    context_data = models.JSONField(default=dict)
    conversation_history = models.JSONField(default=list)
    learned_patterns = models.JSONField(default=dict)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.agent_name} Context"
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': timezone.now().isoformat()
        })
        self.save()
    
    def get_recent_history(self, limit: int = 10):
        """Get recent conversation history"""
        return self.conversation_history[-limit:]


class SystemMetrics(models.Model):
    """Track system-wide metrics for monitoring"""
    
    timestamp = models.DateTimeField(auto_now_add=True)
    total_tasks = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    failed_tasks = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0.0)
    active_agents = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return f"Metrics - {self.timestamp}"