from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import litellm
import json
from datetime import datetime
from core.models import AgentLog, Task

class BaseAgent(ABC):
    """
    Base class for all agents in the Allisson Empire.
    Every agent inherits this and implements their specific capabilities.
    """
    
    def __init__(
        self, 
        name: str, 
        role: str,
        model: str = "gemini/gemini-2.0-flash-exp",
        temperature: float = 0.3
    ):
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        self.capabilities = []
        self.conversation_history = []
        self.context = {}
    
    async def execute(
        self, 
        command: str, 
        context: Optional[Dict] = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Main entry point for agent execution.
        
        Flow:
        1. Parse intent from command
        2. Create execution plan
        3. Execute plan step-by-step
        4. Log results
        5. Return output
        """
        try:
            # Start logging
            task = await self._create_task(command, user_id)
            
            # Step 1: Understand what user wants
            intent = await self._parse_intent(command, context)
            await self._update_task(task, "intent_parsed", intent)
            
            # Step 2: Check if this is within agent's capabilities
            if not await self._can_handle(intent):
                return await self._delegate_to_allisson(intent, task)
            
            # Step 3: Create execution plan
            plan = await self._create_plan(intent, context)
            await self._update_task(task, "plan_created", plan)
            
            # Step 4: Execute the plan
            result = await self._execute_plan(plan, task)
            
            # Step 5: Verify and log
            await self._log_execution(task, result)
            
            return {
                "success": True,
                "agent": self.name,
                "result": result,
                "task_id": task.id
            }
            
        except Exception as e:
            error_result = {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            await self._log_execution(task, error_result)
            return error_result
    
    async def _parse_intent(self, command: str, context: Dict) -> Dict:
        """Use LLM to understand command intent"""
        
        system_prompt = f"""
        You are {self.name}, {self.role} in the Allisson Empire.
        
        Your capabilities: {', '.join(self.capabilities)}
        
        Parse the user command and extract:
        1. primary_action: What needs to be done
        2. parameters: Specific details (names, values, constraints)
        3. priority: urgent, high, medium, low
        4. deadline: When it should be completed
        5. success_criteria: How to know if successful
        
        Return ONLY valid JSON. No explanation.
        """
        
        user_prompt = f"""
        Command: {command}
        Context: {json.dumps(context or {})}
        
        Return JSON with: primary_action, parameters, priority, deadline, success_criteria
        """
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature
        )
        
        return self._safe_json_parse(response.choices[0].message.content)
    
    @abstractmethod
    async def _can_handle(self, intent: Dict) -> bool:
        """Each agent decides if they can handle this task"""
        pass
    
    @abstractmethod
    async def _create_plan(self, intent: Dict, context: Dict) -> List[Dict]:
        """Each agent creates their own execution plan"""
        pass
    
    @abstractmethod
    async def _execute_plan(self, plan: List[Dict], task) -> Dict:
        """Each agent executes their plan"""
        pass
    
    async def _delegate_to_allisson(self, intent: Dict, task) -> Dict:
        """If agent can't handle, escalate to Allisson"""
        from agents.allisson import AlissonAgent
        
        allisson = AlissonAgent()
        return await allisson.delegate_to_specialist(intent, task)
    
    async def _create_task(self, command: str, user_id: int):
        """Create task record in database"""
        from core.models import Task
        
        return await Task.objects.acreate(
            agent_name=self.name,
            command=command,
            user_id=user_id,
            status="initiated",
            created_at=datetime.now()
        )
    
    async def _update_task(self, task, status: str, data: Dict):
        """Update task progress"""
        task.status = status
        task.metadata = {**task.metadata, **data}
        await task.asave()
    
    async def _log_execution(self, task, result: Dict):
        """Log execution for Steve (monitoring agent) to review"""
        from core.models import AgentLog
        
        await AgentLog.objects.acreate(
            agent_name=self.name,
            task_id=task.id,
            action=task.command,
            result=result,
            success=result.get('success', False),
            timestamp=datetime.now()
        )
        
        # Update task
        task.status = "completed" if result.get('success') else "failed"
        task.completed_at = datetime.now()
        await task.asave()
    
    def _safe_json_parse(self, text: str) -> Dict:
        """Safely parse JSON from LLM response"""
        try:
            # Remove markdown code blocks if present
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Fallback: extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
    
    async def learn_from_feedback(self, task_id: int, feedback: str, rating: int):
        """Agent learns from user feedback (for future improvement)"""
        # Store feedback for fine-tuning or prompt adjustment
        from core.models import AgentFeedback
        
        await AgentFeedback.objects.acreate(
            agent_name=self.name,
            task_id=task_id,
            feedback=feedback,
            rating=rating,
            timestamp=datetime.now()
        )