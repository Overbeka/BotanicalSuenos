import os
from config import DB_URL

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

engine = create_async_engine(url=DB_URL,
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))


class SubCategory(Base):
    __tablename__ = 'subcategories'

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    name: Mapped[str] = mapped_column(String(20))


class Size(Base):
    __tablename__ = 'sizes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(2))


class Item(Base):
    __tablename__ = 'items'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(35))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    subcategory: Mapped[int] = mapped_column(ForeignKey('subcategories.id'))
    size: Mapped[int] = mapped_column(ForeignKey('sizes.id'))
    price: Mapped[str] = mapped_column(String(15))
    photo: Mapped[str] = mapped_column(String(128))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
