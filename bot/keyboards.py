from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main_kb = InlineKeyboardBuilder()
main_kb.add(InlineKeyboardButton(
    text='Предложить пост',
    callback_data='suggest')
)
main_kb.add(InlineKeyboardButton(
    text='Написать админу',
    callback_data='to_admin')
)

public = InlineKeyboardBuilder()
public.add(InlineKeyboardButton(
    text='Ошибка! Начать заново',
    callback_data='again')
)
public.add(InlineKeyboardButton(
    text='Опубликовать пост',
    callback_data='public')
)
