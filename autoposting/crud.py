from sqlalchemy import select
from sqlalchemy.orm import Session

from autoposting.db_models import Posts
from cfg import engine


def check_phone_number(number: int) -> int | None:
    with Session(engine) as session:
        query = select(Posts.signer_id).filter(Posts.phone_number == number)
        response = session.execute(query).scalar_one_or_none()
    return response
