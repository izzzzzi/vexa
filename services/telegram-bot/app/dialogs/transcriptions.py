from typing import Any, Dict
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format, List as TextList
from aiogram_dialog.widgets.kbd import Button, Back, Select, Group, Column, SwitchTo

from ..states import TranscriptionsSG, MainMenuSG
from ..services.user_service import UserService
from ..services.api_client import VexaAPIClient


async def refresh_transcriptions(callback, widget, dialog_manager):
    """Refresh transcriptions list"""
    await callback.message.edit_text(callback.message.text)


async def refresh_transcript(callback, widget, dialog_manager):
    """Refresh transcript data"""
    await callback.message.edit_text(callback.message.text)


async def get_meetings_for_transcription(dialog_manager: DialogManager, **kwargs):
    """Get meetings data for transcription viewing"""
    telegram_id = dialog_manager.middleware_data['event_from_user'].id
    user_service = UserService()
    api_client = VexaAPIClient()
    
    user_data = await user_service.get_user_with_token(telegram_id)
    if not user_data or not user_data['token']:
        return {'meetings': [], 'has_meetings': False}
    
    try:
        meetings_response = await api_client.get_meetings(user_data['token'])
        meetings = meetings_response.get('meetings', [])
        
        # Filter meetings that have transcriptions (status completed or active)
        transcription_meetings = []
        for meeting in meetings:
            if meeting.get('status') in ['active', 'completed']:
                platform_emoji = {
                    'google_meet': '🎥',
                    'zoom': '📹', 
                    'teams': '💼'
                }.get(meeting.get('platform'), '📱')
                
                transcription_meetings.append({
                    'id': f"{meeting.get('platform')}_{meeting.get('native_meeting_id')}",
                    'platform': meeting.get('platform'),
                    'native_id': meeting.get('native_meeting_id'),
                    'created_at': meeting.get('created_at', ''),
                    'status': meeting.get('status'),
                    'display_text': f"{platform_emoji} {meeting.get('platform', 'Unknown')}: {meeting.get('native_meeting_id', 'N/A')[:20]}",
                    'date': meeting.get('created_at', '')[:10] if meeting.get('created_at') else 'N/A'
                })
        
        return {
            'meetings': transcription_meetings[:20],  # Limit to 20 meetings
            'has_meetings': len(transcription_meetings) > 0,
            'count': len(transcription_meetings)
        }
    except Exception as e:
        return {'meetings': [], 'has_meetings': False, 'error': str(e)}


async def meeting_selected_for_transcript(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    item_id: str
):
    """Handle meeting selection for transcript viewing"""
    # Parse meeting ID to get platform and native_id
    platform, native_id = item_id.split('_', 1)
    dialog_manager.dialog_data['selected_platform'] = platform
    dialog_manager.dialog_data['selected_meeting_id'] = native_id
    await dialog_manager.switch_to(TranscriptionsSG.view)


async def get_transcript_data(dialog_manager: DialogManager, **kwargs):
    """Get transcript data for viewing"""
    telegram_id = dialog_manager.middleware_data['event_from_user'].id
    user_service = UserService()
    api_client = VexaAPIClient()
    
    user_data = await user_service.get_user_with_token(telegram_id)
    if not user_data or not user_data['token']:
        return {'segments': [], 'has_segments': False}
    
    platform = dialog_manager.dialog_data.get('selected_platform')
    meeting_id = dialog_manager.dialog_data.get('selected_meeting_id')
    
    if not platform or not meeting_id:
        return {'segments': [], 'has_segments': False}
    
    try:
        transcript_response = await api_client.get_transcript(
            api_key=user_data['token'],
            platform=platform,
            native_meeting_id=meeting_id
        )
        
        segments = transcript_response.get('segments', [])
        
        # Format segments for display
        formatted_segments = []
        for i, segment in enumerate(segments[:50]):  # Limit to 50 segments
            # Format time
            start_time = segment.get('start_time', 0)
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            speaker = segment.get('speaker', 'Unknown')
            text = segment.get('text', '').strip()
            
            if text:
                formatted_segments.append({
                    'id': i,
                    'time': time_str,
                    'speaker': speaker,
                    'text': text[:200] + ('...' if len(text) > 200 else ''),
                    'full_text': text
                })
        
        return {
            'segments': formatted_segments,
            'has_segments': len(formatted_segments) > 0,
            'platform': platform,
            'meeting_id': meeting_id,
            'total_segments': len(segments),
            'showing_segments': len(formatted_segments)
        }
    except Exception as e:
        return {
            'segments': [], 
            'has_segments': False, 
            'error': str(e),
            'platform': platform,
            'meeting_id': meeting_id
        }


transcriptions_dialog = Dialog(
    # Meetings list for transcription viewing
    Window(
        Format("📝 <b>Meeting Transcriptions</b>\n\n"
               "{?has_meetings}"
               "Select a meeting to view transcription ({count}):\n\n"
               "{/has_meetings}"
               "{?not has_meetings}"
               "You don't have any meetings with transcriptions yet.\n"
               "Create a bot for a meeting to get transcription."
               "{/not has_meetings}"),
        Select(
            Format("{item[display_text]} ({item[date]})"),
            id="meeting_select",
            item_id_getter=lambda item: item['id'],
            items="meetings",
            on_click=meeting_selected_for_transcript
        ),
        Column(
            Button(
                Const("🔄 Refresh"),
                id="refresh_transcriptions",
                on_click=refresh_transcriptions
            ),
            Back(Const("🏠 Main Menu"))
        ),
        state=TranscriptionsSG.meeting_list,
        getter=get_meetings_for_transcription
    ),
    
    # Transcript viewing
    Window(
        Format("📄 <b>Meeting Transcription</b>\n\n"
               "Platform: {platform}\n"
               "Meeting ID: {meeting_id}\n\n"
               "{?has_segments}"
               "Showing {showing_segments} of {total_segments} segments:\n\n"
               "{/has_segments}"
               "{?not has_segments}"
               "Transcription is not available yet.\n"
               "Meeting may not have started or bot is not connected."
               "{/not has_segments}"
               "{?error}"
               "Error: {error}"
               "{/error}"),
        TextList(
            Format("<b>[{item[time]}] {item[speaker]}:</b>\n{item[text]}\n"),
            items="segments",
            id="segments_list"
        ),
        Group(
            SwitchTo(
                Const("📄 Full transcript"),
                id="full_transcript",
                state=TranscriptionsSG.segments
            ),
            Button(
                Const("🔄 Refresh"),
                id="refresh_transcript",
                on_click=refresh_transcript
            ),
            Back(Const("◀️ Back to meetings list"))
        ),
        state=TranscriptionsSG.view,
        getter=get_transcript_data
    ),
    
    # Full transcript segments view
    Window(
        Format("📋 <b>Full Transcription</b>\n\n"
               "Meeting: {platform} - {meeting_id}\n"
               "Total segments: {total_segments}\n\n"),
        TextList(
            Format("<b>{item[time]} | {item[speaker]}:</b>\n{item[full_text]}\n"),
            items="segments",
            id="full_segments_list"
        ),
        Back(Const("◀️ Back")),
        state=TranscriptionsSG.segments,
        getter=get_transcript_data
    )
) 