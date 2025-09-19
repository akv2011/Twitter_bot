"""
Configuration management for Twitter Bot
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable loading"""
    
    # Twitter API Configuration
    twitter_client_id: str = Field(..., env="TWITTER_CLIENT_ID")
    twitter_client_secret: str = Field(..., env="TWITTER_CLIENT_SECRET") 
    twitter_redirect_uri: str = Field(default="http://localhost:8000/auth/callback", env="TWITTER_REDIRECT_URI")
    twitter_bearer_token: str = Field(..., env="TWITTER_BEARER_TOKEN")
    twitter_access_token: str = Field(..., env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: str = Field(..., env="TWITTER_ACCESS_TOKEN_SECRET")
    
    # Claude AI Configuration
    claude_api_key: str = Field(..., env="CLAUDE_API_KEY")
    
    # Application Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="localhost", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./twitter_bot.db", env="DATABASE_URL")
    
    # Scheduling Configuration
    timezone: str = Field(default="UTC", env="TIMEZONE")
    default_post_interval_hours: int = Field(default=2, env="DEFAULT_POST_INTERVAL_HOURS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/twitter_bot.log", env="LOG_FILE")
    
    # Security Configuration
    token_expire_hours: int = Field(default=24, env="TOKEN_EXPIRE_HOURS")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance"""
    return settings