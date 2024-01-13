from functools import wraps
from typing import Callable

from sqlalchemy import select, insert, Sequence, text
from sqlalchemy.orm import Session
from collections import Counter

from autoposting.db_models import Posts, People
from cfg import engine, hv


def check_phone_number(number: int) -> int | None:
    with Session(engine) as session:
        query = select(Posts.signer_id).filter(Posts.phone_number == number)
        response = session.execute(query).scalars().all()
    try:
        counter = Counter(response)
        item, count = max(counter.items(), key=lambda p: p[::-1])
        return item
    except ValueError:
        if len(response) == 0:
            return None


def write_post_data(data):
    with Session(engine) as session:
        stmt = insert(Posts).values(
            id=session.execute(Sequence('posts_id_seq')),
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
        session.execute(stmt)
        session.commit()


def post_filter(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        for filter_one_word in hv.filter_words:
            if filter_one_word in kwargs.get('text'):
                response = False
        return response

    return wrapper


@post_filter
def read_post_data(post_id: int, group_id: int, text: str) -> bool:
    with Session(engine) as session:
        query = select(Posts.post_id, Posts.group_id) \
            .filter(Posts.post_id == post_id, Posts.group_id == group_id)
        response = session.execute(query).fetchone()
    if response == (post_id, group_id):
        return False
    with Session(engine) as session:
        query = select(Posts.text).filter(Posts.text == text)
        response_text = session.execute(query).fetchone()
    if response_text:
        return False
    return True


def data_transfer():
    with Session(engine) as session:
        select_stmt = select(People.user_id, People.full_name, People.phone_number)
        insert_stmt = insert(Posts).from_select(
            ['signer_id', 'signer_name', 'phone_number'], select_stmt)
        session.execute(insert_stmt)
        session.commit()
