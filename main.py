import asyncio
from autoposting.db_models import Base
from autoposting.start import start_autoposting
from bot.main_bot import bot_working
from cfg import engine


async def main():
    bot_task = asyncio.create_task(bot_working())
    autopost = asyncio.create_task(start_autoposting())
    async with engine.begin() as async_connect:
        await async_connect.run_sync(Base.metadata.create_all)
    await asyncio.gather(bot_task, autopost)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
