"""
Database models for Twitter Bot
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from config.settings import get_settings

settings = get_settings()

Base = declarative_base()


class User(Base):
    """User model for storing Twitter user information and tokens"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    twitter_user_id = Column(String(50), unique=True, index=True)
    username = Column(String(50), index=True)
    display_name = Column(String(100))
    
    # OAuth tokens
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    
    # User preferences
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BotConfiguration(Base):
    """Bot configuration for each user"""
    __tablename__ = "bot_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Reference to User.id
    
    # Scheduling configuration
    posting_enabled = Column(Boolean, default=True)
    posting_interval_hours = Column(Integer, default=2)
    posting_interval_days = Column(Integer, default=0)
    timezone = Column(String(50), default="UTC")
    
    # Content configuration
    content_themes = Column(JSON)  # List of themes
    personality = Column(String(50), default="friendly")
    content_types = Column(JSON)  # List of content types
    max_tweet_length = Column(Integer, default=280)
    
    # Monitoring configuration
    monitoring_enabled = Column(Boolean, default=True)
    monitoring_interval_hours = Column(Integer, default=2)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TargetAccount(Base):
    """Target accounts to monitor for each user"""
    __tablename__ = "target_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Reference to User.id
    
    target_username = Column(String(50), index=True)
    target_user_id = Column(String(50))
    enabled = Column(Boolean, default=True)
    reply_enabled = Column(Boolean, default=True)
    
    # Monitoring stats
    last_checked_at = Column(DateTime)
    last_tweet_id = Column(String(50))  # Last tweet ID seen
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """Log of all bot activities"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    
    activity_type = Column(String(50))  # 'post', 'reply', 'like', 'follow', 'error'
    description = Column(Text)
    
    # Tweet information
    tweet_id = Column(String(50))
    tweet_text = Column(Text)
    target_username = Column(String(50))
    
    # Result information
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Metadata
    extra_data = Column(JSON)  # Additional data as JSON
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()