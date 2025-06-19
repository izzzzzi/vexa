from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from aiogram_dialog import DialogManager, StartMode

from ..services.user_service import UserService
from ..states import AuthSG


class AuthMiddleware(BaseMiddleware):
    """Middleware to check if user is authenticated"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Skip auth check for start command and auth dialogs
        update: Update = data.get('update')
        if update and update.message and update.message.text == '/start':
            return await handler(event, data)
        
        # Check if user is authenticated
        telegram_user = data.get('event_from_user')
        if telegram_user:
            user_service = UserService()
            user_data = await user_service.get_user_with_token(telegram_user.id)
            
            if not user_data:
                # User not authenticated, redirect to auth dialog
                dialog_manager = data.get('dialog_manager')
                if dialog_manager and not isinstance(dialog_manager, type(None)):
                    await dialog_manager.start(AuthSG.waiting_email, mode=StartMode.RESET_STACK)
                    return
        
        return await handler(event, data) 