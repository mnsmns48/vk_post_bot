import asyncio

from autoposting.core import get_name_by_id
from autoposting.db_models import db_
from autoposting.start import start_autoposting


# async def main():
#     await start_autoposting()


if __name__ == "__main__":
    try:
        db_.drop_table()
        db_.create_table()
        # asyncio.run(main())
    except KeyboardInterrupt:
        pass
        # main().close()
