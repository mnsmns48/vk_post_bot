import asyncio
from autoposting.db_models import Base
from autoposting.start import start_autoposting
from bot.main_bot import bot_working
from cfg_and_engine import engine
from send_own_posts.adv import dobrotsen_adv


async def main():
    bot_task = asyncio.create_task(bot_working())
    autopost = asyncio.create_task(start_autoposting())
    send_adv = asyncio.create_task(dobrotsen_adv())
    async with engine.engine.begin() as async_connect:
        await async_connect.run_sync(Base.metadata.create_all)
    await asyncio.gather(bot_task, autopost, send_adv)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
