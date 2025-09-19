"""
Claude AI service for content generation and analysis
"""

import anthropic
from typing import Optional, Dict, Any, List
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class ClaudeService:
    """Service for Claude AI interactions"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.claude_api_key)
    
    async def generate_tweet_content(
        self, 
        prompt: str, 
        theme: Optional[str] = None,
        personality: str = "friendly",
        max_length: int = 280
    ) -> Dict[str, Any]:
        """Generate tweet content based on prompt and theme"""
        try:
            system_prompt = f"""You are a {personality} Twitter bot. Generate engaging tweet content that:
- Is {max_length} characters or less
- Matches the personality: {personality}
- Is relevant to the theme: {theme or 'general topics'}
- Includes appropriate hashtags if relevant
- Is engaging and encourages interaction
- Follows Twitter community guidelines
- Does not include sensitive or controversial content

Generate only the tweet text, no additional formatting or quotes."""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = message.content[0].text.strip()
            
            # Ensure content is within character limit
            if len(content) > max_length:
                content = content[:max_length-3] + "..."
            
            return {
                "content": content,
                "success": True,
                "character_count": len(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate tweet content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_tweet_for_reply(
        self, 
        tweet_text: str, 
        author_username: str,
        personality: str = "friendly"
    ) -> Dict[str, Any]:
        """Analyze a tweet and generate a contextual reply"""
        try:
            system_prompt = f"""You are a {personality} Twitter bot analyzing a tweet to generate an appropriate reply. 

Rules for replies:
- Be genuinely helpful and engaging
- Match the {personality} personality
- Keep replies under 280 characters
- Don't be promotional or spammy
- Add value to the conversation
- Be respectful and considerate
- Only reply if you have something meaningful to contribute
- Avoid controversial topics

Tweet Author: @{author_username}
Tweet Content: "{tweet_text}"

Analyze the tweet and provide:
1. Whether this tweet is worth replying to (true/false)
2. If yes, generate an appropriate reply
3. Explain why this is a good opportunity to engage

Format your response as:
SHOULD_REPLY: [true/false]
REPLY: [your reply text or "N/A"]
REASON: [brief explanation]"""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.6,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this tweet and determine if/how to reply: {tweet_text}"
                    }
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # Parse the structured response
            should_reply = False
            reply_text = ""
            reason = ""
            
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith('SHOULD_REPLY:'):
                    should_reply = 'true' in line.lower()
                elif line.startswith('REPLY:'):
                    reply_text = line.replace('REPLY:', '').strip()
                elif line.startswith('REASON:'):
                    reason = line.replace('REASON:', '').strip()
            
            return {
                "should_reply": should_reply,
                "reply_text": reply_text if reply_text != "N/A" else "",
                "reason": reason,
                "success": True,
                "character_count": len(reply_text) if reply_text else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze tweet for reply: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_content_ideas(
        self, 
        themes: List[str],
        count: int = 5,
        personality: str = "friendly"
    ) -> Dict[str, Any]:
        """Generate content ideas based on themes"""
        try:
            themes_text = ", ".join(themes) if themes else "general interesting topics"
            
            system_prompt = f"""You are a {personality} content creator generating engaging tweet ideas.

Generate {count} diverse tweet ideas about: {themes_text}

Each idea should be:
- Engaging and likely to get interactions
- Appropriate for the {personality} personality
- Different from each other
- Suitable for Twitter's audience
- Include potential hashtags where relevant

Format: Return only the tweet ideas, one per line, numbered 1-{count}."""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                temperature=0.8,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate {count} tweet ideas about {themes_text}"
                    }
                ]
            )
            
            content = message.content[0].text.strip()
            ideas = [line.strip() for line in content.split('\n') if line.strip()]
            
            return {
                "ideas": ideas,
                "count": len(ideas),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to generate content ideas: {e}")
            return {
                "success": False,
                "error": str(e)
            }