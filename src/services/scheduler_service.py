"""
Scheduler service for managing automated tasks
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SchedulerService:
    """Service for managing scheduled tasks"""
    
    def __init__(self):
        # Configure job stores, executors and job defaults
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.database_url)
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=settings.timezone
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        
        self._running = False
    
    async def start(self):
        """Start the scheduler"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("Scheduler started successfully")
    
    async def stop(self):
        """Stop the scheduler"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            logger.info("Scheduler stopped")
    
    def _job_executed(self, event):
        """Handle job execution event"""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event):
        """Handle job error event"""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    
    def schedule_content_posting(
        self, 
        interval_hours: int = 2,
        interval_days: int = 0,
        user_id: str = "default"
    ) -> str:
        """Schedule automated content posting"""
        job_id = f"content_posting_{user_id}"
        
        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # Calculate interval
        if interval_days > 0:
            # Use interval trigger for days
            self.scheduler.add_job(
                func=self._post_content_job,
                trigger="interval",
                days=interval_days,
                id=job_id,
                args=[user_id],
                replace_existing=True,
                next_run_time=datetime.now() + timedelta(minutes=1)  # Start in 1 minute
            )
        else:
            # Use interval trigger for hours
            self.scheduler.add_job(
                func=self._post_content_job,
                trigger="interval",
                hours=interval_hours,
                id=job_id,
                args=[user_id],
                replace_existing=True,
                next_run_time=datetime.now() + timedelta(minutes=1)  # Start in 1 minute
            )
        
        logger.info(f"Scheduled content posting every {interval_days} days, {interval_hours} hours for user {user_id}")
        return job_id
    
    def schedule_account_monitoring(
        self, 
        target_accounts: list,
        check_interval_hours: int = 2,
        user_id: str = "default"
    ) -> str:
        """Schedule automated account monitoring"""
        job_id = f"account_monitoring_{user_id}"
        
        # Remove existing job if it exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        self.scheduler.add_job(
            func=self._monitor_accounts_job,
            trigger="interval",
            hours=check_interval_hours,
            id=job_id,
            args=[target_accounts, user_id],
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(minutes=2)  # Start in 2 minutes
        )
        
        logger.info(f"Scheduled account monitoring every {check_interval_hours} hours for {len(target_accounts)} accounts")
        return job_id
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def get_jobs(self) -> list:
        """Get all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    async def _post_content_job(self, user_id: str):
        """Background job for posting content"""
        try:
            logger.info(f"Starting content posting job for user {user_id}")
            
            # Import here to avoid circular imports
            from src.services.claude_service import ClaudeService
            from src.services.twitter_service import TwitterService
            
            # Initialize services
            claude_service = ClaudeService()
            twitter_service = TwitterService()  # Will need user tokens
            
            # Generate content
            content_result = await claude_service.generate_tweet_content(
                prompt="Generate an engaging and interesting tweet",
                theme="technology and innovation",
                personality="friendly"
            )
            
            if content_result["success"]:
                # Post the tweet
                tweet_result = await twitter_service.post_tweet(content_result["content"])
                
                if tweet_result["success"]:
                    logger.info(f"Successfully posted automated tweet: {content_result['content']}")
                else:
                    logger.error(f"Failed to post tweet: {tweet_result['error']}")
            else:
                logger.error(f"Failed to generate content: {content_result['error']}")
                
        except Exception as e:
            logger.error(f"Content posting job failed: {e}")
    
    async def _monitor_accounts_job(self, target_accounts: list, user_id: str):
        """Background job for monitoring target accounts"""
        try:
            logger.info(f"Starting account monitoring job for user {user_id}")
            
            # Import here to avoid circular imports
            from src.services.twitter_service import TwitterService
            from src.services.claude_service import ClaudeService
            
            twitter_service = TwitterService()  # Will need user tokens
            claude_service = ClaudeService()
            
            for account in target_accounts:
                try:
                    username = account.get("username")
                    if not username:
                        continue
                    
                    logger.info(f"Monitoring account: {username}")
                    
                    # Get user info
                    user_info = await twitter_service.get_user_by_username(username)
                    if not user_info or not user_info["success"]:
                        continue
                    
                    user_id_target = user_info["id"]
                    
                    # Get recent tweets
                    tweets_result = await twitter_service.get_user_tweets(user_id_target, max_results=5)
                    
                    if tweets_result["success"] and tweets_result["data"]:
                        for tweet in tweets_result["data"]:
                            # Analyze tweet for potential reply
                            analysis = await claude_service.analyze_tweet_for_reply(
                                tweet_text=tweet.text,
                                author_username=username
                            )
                            
                            if analysis["success"] and analysis["should_reply"]:
                                # Post reply
                                reply_result = await twitter_service.post_tweet(
                                    text=analysis["reply_text"],
                                    reply_to_id=tweet.id
                                )
                                
                                if reply_result["success"]:
                                    logger.info(f"Posted reply to {username}: {analysis['reply_text']}")
                                else:
                                    logger.error(f"Failed to post reply: {reply_result['error']}")
                                
                                # Only reply to one tweet per account per monitoring cycle
                                break
                    
                except Exception as e:
                    logger.error(f"Error monitoring account {username}: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"Account monitoring job failed: {e}")


# Global scheduler instance
scheduler_service = SchedulerService()


def get_scheduler() -> SchedulerService:
    """Get the scheduler service instance"""
    return scheduler_service