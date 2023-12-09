import asyncio

from autoposting.start import start_autoposting


async def main():
    await start_autoposting()


if __name__ == "__main__":
    asyncio.run(main())
