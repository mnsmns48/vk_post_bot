from typing import Optional
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Dobrotsen(Base):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    parent: Mapped[int]
    title: Mapped[str] = mapped_column(primary_key=True, unique=True)
    link: Mapped[str] = mapped_column(primary_key=True, unique=True)
    price: Mapped[Optional[float]]
    image: Mapped[Optional[str]]
