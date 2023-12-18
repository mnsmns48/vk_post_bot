from sqlalchemy import select, insert, Sequence, Table, Column, Integer, schema
from sqlalchemy.orm import Session



from autoposting.db_models import Posts
from cfg import engine


def check_phone_number(number: int) -> int | None:
    with Session(engine) as session:
        query = select(Posts.signer_id).filter(Posts.phone_number == number)
        response = session.execute(query).scalar_one_or_none()
    return response


def write_post_data(data):
    with Session(engine) as session:
        seq = Sequence(Posts.id)
        session.execute(seq)
        stmt = insert(Posts).values(id=seq.next_value(),
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
                                    attachments=data.attachments,
                                    source=data.source,
                                    )
        session.execute(stmt)
        session.commit()
