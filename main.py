import asyncio

from autoposting.db_models import Base
from autoposting.start import start_autoposting
from bot.main_bot import bot_working
from cfg import engine


async def main():
    pass
    # Base.metadata.drop_all(engine)
    await bot_working()
    # await start_autoposting()


if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
