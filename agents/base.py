from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import litellm
import json
import logging
from datetime import datetime
from asgiref.sync import sync_to_async

logger = logging.getLogger('allisson')

class BaseAgent(ABC):
    """
    Foundation class for all agents in the Allisson Empire.
    
    Every agent (Allisson, Hannah, Lucy, etc.) inherits this.
    Provides core functionality: intent parsing, planning, execution, logging, learning.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        model: str = "gemini/gemini-2.0-flash-exp",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.capabilities = []  # Each agent defines their capabilities
        
        logger.info(f"Agent {self.name} initialized - Role: {self.role}")
    
    async def execute(
        self,
        command: str,
        context: Optional[Dict] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main execution pipeline.
        
        Args:
            command: Natural language command from user
            context: Additional context (previous tasks, user preferences, etc.)
            user_id: User making the request
        
        Returns:
            Dict with execution results
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"{self.name} received command: {command}")
            
            # Create task record
            task = await self._create_task(command, user_id)
            
            # Step 1: Parse intent
            intent = await self._parse_intent(command, context)
            await self._update_task(task, "intent_parsed", {"intent": intent})
            logger.info(f"{self.name} parsed intent: {intent.get('primary_action')}")
            
            # Step 2: Check if this agent can handle it
            if not await self._can_handle(intent):
                logger.info(f"{self.name} delegating task - outside capabilities")
                return await self._delegate(intent, task)
            
            # Step 3: Create execution plan
            plan = await self._create_plan(intent, context)
            await self._update_task(task, "plan_created", {"plan": plan})
            logger.info(f"{self.name} created plan with {len(plan)} steps")
            
            # Step 4: Execute plan
            await self._update_task(task, "executing", {})
            result = await self._execute_plan(plan, task)
            
            # Step 5: Finalize
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._log_execution(task, result, execution_time)
            
            logger.info(f"{self.name} completed task in {execution_time:.2f}s")
            
            return {
                "success": True,
                "agent": self.name,
                "result": result,
                "task_id": task.id,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"{self.name} error: {str(e)}", exc_info=True)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "execution_time": execution_time
            }
            
            if 'task' in locals():
                await self._log_execution(task, error_result, execution_time)
            
            return error_result
    
    async def _parse_intent(self, command: str, context: Optional[Dict]) -> Dict:
        """
        Use LLM to understand what the user wants.
        
        Returns JSON with:
        - primary_action: What to do
        - parameters: Specific details
        - priority: urgent/high/medium/low
        - success_criteria: How to know if successful
        """
        
        system_prompt = f"""You are {self.name}, {self.role} in the Allisson Empire.

        Your capabilities: {', '.join(self.capabilities)}

        Analyze the user's command and extract structured information.

        Return ONLY valid JSON (no markdown, no explanation) with these fields:
        {{
        "primary_action": "specific action to take",
        "parameters": {{
            "key": "value pairs of all relevant parameters"
        }},
        "priority": "urgent|high|medium|low",
        "deadline": "if mentioned, otherwise null",
        "success_criteria": "how to verify success"
        }}"""
                
        user_prompt = f"""Command: {command}

        Additional context: {json.dumps(context or {}, indent=2)}

        Return structured JSON analysis."""
        
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            return self._safe_json_parse(content)
            
        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            # Fallback basic intent
            return {
                "primary_action": "unknown",
                "parameters": {"raw_command": command},
                "priority": "medium",
                "deadline": None,
                "success_criteria": "task completion"
            }
    
    @abstractmethod
    async def _can_handle(self, intent: Dict) -> bool:
        """
        Each agent decides if they can handle this task.
        
        Example for Hannah (social media agent):
            return intent['primary_action'] in ['post_tweet', 'post_linkedin', 'engage_twitter']
        """
        pass
    
    @abstractmethod
    async def _create_plan(self, intent: Dict, context: Optional[Dict]) -> List[Dict]:
        """
        Each agent creates their specific execution plan.
        
        Returns list of steps:
        [
            {"step": 1, "action": "validate_input", "params": {...}},
            {"step": 2, "action": "execute_main", "params": {...}},
            {"step": 3, "action": "verify_result", "params": {...}}
        ]
        """
        pass
    
    @abstractmethod
    async def _execute_plan(self, plan: List[Dict], task) -> Dict:
        """
        Execute the plan step by step.
        
        Returns execution result with details.
        """
        pass
    
    async def _delegate(self, intent: Dict, task) -> Dict:
        """
        If agent can't handle task, delegate to Allisson (CEO) for routing.
        """
        logger.info(f"{self.name} delegating to Allisson")
        
        # Import here to avoid circular imports
        from agents.allisson import AllissonAgent
        
        allisson = AllissonAgent()
        return await allisson.route_task(intent, task, delegated_from=self.name)
    
    @sync_to_async
    def _create_task(self, command: str, user_id: Optional[int]):
        """Create task record in database"""
        from core.models import Task
        
        return Task.objects.create(
            user_id=user_id,
            agent_name=self.name,
            command=command,
            status="initiated",
            metadata={}
        )
    
    @sync_to_async
    def _update_task(self, task, status: str, data: Dict):
        """Update task status and metadata"""
        task.status = status
        task.metadata = {**task.metadata, **data}
        task.save()
    
    @sync_to_async
    def _log_execution(self, task, result: Dict, execution_time: float):
        """Log execution for monitoring (Steve will review these)"""
        from core.models import AgentLog
        
        task.status = "completed" if result.get('success') else "failed"
        task.result = result
        task.completed_at = datetime.now()
        task.save()
        
        AgentLog.objects.create(
            task=task,
            agent_name=self.name,
            action=task.command,
            result=result,
            success=result.get('success', False),
            execution_time=execution_time
        )
    
    def _safe_json_parse(self, text: str) -> Dict:
        """Safely extract and parse JSON from LLM response"""
        try:
            # Remove markdown code blocks
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            text = text.strip()
            return json.loads(text)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed, trying regex extraction: {e}")
            
            # Try to extract JSON with regex
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Ultimate fallback
            return {"error": "Failed to parse JSON", "raw": text}
    
    async def get_context(self) -> Dict:
        """Get agent's persistent context from database"""
        from core.models import AgentContext
        
        context, _ = await sync_to_async(AgentContext.objects.get_or_create)(
            agent_name=self.name
        )
        return context.context_data
    
    async def update_context(self, new_data: Dict):
        """Update agent's persistent context"""
        from core.models import AgentContext
        
        context, _ = await sync_to_async(AgentContext.objects.get_or_create)(
            agent_name=self.name
        )
        context.context_data = {**context.context_data, **new_data}
        await sync_to_async(context.save)()
    
    @sync_to_async
    def learn_from_feedback(self, task_id: int, feedback: str, rating: int):
        """
        Agent learns from user feedback for continuous improvement.
        
        This is critical for Steve (monitoring agent) to analyze and
        for individual agents to improve their performance over time.
        
        Args:
            task_id: The task being rated
            feedback: User's text feedback
            rating: 1-5 star rating
        
        Usage:
            await agent.learn_from_feedback(
                task_id=123,
                feedback="The tweet was too formal, needed more personality",
                rating=3
            )
        """
        from core.models import AgentFeedback
        
        AgentFeedback.objects.create(
            task_id=task_id,
            agent_name=self.name,
            feedback=feedback,
            rating=rating,
            timestamp=datetime.now()
        )
        
        logger.info(f"{self.name} received feedback (rating: {rating}/5) for task {task_id}")