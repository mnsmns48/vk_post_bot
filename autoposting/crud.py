import asyncio
from functools import wraps
from typing import Callable

from sqlalchemy import select, insert, Sequence, text
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from autoposting.db_models import Posts
from cfg import engine, hv


async def check_phone_number(number: int, session: AsyncSession) -> str | None:
    query = select(Posts.signer_id).filter(Posts.phone_number == number)
    interim = await session.execute(query)
    response = interim.scalars().all()
    try:
        counter = Counter(response)
        item, count = max(counter.items(), key=lambda p: p[::-1])
        return item
    except ValueError:
        if len(response) == 0:
            return None


async def write_post_data(data, session: AsyncSession):
    stmt = insert(Posts).values(
        id=await session.execute(Sequence('posts_id_seq')),
        post_id=data.post_id,
        time=data.time,
        group_id=data.group_id,
        group_name=data.group_name,
        phone_number=data.signer_phone_number,
        signer_id=data.signer_id,
        signer_name=data.signer_name,
        text=data.text,
        is_repost=data.repost,
        repost_source_id=data.repost_place_id,
        repost_source_name=data.repost_place_name,
        attachments=data.attachments.get('to_db_str') if data.attachments else None,
        source=data.source,
    )
    await session.execute(stmt)
    await session.commit()


def post_filter(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        for filter_one_word in hv.filter_words:
            if filter_one_word in kwargs.get('text'):
                response = False
        return response

    return wrapper


@post_filter
async def read_post_data(post_id: int, group_id: int, text: str) -> bool:
    async with AsyncSession(engine) as session:
        query = select(Posts.post_id, Posts.group_id) \
            .filter(Posts.post_id == post_id, Posts.group_id == group_id)
        response = await session.execute(query)
    if response.fetchone() == (post_id, group_id):
        return False
    async with AsyncSession(engine) as session:
        query = select(Posts.text).filter(Posts.text == text)
        response_text = await session.execute(query)
    if response_text.fetchone():
        return False
    await asyncio.sleep(0.1)
    return True

# def data_transfer():
#     with Session(engine) as session:
#         select_stmt = select(People.user_id, People.full_name, People.phone_number)
#         insert_stmt = insert(Posts).from_select(
#             ['signer_id', 'signer_name', 'phone_number'], select_stmt)
#         session.execute(insert_stmt)
#         session.commit()
