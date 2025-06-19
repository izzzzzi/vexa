from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.input import TextInput

from ..states import AuthSG, MainMenuSG
from ..services.user_service import UserService


async def email_input_handler(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str
):
    """Handle email input for registration"""
    user_service = UserService()
    telegram_user = message.from_user
    
    # Validate email format (basic)
    if '@' not in text or '.' not in text:
        await message.answer("❌ Please enter a valid email address")
        return
    
    try:
        # Register user with Telegram
        result = await user_service.register_user_with_telegram(
            email=text,
            telegram_id=telegram_user.id,
            telegram_username=telegram_user.username,
            name=telegram_user.full_name
        )
        
        if result:
            dialog_manager.dialog_data['user'] = result['user']
            dialog_manager.dialog_data['token'] = result['token']
            await dialog_manager.switch_to(AuthSG.registration_complete)
        else:
            await message.answer("❌ Registration error. Please try again.")
            
    except Exception as e:
        await message.answer(f"❌ An error occurred: {str(e)}")


async def get_auth_data(dialog_manager: DialogManager, **kwargs):
    """Get data for auth dialog"""
    user_data = dialog_manager.dialog_data.get('user', {})
    return {
        'user_email': user_data.get('email', ''),
        'user_name': user_data.get('name', 'User')
    }


auth_dialog = Dialog(
    Window(
        Const("🔐 <b>Welcome to Vexa!</b>\n\n"
              "To get started, you need to link your account.\n"
              "Enter the email you used to register in Vexa, "
              "or a new email to create an account:"),
        TextInput(
            id="email_input",
            on_success=email_input_handler
        ),
        state=AuthSG.waiting_email,
    ),
    Window(
        Format("✅ <b>Registration completed!</b>\n\n"
               "Welcome, {user_name}!\n"
               "Email: {user_email}\n\n"
               "You can now use all Vexa features through this Telegram bot."),
        Start(
            Const("🚀 Go to main menu"),
            id="to_main_menu",
            state=MainMenuSG.main
        ),
        state=AuthSG.registration_complete,
        getter=get_auth_data
    )
) 