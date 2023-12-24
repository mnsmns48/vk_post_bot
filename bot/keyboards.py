from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.add(InlineKeyboardButton(
    text='Предложить пост',
    callback_data='suggest')
)
builder.add(InlineKeyboardButton(
    text='Написать админу',
    callback_data='to_admin')
)
