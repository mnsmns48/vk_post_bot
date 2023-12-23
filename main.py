import asyncio

from autoposting.db_models import visitors
from bot.main_bot import bot_working


async def main():
    visitors.create_table()
    await bot_working()
# await start_autoposting()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
