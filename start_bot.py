import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from autoposting.db_models import Base
from bot.admin_handler import register_admin_handlers, admin_
from bot.bot_vars import bot, dp
from bot.commands import commands
from bot.user_handlers import register_user_handlers, user_
from cfg_and_engine import engine
from send_own_posts.adv import dbt, register_dbt_handlers
from send_own_posts.scheduler_jobs import send_message1, bot_adv_trigger


async def bot_working():
    async with engine.engine.begin() as async_connect:
        await async_connect.run_sync(Base.metadata.create_all)
    await register_admin_handlers()
    await register_user_handlers()
    await register_dbt_handlers()
    dp.include_routers(admin_, user_, dbt)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_message1, trigger=bot_adv_trigger)
    scheduler.start()
    try:
        print('bot start')
        await dp.start_polling(bot)

    finally:
        print('bot stop')
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(bot_working())
    except KeyboardInterrupt:
        print('Script stopped')
