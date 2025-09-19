"""
Twitter API service for handling Twitter interactions
"""

import tweepy
from typing import Optional, List, Dict, Any
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class TwitterService:
    """Service for Twitter API interactions"""
    
    def __init__(self, access_token: Optional[str] = None, access_token_secret: Optional[str] = None):
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self._client_v2 = None
        self._client_v1 = None
    
    @property
    def client_v2(self) -> Optional[tweepy.Client]:
        """Get Twitter API v2 client"""
        if not self._client_v2 and self.access_token:
            try:
                self._client_v2 = tweepy.Client(
                    bearer_token=None,  # Will be set with proper OAuth
                    consumer_key=settings.twitter_client_id,
                    consumer_secret=settings.twitter_client_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
            except Exception as e:
                logger.error(f"Failed to create Twitter client: {e}")
        return self._client_v2
    
    async def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
        """Post a tweet"""
        try:
            if not self.client_v2:
                raise Exception("Twitter client not authenticated")
            
            response = self.client_v2.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_id
            )
            
            return {
                "id": response.data["id"],
                "text": text,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_tweets(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """Get tweets from a user"""
        try:
            if not self.client_v2:
                raise Exception("Twitter client not authenticated")
            
            tweets = self.client_v2.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            return {
                "data": tweets.data or [],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to get user tweets: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def like_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Like a tweet"""
        try:
            if not self.client_v2:
                raise Exception("Twitter client not authenticated")
            
            # Get authenticated user ID (this would be stored from OAuth)
            me = self.client_v2.get_me()
            user_id = me.data.id
            
            response = self.client_v2.like(tweet_id=tweet_id, user_id=user_id)
            
            return {
                "success": True,
                "liked": response.data.get("liked", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to like tweet: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def follow_user(self, target_user_id: str) -> Dict[str, Any]:
        """Follow a user"""
        try:
            if not self.client_v2:
                raise Exception("Twitter client not authenticated")
            
            # Get authenticated user ID
            me = self.client_v2.get_me()
            user_id = me.data.id
            
            response = self.client_v2.follow_user(target_user_id=target_user_id, user_id=user_id)
            
            return {
                "success": True,
                "following": response.data.get("following", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to follow user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username"""
        try:
            if not self.client_v2:
                raise Exception("Twitter client not authenticated")
            
            user = self.client_v2.get_user(username=username)
            
            if user.data:
                return {
                    "id": user.data.id,
                    "username": user.data.username,
                    "name": user.data.name,
                    "success": True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return {
                "success": False,
                "error": str(e)
            }