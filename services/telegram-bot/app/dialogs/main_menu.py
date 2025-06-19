from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Start, Column

from ..states import MainMenuSG, MeetingsSG, TranscriptionsSG, ProfileSG
from ..services.user_service import UserService


async def show_help(callback, widget, dialog_manager):
    """Show help information"""
    await callback.message.answer(
        "📖 <b>Vexa Bot Help</b>\n\n"
        "🤖 <b>Bot Management</b> - create bots for meeting transcription\n"
        "📝 <b>Transcriptions</b> - view your meeting recordings\n"
        "👤 <b>Profile</b> - manage your account settings\n\n"
        "Vexa supports:\n"
        "• Google Meet\n"
        "• Zoom (coming soon)\n"
        "• Microsoft Teams (coming soon)\n\n"
        "To create a bot, just enter the meeting link!"
    )


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    """Get data for main menu"""
    telegram_id = dialog_manager.middleware_data['event_from_user'].id
    user_service = UserService()
    
    user_data = await user_service.get_user_with_token(telegram_id)
    if user_data:
        return {
            'user_name': user_data['user'].name or 'User',
            'user_email': user_data['user'].email,
            'has_account': True
        }
    else:
        return {'has_account': False}


main_menu_dialog = Dialog(
    Window(
        Format("🏠 <b>Vexa Main Menu</b>\n\n"
               "Hello, {user_name}!\n"
               "Welcome to the Vexa meeting transcription system.\n\n"
               "Choose an action:"),
        Column(
            Start(
                Const("🤖 Bot Management"),
                id="meetings_menu",
                state=MeetingsSG.list
            ),
            Start(
                Const("📝 Transcriptions"),
                id="transcriptions_menu", 
                state=TranscriptionsSG.meeting_list
            ),
            Start(
                Const("👤 Profile"),
                id="profile_menu",
                state=ProfileSG.main
            ),
            Button(
                Const("ℹ️ Help"),
                id="help_button",
                on_click=show_help
            )
        ),
        state=MainMenuSG.main,
        getter=get_main_menu_data
    )
) 