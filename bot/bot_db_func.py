import asyncio

from aiogram.types import Message
from sqlalchemy import insert, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from autoposting.db_models import Visitors
from cfg import engine


async def write_user(m: Message, session: AsyncSession):
    stmt = insert(Visitors).values(
        id=await session.execute(Sequence('visitors_id_seq')),
        tg_id=m.from_user.id,
        tg_username=m.from_user.username,
        tg_fullname=m.from_user.full_name
    )
    await session.execute(stmt)
    await session.commit()
