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

