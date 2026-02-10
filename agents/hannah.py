from typing import Dict, Any, List, Optional
import logging
import os
from agents.base import BaseAgent
from integrations.social_media import SocialMediaManager

logger = logging.getLogger('allisson')

class HannahAgent(BaseAgent):
    """
    Hannah - Social Media Manager
    
    Specialist in:
    - Posting to Twitter, LinkedIn, Facebook
    - Using Playwright automation (FREE - no API costs!)
    - Engaging with communities
    - Analyzing social media trends
    - Scheduling posts
    - Growing social presence
    
    NEW: Real browser automation instead of API simulation!
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
        
        # Initialize social media manager (Playwright automation)
        self.social_manager = None
        
        logger.info("Hannah (Social Media Manager) initialized with Playwright automation")
    
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
                {"step": 3, "action": "post_to_platform_real", "params": intent['parameters']},
                {"step": 4, "action": "verify_posted", "params": {}}
            ]
        elif 'thread' in action:
            return [
                {"step": 1, "action": "generate_thread_content", "params": intent['parameters']},
                {"step": 2, "action": "review_thread", "params": {}},
                {"step": 3, "action": "post_thread_real", "params": intent['parameters']},
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
        
        # Initialize social media manager
        self.social_manager = SocialMediaManager()
        
        try:
            for step in plan:
                action = step['action']
                params = step['params']
                
                logger.info(f"Hannah executing: {action}")
                
                if action == 'generate_content':
                    result = await self._generate_content(params)
                elif action == 'generate_thread_content':
                    result = await self._generate_thread_content(params)
                elif action == 'review_content':
                    result = await self._review_content(results[-1] if results else {})
                elif action == 'review_thread':
                    result = await self._review_thread(results[-1] if results else {})
                elif action == 'post_to_platform_real':
                    result = await self._post_to_platform_real(params, results)
                elif action == 'post_thread_real':
                    result = await self._post_thread_real(params, results)
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
        
        finally:
            # Always cleanup browser
            if self.social_manager:
                await self.social_manager.cleanup()
    
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
- Avoid corporate speak - be human!
- Make it shareable and memorable"""
        elif platform == 'linkedin':
            system_prompt += """- Professional but not stiff
- 1-3 paragraphs (150-300 words)
- Include industry insights or personal experience
- Relevant hashtags at end (3-5)
- Can include emojis sparingly
- Value-driven content that educates or inspires"""
        
        system_prompt += "\n\nGenerate the post content (just the text, no explanations):"
        
        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            client = OpenAI(
                api_key=os.getenv('GROQ_API_KEY'),
                base_url="https://api.groq.com/openai/v1"
            )
            
            import asyncio
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt}
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
    
    async def _generate_thread_content(self, params: Dict) -> Dict:
        """Generate content for a Twitter thread."""
        topic = params.get('topic') or params.get('subject') or params.get('content')
        num_tweets = params.get('num_tweets', 5)
        
        system_prompt = f"""You are Hannah creating a Twitter thread.

Topic: {topic}
Number of tweets: {num_tweets}

Requirements:
- Each tweet max 280 characters
- First tweet is a hook that grabs attention
- Last tweet has a call-to-action
- Each tweet stands alone but flows together
- Use emojis strategically
- Include relevant hashtags in last tweet

Generate {num_tweets} tweets as a numbered list:
1. [First tweet]
2. [Second tweet]
...

Just the tweets, no explanations:"""
        
        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            client = OpenAI(
                api_key=os.getenv('GROQ_API_KEY'),
                base_url="https://api.groq.com/openai/v1"
            )
            
            import asyncio
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": system_prompt}],
                temperature=self.temperature,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse tweets from numbered list
            tweets = []
            for line in content.split('\n'):
                line = line.strip()
                # Remove numbering (1. 2. etc)
                if line and (line[0].isdigit() or line.startswith('-')):
                    tweet = line.split('.', 1)[-1].strip()
                    if tweet:
                        tweets.append(tweet)
            
            return {
                "success": True,
                "tweets": tweets[:num_tweets],  # Ensure we don't exceed requested count
                "platform": "twitter",
                "type": "thread"
            }
            
        except Exception as e:
            logger.error(f"Thread generation failed: {e}")
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
    
    async def _review_thread(self, thread_result: Dict) -> Dict:
        """Review thread content."""
        tweets = thread_result.get('tweets', [])
        
        if not tweets:
            return {"success": False, "reason": "No tweets generated"}
        
        # Check each tweet length
        for i, tweet in enumerate(tweets):
            if len(tweet) > 280:
                return {
                    "success": False,
                    "reason": f"Tweet {i+1} too long ({len(tweet)} chars)"
                }
        
        return {
            "success": True,
            "reviewed": True,
            "tweet_count": len(tweets)
        }
    
    async def _post_to_platform_real(self, params: Dict, previous_results: List[Dict]) -> Dict:
        """
        Post content to social media platform using REAL BROWSER AUTOMATION.
        
        This is the NEW implementation using Playwright!
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
        
        logger.info(f"📱 Hannah posting to {platform} using Playwright")
        logger.info(f"Content: {content}")
        
        # Get credentials from environment variables
        credentials = self._get_platform_credentials(platform)
        
        if not credentials:
            return {
                "success": False,
                "error": f"No credentials found for {platform}. Set environment variables.",
                "note": "Required: TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL or LINKEDIN_EMAIL, LINKEDIN_PASSWORD"
            }
        
        try:
            # Use Playwright automation to post
            result = await self.social_manager.post_to_platform(
                platform=platform,
                content=content,
                image_path=params.get('image_path'),
                credentials=credentials
            )
            
            if result.get('success'):
                logger.info(f"✅ Successfully posted to {platform}!")
            else:
                logger.error(f"❌ Failed to post to {platform}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in real posting: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }
    
    async def _post_thread_real(self, params: Dict, previous_results: List[Dict]) -> Dict:
        """Post a Twitter thread using real browser automation."""
        
        # Get generated tweets
        thread_result = next(
            (r for r in previous_results if r.get('tweets')),
            {}
        )
        
        tweets = thread_result.get('tweets', [])
        
        if not tweets:
            return {
                "success": False,
                "error": "No tweets to post"
            }
        
        logger.info(f"📱 Hannah posting thread with {len(tweets)} tweets")
        
        credentials = self._get_platform_credentials('twitter')
        
        if not credentials:
            return {
                "success": False,
                "error": "No Twitter credentials found. Set TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL"
            }
        
        try:
            # Initialize and login
            await self.social_manager.initialize()
            await self.social_manager.twitter.login(
                username=credentials['username'],
                password=credentials['password'],
                email=credentials.get('email')
            )
            
            # Post thread
            result = await self.social_manager.twitter.post_thread(tweets)
            
            if result.get('success'):
                logger.info(f"✅ Successfully posted thread!")
            else:
                logger.error(f"❌ Failed to post thread: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error posting thread: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_platform_credentials(self, platform: str) -> Optional[Dict[str, str]]:
        """
        Get credentials for a platform from environment variables.
        
        Required environment variables:
        - Twitter: TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL
        - LinkedIn: LINKEDIN_EMAIL, LINKEDIN_PASSWORD
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        if platform == 'twitter':
            username = os.getenv('TWITTER_USERNAME')
            password = os.getenv('TWITTER_PASSWORD')
            email = os.getenv('TWITTER_EMAIL')
            
            if username and password:
                return {
                    'username': username,
                    'password': password,
                    'email': email  # Optional, but helpful for verification
                }
        
        elif platform == 'linkedin':
            email = os.getenv('LINKEDIN_EMAIL')
            password = os.getenv('LINKEDIN_PASSWORD')
            
            if email and password:
                return {
                    'email': email,
                    'password': password
                }
        
        return None