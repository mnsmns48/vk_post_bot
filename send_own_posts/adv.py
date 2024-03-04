import asyncio

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.bot_vars import bot


async def dobrotsen_adv():
    dobrotsen_kb = InlineKeyboardBuilder()
    dobrotsen_kb.add(InlineKeyboardButton(
        text='Цены в доброцене',
        callback_data='dobrotsen_go')
    )

    await bot.send_message(chat_id=-1001819403719, text='↓', reply_markup=dobrotsen_kb.as_markup())