from aiogram.types import Message
from sqlalchemy import insert, Sequence, select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from autoposting.db_models import Visitors


async def write_user(m: Message, session: AsyncSession):
    stmt = insert(Visitors).values(
        id=await session.execute(Sequence('visitors_id_seq')),
        tg_id=m.from_user.id,
        tg_username=m.from_user.username,
        tg_fullname=m.from_user.full_name
    )
    await session.execute(stmt)
    await session.commit()


async def last_guests(session: AsyncSession) -> str:
    query = select(Visitors).order_by(Visitors.time.desc()).limit(10)
    r: Result = await session.execute(query)
    guests = r.scalars().all()
    result = str()
    for line in guests:
        result += f"{line.time.strftime('%d-%m-%Y %H:%M')} {line.tg_id} {line.tg_username} {line.tg_fullname}\n"
    return result
