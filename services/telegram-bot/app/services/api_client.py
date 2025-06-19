import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import API_GATEWAY_URL, ADMIN_API_URL, ADMIN_API_TOKEN

logger = logging.getLogger(__name__)


class VexaAPIClient:
    """Client for interacting with Vexa API"""
    
    def __init__(self):
        self.gateway_url = API_GATEWAY_URL
        self.admin_url = ADMIN_API_URL
        self.admin_token = ADMIN_API_TOKEN
        
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Vexa API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"API request failed: {e}")
                raise
    
    # User Management (Admin API)
    async def create_user(self, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create or find user by email"""
        headers = {"X-Admin-API-Key": self.admin_token}
        data = {"email": email}
        if name:
            data["name"] = name
            
        return await self._make_request(
            "POST",
            f"{self.admin_url}/admin/users",
            headers=headers,
            json_data=data
        )
    
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email"""
        headers = {"X-Admin-API-Key": self.admin_token}
        return await self._make_request(
            "GET",
            f"{self.admin_url}/admin/users/email/{email}",
            headers=headers
        )
    
    async def create_api_token(self, user_id: int) -> Dict[str, Any]:
        """Create new API token for user"""
        headers = {"X-Admin-API-Key": self.admin_token}
        return await self._make_request(
            "POST",
            f"{self.admin_url}/admin/users/{user_id}/tokens",
            headers=headers
        )
    
    # Bot Management (User API)
    async def create_bot(
        self,
        api_key: str,
        platform: str,
        native_meeting_id: str,
        bot_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create bot for meeting"""
        headers = {"X-API-Key": api_key}
        data = {
            "platform": platform,
            "native_meeting_id": native_meeting_id
        }
        if bot_name:
            data["bot_name"] = bot_name
        if language:
            data["language"] = language
            
        return await self._make_request(
            "POST",
            f"{self.gateway_url}/bots",
            headers=headers,
            json_data=data
        )
    
    async def stop_bot(
        self,
        api_key: str,
        platform: str,
        native_meeting_id: str
    ) -> Dict[str, Any]:
        """Stop bot for meeting"""
        headers = {"X-API-Key": api_key}
        return await self._make_request(
            "DELETE",
            f"{self.gateway_url}/bots/{platform}/{native_meeting_id}",
            headers=headers
        )
    
    async def get_bot_status(self, api_key: str) -> Dict[str, Any]:
        """Get status of running bots"""
        headers = {"X-API-Key": api_key}
        return await self._make_request(
            "GET",
            f"{self.gateway_url}/bots/status",
            headers=headers
        )
    
    # Meetings and Transcriptions
    async def get_meetings(self, api_key: str) -> Dict[str, Any]:
        """Get user's meetings"""
        headers = {"X-API-Key": api_key}
        return await self._make_request(
            "GET",
            f"{self.gateway_url}/meetings",
            headers=headers
        )
    
    async def get_transcript(
        self,
        api_key: str,
        platform: str,
        native_meeting_id: str
    ) -> Dict[str, Any]:
        """Get transcript for meeting"""
        headers = {"X-API-Key": api_key}
        return await self._make_request(
            "GET",
            f"{self.gateway_url}/transcripts/{platform}/{native_meeting_id}",
            headers=headers
        ) 