"""
Tweet management API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import tweepy

from config.settings import get_settings
from src.services.claude_service import ClaudeService

router = APIRouter()
settings = get_settings()


class TweetGenerate(BaseModel):
    """Tweet generation request model"""
    prompt: str
    theme: Optional[str] = "general"
    personality: Optional[str] = "friendly"
    max_length: Optional[int] = 280


class TweetCreate(BaseModel):
    """Tweet creation request model"""
    text: str
    reply_to_id: Optional[str] = None
    media_ids: Optional[List[str]] = None


class TweetResponse(BaseModel):
    """Tweet response model"""
    id: str
    text: str
    created_at: str
    author_id: str
    public_metrics: Optional[dict] = None


# Placeholder for Twitter API client (will be implemented with proper auth)
def get_twitter_client():
    """Get authenticated Twitter API client"""
    # This will be properly implemented with stored user tokens
    return None


@router.post("/generate")
async def generate_tweet_content(request: TweetGenerate):
    """Generate tweet content using AI"""
    try:
        claude_service = ClaudeService()
        
        result = await claude_service.generate_tweet_content(
            prompt=request.prompt,
            theme=request.theme,
            personality=request.personality,
            max_length=request.max_length
        )
        
        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "length": len(result["content"])
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate content: {str(e)}")


@router.post("/", response_model=TweetResponse)
async def create_tweet(tweet: TweetCreate, client=Depends(get_twitter_client)):
    """Create a new tweet"""
    try:
        if not client:
            raise HTTPException(status_code=401, detail="Not authenticated with Twitter")
        
        # For now, return a mock response
        return TweetResponse(
            id="1234567890",
            text=tweet.text,
            created_at="2025-09-20T00:00:00Z",
            author_id="user123",
            public_metrics={"retweet_count": 0, "like_count": 0, "reply_count": 0}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tweet: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_tweets(user_id: str, max_results: int = 10):
    """Get tweets from a specific user"""
    try:
        # This will be implemented with proper Twitter API calls
        return {
            "data": [],
            "meta": {"result_count": 0, "next_token": None}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tweets: {str(e)}")


@router.post("/{tweet_id}/like")
async def like_tweet(tweet_id: str, client=Depends(get_twitter_client)):
    """Like a tweet"""
    try:
        if not client:
            raise HTTPException(status_code=401, detail="Not authenticated with Twitter")
        
        # Implement with Twitter API
        return {"message": f"Tweet {tweet_id} liked successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to like tweet: {str(e)}")


@router.post("/{tweet_id}/reply")
async def reply_to_tweet(tweet_id: str, reply: TweetCreate, client=Depends(get_twitter_client)):
    """Reply to a tweet"""
    try:
        if not client:
            raise HTTPException(status_code=401, detail="Not authenticated with Twitter")
        
        # Set the reply_to_id for the reply
        reply.reply_to_id = tweet_id
        
        # For now, return a mock response
        return TweetResponse(
            id="1234567891",
            text=reply.text,
            created_at="2025-09-20T00:00:00Z",
            author_id="user123"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reply to tweet: {str(e)}")


@router.get("/timeline")
async def get_timeline(max_results: int = 10, client=Depends(get_twitter_client)):
    """Get user's timeline"""
    try:
        if not client:
            raise HTTPException(status_code=401, detail="Not authenticated with Twitter")
        
        # This will be implemented with proper Twitter API calls
        return {
            "data": [],
            "meta": {"result_count": 0, "next_token": None}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timeline: {str(e)}")