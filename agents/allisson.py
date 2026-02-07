
from typing import Dict, Any, Optional, List
# import litellm
import json
import logging
from agents.base import BaseAgent

logger = logging.getLogger('allisson')

class AllissonAgent(BaseAgent):
    """
    CEO of the Allisson Empire.
    
    YOUR ONLY INTERFACE - All commands flow through Allisson.
    
    Responsibilities:
    - Receive all user commands
    - Analyze intent and complexity
    - Route to appropriate specialist agents
    - Orchestrate multi-agent workflows
    - Aggregate and return results
    """
    
    def __init__(self):
        super().__init__(
            name="Allisson",
            role="Chief Executive Officer - Empire Orchestrator",
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        
        # Allisson knows about ALL specialist agents
        self.specialists = {
            'hannah': {
                'class': 'HannahAgent',
                'module': 'agents.hannah',
                'description': 'Social Media Manager - Twitter, LinkedIn, Facebook posting and engagement',
                'capabilities': ['post_tweet', 'post_linkedin', 'engage_twitter', 'analyze_trends', 'schedule_posts']
            },
            'lucy': {
                'class': 'LucyAgent',
                'module': 'agents.lucy',
                'description': 'Research Director - Web research, analysis, reports, data gathering',
                'capabilities': ['web_research', 'analyze_data', 'create_report', 'fact_check']
            },
            'mike': {
                'class': 'MikeAgent',
                'module': 'agents.mike',
                'description': 'Financial Analyst - Investment tracking, market analysis, portfolio management',
                'capabilities': ['track_investments', 'analyze_market', 'research_stocks', 'portfolio_advice']
            },
            'joseph': {
                'class': 'JosephAgent',
                'module': 'agents.joseph',
                'description': 'Health Coordinator - Fitness, nutrition, meditation, wellness planning',
                'capabilities': ['create_workout', 'meal_planning', 'track_health', 'wellness_advice']
            },
            'melvin': {
                'class': 'MelvinAgent',
                'module': 'agents.melvin',
                'description': 'Freelancing Manager - Gig hunting, content writing, ecommerce',
                'capabilities': ['find_gigs', 'write_content', 'manage_ecommerce', 'client_outreach']
            },
            'steve': {
                'class': 'SteveAgent',
                'module': 'agents.steve',
                'description': 'Quality Monitor - Performance review, system optimization, feedback analysis',
                'capabilities': ['review_performance', 'analyze_feedback', 'optimize_system', 'quality_control']
            }
        }
        
        # Allisson can handle some tasks herself (simple queries, scheduling, etc.)
        self.capabilities = [
            'route_task',
            'orchestrate_multi_agent',
            'answer_simple_query',
            'manage_schedule',
            'system_status'
        ]
        
        logger.info("Allisson CEO initialized - Managing empire of specialist agents")
    
    async def execute(
        self,
        command: str,
        context: Optional[Dict] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main entry point - YOUR interface to the empire.
        
        Examples:
            "Post a tweet about AI trends"
            "Research best stocks to buy and post summary"
            "Find me freelance gigs in web development"
            "Create a workout plan"
        """
        logger.info(f"🎯 Allisson received command: {command}")
        
        try:
            # Create task
            task = await self._create_task(command, user_id)
            
            # Parse intent
            intent = await self._parse_intent(command, context)
            await self._update_task(task, "intent_parsed", {"intent": intent})
            
            # Decide: Simple task or needs specialist?
            if await self._is_simple_query(intent):
                logger.info("Allisson handling simple query herself")
                result = await self._handle_simple_query(intent, command)
            else:
                # Route to specialist(s)
                result = await self._route_to_specialists(intent, command, context, task)
            
            # Log and return
            await self._log_execution(task, result, 0)
            
            return {
                "success": True,
                "agent": "Allisson",
                "result": result,
                "task_id": task.id
            }
            
        except Exception as e:
            logger.error(f"Allisson error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "agent": "Allisson",
                "error": str(e)
            }
    
    async def _is_simple_query(self, intent: Dict) -> bool:
        """Check if Allisson can handle this herself"""
        simple_actions = [
            'greeting',
            'status_check',
            'help_request',
            'time_query',
            'schedule_query'
        ]
        return intent.get('primary_action') in simple_actions
    
    async def _handle_simple_query(self, intent: Dict, command: str) -> Dict:
        """Allisson handles simple queries herself"""
        action = intent.get('primary_action')
        
        if action == 'greeting':
            return {
                "message": "Hello! I'm Allisson, your AI Chief of Staff. How can I help you today?",
                "handled_by": "Allisson"
            }
        elif action == 'status_check':
            return await self._get_system_status()
        elif action == 'help_request':
            return self._get_help_info()
        else:
            return {
                "message": f"I can help with that. Let me route you to the right specialist.",
                "handled_by": "Allisson"
            }
    
    async def _route_to_specialists(
        self,
        intent: Dict,
        command: str,
        context: Optional[Dict],
        task
    ) -> Dict:
        """
        Core routing logic - decides which specialist(s) to use.
        
        Can handle:
        1. Single agent tasks
        2. Multi-agent sequential tasks
        3. Multi-agent parallel tasks
        """
        
        # Analyze if this needs multiple agents
        needs_multiple = await self._needs_multiple_agents(intent)
        
        if needs_multiple:
            logger.info("Multi-agent task detected")
            return await self._orchestrate_multi_agent(intent, command, context, task)
        else:
            # Single specialist
            specialist_name = await self._select_specialist(intent)
            
            if not specialist_name:
                return {
                    "success": False,
                    "message": "No suitable specialist found. Please rephrase your request.",
                    "handled_by": "Allisson"
                }
            
            logger.info(f"Routing to specialist: {specialist_name}")
            return await self._delegate_to_specialist(specialist_name, command, context, task)
    
    async def _select_specialist(self, intent: Dict) -> Optional[str]:
        """
        Use AI to intelligently select the best specialist.
        
        This is Allisson's "intelligence" - deciding who's best for the job.
        """
        
        # Build specialist directory for AI
        specialist_info = "\n".join([
            f"- {name.upper()}: {info['description']}"
            for name, info in self.specialists.items()
        ])
        
        routing_prompt = f"""You are Allisson, CEO of an AI agent empire.

        Available specialists:
        {specialist_info}

        User request analysis:
        - Action: {intent.get('primary_action')}
        - Parameters: {json.dumps(intent.get('parameters', {}))}
        - Priority: {intent.get('priority')}

        Which ONE specialist should handle this request?

        Rules:
        - Return ONLY the specialist name (hannah, lucy, mike, joseph, melvin, or steve)
        - If NO specialist fits, return "none"
        - Choose the BEST match based on capabilities

        Examples:
        - "Post a tweet" → hannah
        - "Research AI trends" → lucy
        - "Find freelance work" → melvin
        - "Track Bitcoin price" → mike
        - "Create workout plan" → joseph
        - "Review system performance" → steve

        Response (ONE WORD ONLY):"""
        
        # Quick keyword-based heuristic to avoid unnecessary LLM calls during tests
        action = (intent.get('primary_action') or '').lower()
        params_text = json.dumps(intent.get('parameters', {})).lower()
        combined = f"{action} {params_text}"

        keyword_map = {
            'hannah': ['tweet', 'twitter', 'post', 'linkedin', 'facebook', 'social'],
            'lucy': ['research', 'researcher', 'study', 'analyze', 'report', 'web'],
            'mike': ['stock', 'stocks', 'bitcoin', 'price', 'market', 'investment', 'invest'],
            'joseph': ['workout', 'meal', 'fitness', 'exercise', 'nutrition', 'wellness'],
            'melvin': ['freelance', 'freelancer', 'gig', 'gigs', 'portfolio', 'write', 'content'],
            'steve': ['review', 'performance', 'optimize', 'quality', 'monitor']
        }

        for name, kws in keyword_map.items():
            if any(k in combined for k in kws):
                return name

        # If heuristic didn't match, fall back to LLM-based routing
        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            import re

            load_dotenv()

            client = OpenAI(
                api_key=os.getenv('GROQ_API_KEY'),
                base_url="https://api.groq.com/openai/v1"
            )

            messages = [
                {"role": "system", "content": routing_prompt},
                {"role": "user", "content": f"Intent: {json.dumps(intent)}"}
            ]

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )

            specialist = response.choices[0].message.content.strip().lower()
            # Normalize the model output to a simple token (letters only)
            specialist = re.sub(r"[^a-z]", "", specialist)

            if specialist in self.specialists:
                return specialist
            elif specialist == "none":
                return None
            else:
                logger.warning(f"Invalid specialist selected: {specialist}")
                return None

        except Exception as e:
            logger.error(f"Specialist selection failed: {e}")
            return None
    
    async def _delegate_to_specialist(
        self,
        specialist_name: str,
        command: str,
        context: Optional[Dict],
        task
    ) -> Dict:
        """
        Instantiate and execute the specialist agent.
        """
        try:
            # Dynamically import the specialist
            specialist_info = self.specialists[specialist_name]
            module_name = specialist_info['module']
            class_name = specialist_info['class']
            
            # Import the module
            import importlib
            module = importlib.import_module(module_name)
            
            # Get the class
            specialist_class = getattr(module, class_name)
            
            # Instantiate the agent
            specialist = specialist_class()
            
            logger.info(f"✅ Delegating to {specialist_name.upper()}")
            
            # Execute
            result = await specialist.execute(
                command=command,
                context={
                    **(context or {}),
                    'delegated_by': 'Allisson',
                    'parent_task_id': task.id
                }
            )
            
            return {
                "success": result.get('success', False),
                "delegated_to": specialist_name,
                "specialist_result": result,
                "message": f"Task completed by {specialist_name.upper()}"
            }
            
        except ImportError:
            logger.warning(f"Specialist {specialist_name} not yet implemented")
            return {
                "success": False,
                "message": f"{specialist_name.upper()} is not available yet. Coming soon!",
                "delegated_to": specialist_name
            }
        except Exception as e:
            logger.error(f"Delegation to {specialist_name} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "delegated_to": specialist_name
            }
    
    async def _needs_multiple_agents(self, intent: Dict) -> bool:
        """
        Determine if task requires multiple specialists.
        
        Examples:
        - "Research X and post about it" → lucy + hannah
        - "Find gigs and create portfolio" → melvin + fiona
        """
        
        action = intent.get('primary_action', '')
        
        # Keywords that indicate multi-agent tasks
        multi_agent_keywords = [
            'and',
            'then',
            'after',
            'before',
            'both',
            'also',
            'plus'
        ]
        
        # Check if command suggests multiple actions
        return any(keyword in action.lower() for keyword in multi_agent_keywords)
    
    async def _orchestrate_multi_agent(
        self,
        intent: Dict,
        command: str,
        context: Optional[Dict],
        task
    ) -> Dict:
        """
        Handle tasks that need multiple specialists working together.
        
        Example: "Research AI trends and post a summary tweet"
        - Step 1: Lucy researches
        - Step 2: Hannah posts (using Lucy's research)
        """
        
        logger.info("🎭 Orchestrating multi-agent workflow")
        
        # Use AI to break down into sub-tasks
        breakdown = await self._break_into_subtasks(intent, command)
        
        results = []
        accumulated_context = context or {}
        
        for subtask in breakdown.get('subtasks', []):
            specialist_name = subtask.get('specialist')
            subtask_command = subtask.get('command')
            
            logger.info(f"Multi-agent step: {specialist_name} - {subtask_command}")
            
            result = await self._delegate_to_specialist(
                specialist_name,
                subtask_command,
                accumulated_context,
                task
            )
            
            results.append(result)
            
            # Pass results to next agent
            if result.get('success'):
                accumulated_context['previous_results'] = result.get('specialist_result')
        
        return {
            "success": all(r.get('success', False) for r in results),
            "multi_agent": True,
            "workflow": breakdown,
            "results": results,
            "message": "Multi-agent workflow completed"
        }
    
    async def _break_into_subtasks(self, intent: Dict, command: str) -> Dict:
        """
        Use AI to break complex command into sequential subtasks.
        """
        
        specialist_list = ", ".join(self.specialists.keys())
        
        breakdown_prompt = f"""Break this command into sequential subtasks for specialists.

        Command: {command}
        Intent: {json.dumps(intent)}

        Available specialists: {specialist_list}

        Return JSON array of subtasks:
        {{
        "subtasks": [
            {{"specialist": "specialist_name", "command": "what they should do"}},
            ...
        ]
        }}

        Example:
        Command: "Research AI trends and post a tweet about it"
        Output:
        {{
        "subtasks": [
            {{"specialist": "lucy", "command": "Research current AI trends"}},
            {{"specialist": "hannah", "command": "Create and post a tweet summarizing the research"}}
        ]
        }}

        Return ONLY valid JSON:"""
        
        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            import asyncio

            load_dotenv()

            client = OpenAI(
                api_key=os.getenv('GROQ_API_KEY'),
                base_url="https://api.groq.com/openai/v1"
            )

            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": breakdown_prompt}],
                temperature=0.5,
                max_tokens=self.max_tokens
            )

            return self._safe_json_parse(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Subtask breakdown failed: {e}")
            return {"subtasks": []}
    
    async def _get_system_status(self) -> Dict:
        """Get status of all agents and system health"""
        from core.models import Task, AgentLog
        from django.db.models import Count, Avg
        from asgiref.sync import sync_to_async
        
        @sync_to_async
        def get_stats():
            total_tasks = Task.objects.count()
            completed_tasks = Task.objects.filter(status='completed').count()
            failed_tasks = Task.objects.filter(status='failed').count()
            
            agent_stats = AgentLog.objects.values('agent_name').annotate(
                count=Count('id'),
                avg_time=Avg('execution_time')
            )
            
            return {
                "total_tasks": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "success_rate": f"{(completed_tasks/total_tasks*100):.1f}%" if total_tasks > 0 else "N/A",
                "agent_stats": list(agent_stats)
            }
        
        stats = await get_stats()
        
        return {
            "status": "operational",
            "message": "All systems running",
            "statistics": stats,
            "specialists_available": list(self.specialists.keys()),
            "handled_by": "Allisson"
        }
    
    def _get_help_info(self) -> Dict:
        """Provide help information"""
        return {
            "message": "I'm Allisson, your AI Chief of Staff. I can help you with:",
            "capabilities": [
                "📱 Social Media - Post to Twitter, LinkedIn, engage with communities",
                "🔍 Research - Deep web research, analysis, reports",
                "💰 Finance - Track investments, analyze markets, portfolio advice",
                "💪 Health - Workout plans, nutrition, wellness tracking",
                "💼 Freelancing - Find gigs, manage clients, create content",
                "📊 Monitoring - System performance, quality control"
            ],
            "examples": [
                "Post a tweet about AI trends",
                "Research best stocks to invest in",
                "Find me web development gigs",
                "Create a 30-day workout plan",
                "What's my system status?"
            ],
            "handled_by": "Allisson"
        }
    
    async def route_task(
        self,
        intent: Dict,
        task,
        delegated_from: str = None
    ) -> Dict:
        """
        Special method for when other agents delegate back to Allisson.
        
        Called when a specialist realizes they need help from another specialist.
        """
        logger.info(f"⬆️ Task escalated to Allisson from {delegated_from}")
        
        command = task.command
        return await self._route_to_specialists(intent, command, {}, task)
    
    # BaseAgent abstract methods implementation
    async def _can_handle(self, intent: Dict) -> bool:
        """Allisson can handle anything - she routes appropriately"""
        return True  # CEO handles everything by routing
    
    async def _create_plan(self, intent: Dict, context: Optional[Dict]) -> List[Dict]:
        """Allisson's plan is always: analyze and route"""
        return [
            {"step": 1, "action": "analyze_intent", "params": intent},
            {"step": 2, "action": "select_specialist", "params": {}},
            {"step": 3, "action": "delegate_task", "params": {}}
        ]
    
    async def _execute_plan(self, plan: List[Dict], task) -> Dict:
        """Plan execution handled in main execute method"""
        return {"success": True, "message": "Routing complete"}