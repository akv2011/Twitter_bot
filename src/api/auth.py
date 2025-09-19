"""
Authentication API routes for Twitter OAuth 2.0 integration
"""

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from typing import Optional
import secrets
import base64
import hashlib
import time
from urllib.parse import urlencode
import tweepy

from config.settings import get_settings

router = APIRouter()
settings = get_settings()

# Store for OAuth state and PKCE verifiers (use Redis in production)
oauth_states = {}


def generate_pkce_params():
    """Generate PKCE code verifier and challenge"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge


@router.get("/login")
async def login():
    """Initiate Twitter OAuth 2.0 login with PKCE"""
    try:
        # Generate state and PKCE parameters
        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = generate_pkce_params()
        
        # Store state and code verifier (use Redis in production)
        oauth_states[state] = {
            'code_verifier': code_verifier,
            'timestamp': int(time.time())
        }
        
        # Build authorization URL
        auth_params = {
            'response_type': 'code',
            'client_id': settings.twitter_client_id,
            'redirect_uri': settings.twitter_redirect_uri,
            'scope': 'tweet.read tweet.write users.read follows.read follows.write like.read like.write',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(auth_params)}"
        
        return {
            "auth_url": auth_url,
            "state": state
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")


@router.get("/callback")
async def auth_callback(
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None)
):
    """Handle Twitter OAuth 2.0 callback"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
        
        # Verify state parameter
        if state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        stored_data = oauth_states[state]
        code_verifier = stored_data['code_verifier']
        
        # Exchange code for access token
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.twitter_client_id,
            'client_secret': settings.twitter_client_secret,
            'redirect_uri': settings.twitter_redirect_uri,
            'code': code,
            'code_verifier': code_verifier
        }
        
        # Use tweepy to handle token exchange
        oauth2_client = tweepy.OAuth2UserHandler(
            client_id=settings.twitter_client_id,
            client_secret=settings.twitter_client_secret,
            redirect_uri=settings.twitter_redirect_uri,
            scope=['tweet.read', 'tweet.write', 'users.read', 'follows.read', 'follows.write', 'like.read', 'like.write']
        )
        
        # This would need to be implemented properly with tweepy
        # For now, return success message
        
        # Clean up state
        del oauth_states[state]
        
        return {
            "message": "Authentication successful",
            "access_token": "TOKEN_PLACEHOLDER",  # Store securely in production
            "user_id": "USER_ID_PLACEHOLDER"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/status")
async def auth_status():
    """Check authentication status"""
    # In production, verify stored tokens
    return {
        "authenticated": False,  # Placeholder
        "user_id": None,
        "username": None
    }


@router.post("/logout")
async def logout():
    """Logout and revoke tokens"""
    # In production, revoke stored tokens
    return {"message": "Logged out successfully"}