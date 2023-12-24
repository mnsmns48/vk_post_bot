from aiogram.types import Message
from sqlalchemy import insert, Sequence
from sqlalchemy.orm import Session

from autoposting.db_models import Visitors
from cfg import engine


def write_user(m: Message):
    with Session(engine) as session:
        stmt = insert(Visitors).values(
            id=session.execute(Sequence('visitors_id_seq')),
            tg_id=m.from_user.id,
            tg_username=m.from_user.username,
            tg_fullname=m.from_user.full_name
        )
        session.execute(stmt)
        session.commit()
