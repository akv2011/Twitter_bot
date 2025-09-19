"""
Configuration management API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from src.services.scheduler_service import get_scheduler

router = APIRouter()


class ScheduleConfig(BaseModel):
    """Schedule configuration model"""
    enabled: bool = True
    interval_hours: int = 2
    interval_days: int = 0
    timezone: str = "UTC"


class TargetAccount(BaseModel):
    """Target account model for monitoring"""
    username: str
    user_id: Optional[str] = None
    enabled: bool = True
    reply_enabled: bool = True


class ContentConfig(BaseModel):
    """Content configuration model"""
    themes: List[str] = []
    personality: str = "friendly"
    content_types: List[str] = ["tips", "thoughts", "questions"]
    max_length: int = 280


class BotConfig(BaseModel):
    """Bot configuration model"""
    schedule: ScheduleConfig
    target_accounts: List[TargetAccount]
    content: ContentConfig
    enabled: bool = True


# In-memory storage (use database in production)
bot_config = BotConfig(
    schedule=ScheduleConfig(),
    target_accounts=[],
    content=ContentConfig()
)


@router.get("/", response_model=BotConfig)
async def get_config():
    """Get current bot configuration"""
    return bot_config


@router.put("/", response_model=BotConfig)
async def update_config(config: BotConfig, scheduler=Depends(get_scheduler)):
    """Update bot configuration"""
    try:
        global bot_config
        bot_config = config
        
        # Update scheduler if config changed
        if config.enabled:
            await _update_scheduler_jobs(scheduler)
        else:
            await _stop_scheduler_jobs(scheduler)
        
        return bot_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@router.get("/schedule", response_model=ScheduleConfig)
async def get_schedule():
    """Get schedule configuration"""
    return bot_config.schedule


@router.put("/schedule", response_model=ScheduleConfig)
async def update_schedule(schedule: ScheduleConfig, scheduler=Depends(get_scheduler)):
    """Update schedule configuration"""
    try:
        bot_config.schedule = schedule
        
        # Reschedule jobs with new settings
        if bot_config.enabled and schedule.enabled:
            await _update_scheduler_jobs(scheduler)
        
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")


@router.get("/targets", response_model=List[TargetAccount])
async def get_target_accounts():
    """Get target accounts for monitoring"""
    return bot_config.target_accounts


@router.post("/targets", response_model=TargetAccount)
async def add_target_account(account: TargetAccount, scheduler=Depends(get_scheduler)):
    """Add a target account for monitoring"""
    try:
        # Check if account already exists
        for existing in bot_config.target_accounts:
            if existing.username == account.username:
                raise HTTPException(status_code=400, detail="Account already exists")
        
        bot_config.target_accounts.append(account)
        
        # Update monitoring schedule
        if bot_config.enabled:
            await _update_scheduler_jobs(scheduler)
        
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add target account: {str(e)}")


@router.delete("/targets/{username}")
async def remove_target_account(username: str, scheduler=Depends(get_scheduler)):
    """Remove a target account"""
    try:
        bot_config.target_accounts = [
            acc for acc in bot_config.target_accounts 
            if acc.username != username
        ]
        
        # Update monitoring schedule
        if bot_config.enabled:
            await _update_scheduler_jobs(scheduler)
        
        return {"message": f"Account {username} removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove target account: {str(e)}")


@router.get("/content", response_model=ContentConfig)
async def get_content_config():
    """Get content configuration"""
    return bot_config.content


@router.put("/content", response_model=ContentConfig)
async def update_content_config(content: ContentConfig):
    """Update content configuration"""
    try:
        bot_config.content = content
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update content config: {str(e)}")


@router.post("/start")
async def start_bot(scheduler=Depends(get_scheduler)):
    """Start the bot"""
    try:
        bot_config.enabled = True
        await _update_scheduler_jobs(scheduler)
        return {"message": "Bot started successfully", "status": "running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")


@router.post("/stop")
async def stop_bot(scheduler=Depends(get_scheduler)):
    """Stop the bot"""
    try:
        bot_config.enabled = False
        await _stop_scheduler_jobs(scheduler)
        return {"message": "Bot stopped successfully", "status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")


@router.get("/status")
async def get_bot_status(scheduler=Depends(get_scheduler)):
    """Get bot status"""
    jobs = scheduler.get_jobs()
    
    return {
        "enabled": bot_config.enabled,
        "status": "running" if bot_config.enabled else "stopped",
        "scheduled_jobs": len(jobs),
        "jobs": jobs,
        "target_accounts_count": len(bot_config.target_accounts),
        "next_post": _get_next_job_time(jobs, "content_posting"),
        "next_monitoring": _get_next_job_time(jobs, "account_monitoring")
    }


@router.get("/jobs")
async def get_scheduled_jobs(scheduler=Depends(get_scheduler)):
    """Get all scheduled jobs"""
    return {"jobs": scheduler.get_jobs()}


async def _update_scheduler_jobs(scheduler):
    """Update scheduler jobs based on current configuration"""
    user_id = "default"  # In production, use actual user ID
    
    # Schedule content posting
    if bot_config.schedule.enabled:
        scheduler.schedule_content_posting(
            interval_hours=bot_config.schedule.interval_hours,
            interval_days=bot_config.schedule.interval_days,
            user_id=user_id
        )
    
    # Schedule account monitoring
    if bot_config.target_accounts:
        target_accounts_data = [
            {"username": acc.username, "enabled": acc.enabled, "reply_enabled": acc.reply_enabled}
            for acc in bot_config.target_accounts
            if acc.enabled
        ]
        
        if target_accounts_data:
            scheduler.schedule_account_monitoring(
                target_accounts=target_accounts_data,
                check_interval_hours=2,  # Fixed for now
                user_id=user_id
            )


async def _stop_scheduler_jobs(scheduler):
    """Stop all scheduler jobs"""
    user_id = "default"
    
    scheduler.remove_job(f"content_posting_{user_id}")
    scheduler.remove_job(f"account_monitoring_{user_id}")


def _get_next_job_time(jobs: list, job_type: str) -> Optional[str]:
    """Get next run time for a specific job type"""
    for job in jobs:
        if job_type in job["id"]:
            return job["next_run"]
    return None