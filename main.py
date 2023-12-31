import asyncio

from autoposting.crud import data_transfer
from autoposting.db_models import Base
from autoposting.start import start_autoposting
from bot.main_bot import bot_working
from cfg import engine


async def main():
    # data_transfer()
    # Base.metadata.drop_all(engine)
    bot_task = asyncio.create_task(bot_working())
    autoposting = asyncio.create_task(start_autoposting())
    await asyncio.gather(bot_task, autoposting)

if __name__ == "__main__":
    try:
        # Base.metadata.create_all(engine)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
