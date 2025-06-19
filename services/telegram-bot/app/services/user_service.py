import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from shared_models.models import User, APIToken
from shared_models.database import async_session_local
from .api_client import VexaAPIClient

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing Telegram users and their Vexa accounts"""
    
    def __init__(self):
        self.api_client = VexaAPIClient()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID from database"""
        async with async_session_local() as session:
            # Check if user has telegram_id in their data field
            result = await session.execute(
                select(User).where(User.data['telegram_id'].astext == str(telegram_id))
            )
            return result.scalars().first()
    
    async def link_telegram_account(self, user_id: int, telegram_id: int, telegram_username: Optional[str] = None) -> bool:
        """Link Telegram account to existing Vexa user"""
        async with async_session_local() as session:
            try:
                # Update user's data field with telegram info
                telegram_data = {
                    'telegram_id': str(telegram_id),
                    'telegram_username': telegram_username
                }
                
                await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(data=User.data.op('||')(telegram_data))
                )
                await session.commit()
                logger.info(f"Linked Telegram ID {telegram_id} to user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to link Telegram account: {e}")
                await session.rollback()
                return False
    
    async def register_user_with_telegram(
        self,
        email: str,
        telegram_id: int,
        telegram_username: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Register new user with Telegram account"""
        try:
            # Create user via Admin API
            user_data = await self.api_client.create_user(email, name)
            user_id = user_data.get('id')
            
            if not user_id:
                logger.error("Failed to get user ID from API response")
                return None
            
            # Link Telegram account
            success = await self.link_telegram_account(user_id, telegram_id, telegram_username)
            if not success:
                logger.error("Failed to link Telegram account after user creation")
                return None
            
            # Create API token for the user
            token_data = await self.api_client.create_api_token(user_id)
            
            return {
                'user': user_data,
                'token': token_data.get('token'),
                'linked': True
            }
            
        except Exception as e:
            logger.error(f"Failed to register user with Telegram: {e}")
            return None
    
    async def get_user_api_token(self, user_id: int) -> Optional[str]:
        """Get user's API token"""
        async with async_session_local() as session:
            result = await session.execute(
                select(APIToken).where(APIToken.user_id == user_id).order_by(APIToken.created_at.desc())
            )
            token = result.scalars().first()
            return token.token if token else None
    
    async def get_user_with_token(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user and their API token by Telegram ID"""
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        token = await self.get_user_api_token(user.id)
        return {
            'user': user,
            'token': token
        } 