import asyncio

from autoposting.core import get_name_by_id
from autoposting.crud import check_phone_number
from autoposting.db_models import db_
from autoposting.start import start_autoposting


def main():
    start_autoposting()



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
