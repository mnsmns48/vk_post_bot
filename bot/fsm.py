from aiogram.fsm.state import StatesGroup, State


class ListenUser(StatesGroup):
    main_ = State()
    suggest_ = State()
    to_public_ = State()
    to_admin_ = State()
