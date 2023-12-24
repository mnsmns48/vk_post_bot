import logging
import sys

from bot.bot_vars import bot, dp
from bot.commands import commands
from bot.user_handlers import register_user_handlers, user_


async def bot_working():
    register_user_handlers()
    dp.include_routers(user_)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands)
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
