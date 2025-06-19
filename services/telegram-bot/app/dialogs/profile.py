from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Back, Column

from ..states import ProfileSG
from ..services.user_service import UserService


async def show_api_keys_placeholder(callback, widget, dialog_manager):
    """Show API keys placeholder message"""
    await callback.message.answer("🔑 API keys will be implemented in future versions")


async def show_settings_placeholder(callback, widget, dialog_manager):
    """Show settings placeholder message"""
    await callback.message.answer("⚙️ Settings will be implemented in future versions")


async def get_profile_data(dialog_manager: DialogManager, **kwargs):
    """Get profile data"""
    telegram_id = dialog_manager.middleware_data['event_from_user'].id
    user_service = UserService()
    
    user_data = await user_service.get_user_with_token(telegram_id)
    if user_data:
        return {
            'user_name': user_data['user'].name or 'Not specified',
            'user_email': user_data['user'].email,
            'user_id': user_data['user'].id,
            'has_token': bool(user_data['token']),
            'token_preview': user_data['token'][:20] + '...' if user_data['token'] else 'None'
        }
    return {'has_account': False}


profile_dialog = Dialog(
    Window(
        Format("👤 <b>User Profile</b>\n\n"
               "Name: {user_name}\n"
               "Email: {user_email}\n"
               "ID: {user_id}\n"
               "API token: {token_preview}\n\n"
               "Status: ✅ Authorized"),
        Column(
            Button(
                Const("🔑 API Keys"),
                id="api_keys",
                on_click=show_api_keys_placeholder
            ),
            Button(
                Const("⚙️ Settings"),
                id="settings", 
                on_click=show_settings_placeholder
            ),
            Back(Const("🏠 Main Menu"))
        ),
        state=ProfileSG.main,
        getter=get_profile_data
    )
) 