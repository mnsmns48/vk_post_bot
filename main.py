import asyncio
from autoposting.start import start_autoposting
from bot.main_bot import bot_working


async def main():
    bot_task = asyncio.create_task(bot_working())
    autopost = asyncio.create_task(start_autoposting())
    await asyncio.gather(bot_task, autopost)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Script stopped')
