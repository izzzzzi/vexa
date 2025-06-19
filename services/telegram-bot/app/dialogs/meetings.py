import re
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window, setup_dialogs
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Back, Start, Group, Radio, Column, SwitchTo
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import TextList

from ..states import MeetingsSG, MainMenuSG
from ..services.api_client import VexaAPIClient
from ..services.user_service import UserService


async def refresh_meetings(callback, widget, dialog_manager):
    """Refresh meetings list"""
    await callback.message.edit_text(callback.message.text)


async def get_meetings_data(dialog_manager: DialogManager, **kwargs):
    """Get meetings data for display"""
    try:
        telegram_id = dialog_manager.middleware_data['event_from_user'].id
        user_service = UserService()
        api_client = VexaAPIClient()
        
        user_data = await user_service.get_user_with_token(telegram_id)
        if not user_data or not user_data['token']:
            return {'meetings': [], 'has_meetings': False, 'error': 'No auth'}
        
        # Get user meetings
        meetings = await api_client.get_meetings(user_data['token'])
        running_bots = await api_client.get_running_bots()
        
        formatted_meetings = []
        for meeting in meetings:
            status_emoji = "🟢" if meeting.get('status') == 'active' else "🔴"
            
            # Check if bot is running for this meeting
            bot_running = any(
                bot.get('platform') == meeting.get('platform') and 
                bot.get('native_meeting_id') == meeting.get('native_meeting_id')
                for bot in running_bots
            )
            bot_status = "🤖 Active" if bot_running else "💤 Stopped"
            
            formatted_meetings.append({
                'id': meeting.get('id'),
                'platform': meeting.get('platform', 'unknown'),
                'native_id': meeting.get('native_meeting_id', 'N/A'),
                'status': meeting.get('status', 'unknown'),
                'created_at': meeting.get('created_at', ''),
                'display_text': f"{status_emoji} {meeting.get('platform', 'Unknown')}: {meeting.get('native_meeting_id', 'N/A')[:15]}...",
                'bot_status': bot_status
            })
        
        return {
            'meetings': formatted_meetings,
            'has_meetings': len(formatted_meetings) > 0,
            'meetings_count': len(formatted_meetings)
        }
    except Exception as e:
        return {'meetings': [], 'has_meetings': False, 'error': str(e)}


async def platform_selected(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    item_id: str
):
    """Handle platform selection"""
    dialog_manager.dialog_data['selected_platform'] = item_id
    await dialog_manager.switch_to(MeetingsSG.create_meeting_id)


async def meeting_id_input_handler(
    message: Message,
    widget,
    dialog_manager: DialogManager,
    text: str
):
    """Handle meeting ID input"""
    platform = dialog_manager.dialog_data.get('selected_platform')
    
    # Validate meeting ID format based on platform
    if platform == 'google_meet':
        if not re.match(r'^[a-z]{3}-[a-z]{4}-[a-z]{3}$', text):
            await message.answer("❌ Invalid Google Meet ID format.\nExample: abc-defg-hij")
            return
    
    dialog_manager.dialog_data['meeting_id'] = text
    await dialog_manager.switch_to(MeetingsSG.create_options)


async def create_bot_handler(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager
):
    """Handle bot creation"""
    telegram_id = dialog_manager.middleware_data['event_from_user'].id
    user_service = UserService()
    api_client = VexaAPIClient()
    
    user_data = await user_service.get_user_with_token(telegram_id)
    if not user_data or not user_data['token']:
        await callback.message.answer("❌ Authorization error")
        return
    
    platform = dialog_manager.dialog_data.get('selected_platform')
    meeting_id = dialog_manager.dialog_data.get('meeting_id')
    
    try:
        result = await api_client.create_bot(
            api_key=user_data['token'],
            platform=platform,
            native_meeting_id=meeting_id,
            bot_name="Vexa Assistant",
            language="en"
        )
        
        await callback.message.answer(
            f"✅ <b>Bot created successfully!</b>\n\n"
            f"Platform: {platform}\n"
            f"Meeting ID: {meeting_id}\n"
            f"Status: {result.get('status', 'unknown')}\n\n"
            f"Bot will join the meeting within 10 seconds."
        )
        await dialog_manager.switch_to(MeetingsSG.list)
        
    except Exception as e:
        await callback.message.answer(f"❌ Bot creation error: {str(e)}")


async def get_create_data(dialog_manager: DialogManager, **kwargs):
    """Get data for creation dialog"""
    return {
        'platforms': [
            ('google_meet', 'Google Meet'),
            ('zoom', 'Zoom (coming soon)'),
            ('teams', 'Teams (coming soon)')
        ],
        'selected_platform': dialog_manager.dialog_data.get('selected_platform', ''),
        'meeting_id': dialog_manager.dialog_data.get('meeting_id', '')
    }


meetings_dialog = Dialog(
    # Meetings list
    Window(
        Format("🤖 <b>Bot Management</b>\n\n"
               "{?has_meetings}"
               "Your meetings ({meetings_count}):\n\n"
               "{/has_meetings}"
               "{?not has_meetings}"
               "You don't have any meetings yet.\n"
               "{/not has_meetings}"),
        TextList(
            Format("• {item[display_text]} - {item[bot_status]}"),
            items="meetings",
            id="meetings_list"
        ),
        Column(
            SwitchTo(
                Const("➕ Create Bot"),
                id="create_bot",
                state=MeetingsSG.create_platform
            ),
            Button(
                Const("🔄 Refresh"),
                id="refresh_meetings",
                on_click=refresh_meetings
            ),
            Back(Const("🏠 Main Menu"))
        ),
        state=MeetingsSG.list,
        getter=get_meetings_data
    ),
    
    # Platform selection
    Window(
        Const("🎯 <b>Select meeting platform:</b>"),
        Radio(
            Format("🔘 {item[1]}"),
            Format("⚪ {item[1]}"),
            field="selected_platform",
            items="platforms",
            id="platform_radio",
            on_click=platform_selected
        ),
        Back(Const("◀️ Back")),
        state=MeetingsSG.create_platform,
        getter=get_create_data
    ),
    
    # Meeting ID input
    Window(
        Format("📝 <b>Enter meeting ID for {selected_platform}:</b>\n\n"
               "{?selected_platform == 'google_meet'}"
               "For Google Meet, enter the code from the link:\n"
               "https://meet.google.com/<b>abc-defg-hij</b>\n\n"
               "Format: abc-defg-hij"
               "{/selected_platform == 'google_meet'}"
               "{?selected_platform == 'zoom'}"
               "For Zoom, enter meeting ID:\n"
               "Format: 1234567890"
               "{/selected_platform == 'zoom'}"),
        TextInput(
            id="meeting_id_input",
            on_success=meeting_id_input_handler
        ),
        Back(Const("◀️ Back")),
        state=MeetingsSG.create_meeting_id,
        getter=get_create_data
    ),
    
    # Creation options and confirmation
    Window(
        Format("🚀 <b>Creating Bot</b>\n\n"
               "Platform: {selected_platform}\n"
               "Meeting ID: {meeting_id}\n\n"
               "Settings:\n"
               "• Bot name: Vexa Assistant\n"
               "• Language: English\n"
               "• Task: Transcription\n\n"
               "Create bot?"),
        Group(
            Button(
                Const("✅ Create Bot"),
                id="confirm_create",
                on_click=create_bot_handler
            ),
            Back(Const("◀️ Back"))
        ),
        state=MeetingsSG.create_options,
        getter=get_create_data
    )
) 