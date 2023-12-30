from aiogram.fsm.state import StatesGroup, State


class ListenUser(StatesGroup):
    suggest_ = State()
    to_public_ = State()
    to_admin_ = State()
