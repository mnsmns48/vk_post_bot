from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.admin_keyboards import main_admin
from bot.bot_db_func import last_guests
from config.cfg_and_engine import engine

from bot.filter import AdminFilter

admin_ = Router()


async def start(m: Message):
    await m.answer('Admin Mode', reply_markup=main_admin)


async def upload_pic(m: Message):
    id_photo = m.photo[-1].file_id
    await m.answer('ID на сервере Telegram:')
    await m.answer(id_photo)


async def show_guests(m: Message):
    async with engine.scoped_session() as session:
        answer = await last_guests(session=session)
    await m.answer(text=answer)


async def register_admin_handlers():
    admin_.message.filter(AdminFilter())
    admin_.message.register(start, CommandStart())
    admin_.message.register(upload_pic, F.photo)
    admin_.message.register(show_guests, F.text == "Последние гости")
