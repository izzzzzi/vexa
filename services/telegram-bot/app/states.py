from aiogram.fsm.state import State, StatesGroup


class MainMenuSG(StatesGroup):
    main = State()


class AuthSG(StatesGroup):
    waiting_email = State()
    registration_complete = State()


class MeetingsSG(StatesGroup):
    list = State()
    create = State()
    create_platform = State()
    create_meeting_id = State()
    create_options = State()
    details = State()


class TranscriptionsSG(StatesGroup):
    meeting_list = State()
    view = State()
    segments = State()


class ProfileSG(StatesGroup):
    main = State()
    api_keys = State()
    settings = State()
    webhook = State() 