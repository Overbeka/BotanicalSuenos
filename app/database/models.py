import os
from dotenv import load_dotenv

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from typing import List

load_dotenv()

engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'),
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

    basket_rel: Mapped[List['Basket']] = relationship(back_populates='user_rel')


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))

    item_rel: Mapped[List['Item']] = relationship(back_populates='category_rel')


class SubCategory(Base):
    __tablename__ = 'subcategories'

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    name: Mapped[str] = mapped_column(String(20))


class SubSubCategory(Base):
    __tablename__ = 'subsubcategories'

    id: Mapped[int] = mapped_column(primary_key=True)
    subcategory: Mapped[int] = mapped_column(ForeignKey('subcategories.id'))
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

    category_rel: Mapped['Category'] = relationship(back_populates='item_rel')
    basket_rel: Mapped[List['Basket']] = relationship(back_populates='item_rel')


class Basket(Base):
    __tablename__ = 'basket'

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))

    user_rel: Mapped['User'] = relationship(back_populates='basket_rel')
    item_rel: Mapped['Item'] = relationship(back_populates='basket_rel')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
