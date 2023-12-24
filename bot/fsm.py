from aiogram.fsm.state import StatesGroup, State


class ListenUser(StatesGroup):
    suggest_state = State()
    to_admin = State()
