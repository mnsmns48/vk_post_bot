import datetime

from sqlalchemy import DateTime, func, BigInteger
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from cfg import engine


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Posts(Base):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    post_id: Mapped[int | None] = mapped_column(BigInteger)
    time: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
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

    def create_table(self):
        self.metadata.create_all(bind=engine)

    def drop_table(self):
        self.metadata.drop_all(bind=engine)


db_ = Posts()
