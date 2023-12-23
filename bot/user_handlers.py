from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.bot_db_func import write_user

user_ = Router()


async def start(m: Message):
    write_user(m)
    await m.answer_photo(photo='AgACAgIAAxkBAAITZmQlo77a9vGGy1DlE30EBC652E9-AAIyxjEbbWMpSZgCRTKnxt4VAQADAgADeQADLwQ')


def register_user_handlers():
    user_.message.register(start, CommandStart())
