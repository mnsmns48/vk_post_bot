import logging
import sys

from bot.admin_handler import register_admin_handlers, admin_
from bot.bot_vars import bot, dp
from bot.commands import commands
from bot.user_handlers import register_user_handlers, user_


async def bot_working():
    await register_admin_handlers()
    await register_user_handlers()
    dp.include_routers(admin_, user_)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands)
    try:
        print('bot start')
        await dp.start_polling(bot)
    finally:
        print('bot stop')
        await bot.session.close()
