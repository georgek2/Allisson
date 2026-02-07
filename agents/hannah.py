from typing import Dict, Any, List, Optional
# import litellm
import logging
from agents.base import BaseAgent

logger = logging.getLogger('allisson')

class HannahAgent(BaseAgent):
    """
    Hannah - Social Media Manager
    
    Specialist in:
    - Posting to Twitter, LinkedIn, Facebook
    - Engaging with communities
    - Analyzing social media trends
    - Scheduling posts
    - Growing social presence
    """
    
    def __init__(self):
        super().__init__(
            name="Hannah",
            role="Social Media Manager",
            model="llama-3.3-70b-versatile",
            temperature=0.8  # Higher creativity for social content
        )
        
        self.capabilities = [
            'post_tweet',
            'post_linkedin',
            'post_facebook',
            'engage_twitter',
            'analyze_trends',
            'schedule_posts',
            'create_thread',
            'reply_to_mentions'
        ]
        
        logger.info("Hannah (Social Media Manager) initialized")
    
    async def _can_handle(self, intent: Dict) -> bool:
        """Check if this is a social media task"""
        action = intent.get('primary_action', '').lower()
        
        social_keywords = [
            'tweet', 'twitter', 'post', 'linkedin', 'facebook',
            'social', 'engage', 'reply', 'comment', 'share',
            'trend', 'hashtag', 'viral', 'thread'
        ]
        
        return any(keyword in action for keyword in social_keywords)
    
    async def _create_plan(self, intent: Dict, context: Optional[Dict]) -> List[Dict]:
        """Create execution plan for social media tasks"""
        action = intent.get('primary_action')
        
        if 'post' in action or 'tweet' in action:
            return [
                {"step": 1, "action": "generate_content", "params": intent['parameters']},
                {"step": 2, "action": "review_content", "params": {}},
                {"step": 3, "action": "post_to_platform", "params": intent['parameters']},
                {"step": 4, "action": "verify_posted", "params": {}}
            ]
        elif 'engage' in action:
            return [
                {"step": 1, "action": "find_relevant_posts", "params": intent['parameters']},
                {"step": 2, "action": "generate_responses", "params": {}},
                {"step": 3, "action": "post_responses", "params": {}}
            ]
        else:
            return [
                {"step": 1, "action": "analyze_request", "params": intent['parameters']},
                {"step": 2, "action": "execute_task", "params": {}}
            ]
    
    async def _execute_plan(self, plan: List[Dict], task) -> Dict:
        """Execute the social media plan"""
        results = []
        
        for step in plan:
            action = step['action']
            params = step['params']
            
            logger.info(f"Hannah executing: {action}")
            
            if action == 'generate_content':
                result = await self._generate_content(params)
            elif action == 'review_content':
                result = await self._review_content(results[-1] if results else {})
            elif action == 'post_to_platform':
                result = await self._post_to_platform(params, results)
            elif action == 'verify_posted':
                result = {"success": True, "verified": True}
            else:
                result = {"success": True, "action": action}
            
            results.append(result)
            
            if not result.get('success', True):
                break
        
        return {
            "success": all(r.get('success', True) for r in results),
            "steps_completed": len(results),
            "results": results,
            "final_output": results[-1] if results else {}
        }
    
    async def _generate_content(self, params: Dict) -> Dict:
        """
        Generate social media content using AI.
        
        This is where Hannah's creativity shines.
        """
        topic = params.get('topic') or params.get('subject') or params.get('content')
        platform = params.get('platform', 'twitter')
        tone = params.get('tone', 'professional')
        
        # Get context from previous results if available
        context_data = params.get('previous_results', {})
        
        system_prompt = f"""You are Hannah, a social media manager creating engaging content.

        Task: Create a {platform} post
        Topic: {topic}
        Tone: {tone}
        Context: {context_data if context_data else 'None'}

        Requirements for {platform}:
        """
                
        if platform == 'twitter':
            system_prompt += """- Maximum 280 characters
        - Engaging and conversational
        - Include 2-3 relevant hashtags
        - Call-to-action if appropriate
        - Avoid corporate speak - be human!"""
        elif platform == 'linkedin':
            system_prompt += """- Professional but not stiff
        - 1-3 paragraphs
        - Include industry insights
        - Relevant hashtags at end
        - Can include emojis sparingly"""
        
        system_prompt += "\n\nGenerate the post content (just the text, no explanations):"
        
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(
                api_key=os.getenv('GROQ_API_KEY'),
                base_url="https://api.groq.com/openai/v1"
            )
            
            # Run in thread pool to make it async-compatible
            import asyncio
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    # {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "content": content,
                "platform": platform,
                "length": len(content)
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _review_content(self, content_result: Dict) -> Dict:
        """Quick content review for appropriateness"""
        content = content_result.get('content', '')
        
        # Basic checks
        if not content:
            return {"success": False, "reason": "Empty content"}
        
        # Length check for Twitter
        if content_result.get('platform') == 'twitter' and len(content) > 280:
            return {
                "success": False,
                "reason": f"Too long for Twitter ({len(content)} chars)"
            }
        
        # Could add more sophisticated checks here
        # - Content moderation API
        # - Spam detection
        # - Brand voice consistency
        
        return {
            "success": True,
            "reviewed": True,
            "safe": True
        }
    
    async def _post_to_platform(self, params: Dict, previous_results: List[Dict]) -> Dict:
        """
        Post content to social media platform.
        
        NOTE: For MVP, we'll simulate posting.
        Later, integrate real APIs (Twitter, LinkedIn, etc.)
        """
        
        # Get the generated content from previous steps
        content_result = next(
            (r for r in previous_results if r.get('content')),
            {}
        )
        
        content = content_result.get('content')
        platform = params.get('platform', 'twitter')
        
        if not content:
            return {
                "success": False,
                "error": "No content to post"
            }
        
        logger.info(f"📱 Hannah posting to {platform}")
        logger.info(f"Content: {content}")
        
        # MVP: Simulate successful post
        # TODO: Integrate real social media APIs
        
        return {
            "success": True,
            "platform": platform,
            "content": content,
            "post_id": f"sim_{platform}_12345",  # Simulated ID
            "url": f"https://{platform}.com/user/status/12345",  # Simulated URL
            "posted_at": "2026-02-05T22:00:00Z",
            "note": "MVP: Simulated post. Real API integration coming soon!"
        }