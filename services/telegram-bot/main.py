import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import setup_dialogs, DialogManager, StartMode

from config import BOT_TOKEN
from app.dialogs.auth import auth_dialog
from app.dialogs.main_menu import main_menu_dialog
from app.dialogs.meetings import meetings_dialog
from app.dialogs.transcriptions import transcriptions_dialog
from app.dialogs.profile import profile_dialog
from app.states import MainMenuSG, AuthSG
from app.services.user_service import UserService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def start_command(message: Message, dialog_manager: DialogManager):
    """Handle /start command"""
    user_service = UserService()
    telegram_user = message.from_user
    
    # Check if user is already registered
    user_data = await user_service.get_user_with_token(telegram_user.id)
    
    if user_data:
        # User is registered, go to main menu
        await dialog_manager.start(MainMenuSG.main, mode=StartMode.RESET_STACK)
    else:
        # User not registered, go to auth dialog
        await dialog_manager.start(AuthSG.waiting_email, mode=StartMode.RESET_STACK)


async def main():
    """Main function to run the bot"""
    logger.info("Starting Vexa Telegram Bot...")
    
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    
    # Register dialogs
    dp.include_router(auth_dialog)
    dp.include_router(main_menu_dialog)
    dp.include_router(meetings_dialog)
    dp.include_router(transcriptions_dialog)
    dp.include_router(profile_dialog)
    
    # Register handlers
    dp.message.register(start_command, CommandStart())
    
    # Setup dialogs
    setup_dialogs(dp)
    
    # Start polling
    logger.info("Bot started successfully!")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main()) 