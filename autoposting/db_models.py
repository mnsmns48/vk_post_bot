import datetime

from sqlalchemy import DateTime, func, BigInteger, Sequence
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from cfg import engine

POSTS_ID = Sequence('posts_id_seq', start=1)
VISITORS_ID = Sequence('visitors_id_seq', start=1)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Posts(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, server_default=POSTS_ID.next_value())
    post_id: Mapped[int | None] = mapped_column(BigInteger)
    time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=False), server_default=func.now())
    group_id: Mapped[int | None] = mapped_column(BigInteger)
    group_name: Mapped[str | None]
    signer_id: Mapped[int | None] = mapped_column(BigInteger)
    signer_name: Mapped[str]
    phone_number: Mapped[int | None] = mapped_column(BigInteger)
    text: Mapped[str | None]
    is_repost: Mapped[bool | None]
    repost_source_id: Mapped[int | None] = mapped_column(BigInteger)
    repost_source_name: Mapped[str | None]
    attachments: Mapped[str | None]
    source: Mapped[str]

    def create_table(self):
        self.metadata.create_all(bind=engine)

    def drop_table(self):
        self.metadata.drop_all(bind=engine)


class Visitors(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, server_default=VISITORS_ID.next_value())
    time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=False), server_default=func.now())
    tg_id: Mapped[int]
    tg_username: Mapped[str] = mapped_column(nullable=True)
    tg_fullname: Mapped[str] = mapped_column(nullable=True)

    def create_table(self):
        self.metadata.create_all(bind=engine)

    def drop_table(self):
        self.metadata.drop_all(bind=engine)


post_table = Posts()
visitors = Visitors()
