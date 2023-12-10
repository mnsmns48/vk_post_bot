import asyncio

from autoposting.core import get_name_by_id
from autoposting.start import start_autoposting


async def main():

    await start_autoposting()


if __name__ == "__main__":
    asyncio.run(main())
