"""Authentication middleware for RD-Agent Gateway."""

import os
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class AuthManager:
    """Manages authentication for the gateway."""
    
    def __init__(self):
        self.enabled = os.getenv("RD_AGENT_AUTH_ENABLED", "false").lower() == "true"
        self.api_keys = self._load_api_keys()
        
    def _load_api_keys(self) -> set:
        """Load API keys from environment variables."""
        api_keys = set()
        
        # Load from environment variable
        env_key = os.getenv("RD_AGENT_API_KEY")
        if env_key:
            api_keys.add(env_key)
            
        # Load multiple keys from comma-separated list
        env_keys = os.getenv("RD_AGENT_API_KEYS")
        if env_keys:
            for key in env_keys.split(","):
                key = key.strip()
                if key:
                    api_keys.add(key)
        
        return api_keys
    
    def validate_token(self, token: str) -> bool:
        """Validate the provided token."""
        if not self.enabled:
            return True
            
        if not self.api_keys:
            logger.warning("Authentication enabled but no API keys configured")
            return False
            
        return token in self.api_keys


# Global auth manager instance
auth_manager = AuthManager()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """Get current user from authorization header."""
    if not auth_manager.enabled:
        return "anonymous"
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "You didn't provide an API key. Please provide your API key via the Authorization header.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": "missing_api_key"
                }
            }
        )
    
    if not auth_manager.validate_token(credentials.credentials):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "message": "Incorrect API key provided.",
                    "type": "invalid_request_error",
                    "param": None,
                    "code": "invalid_api_key"
                }
            }
        )
    
    return "authenticated_user"


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """Get current user from authorization header (optional)."""
    if not auth_manager.enabled:
        return "anonymous"
        
    if not credentials:
        return None
        
    if auth_manager.validate_token(credentials.credentials):
        return "authenticated_user"
        
    return None