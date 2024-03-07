from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb = [
    [KeyboardButton(text="Последние гости")]
]
main_admin = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)
