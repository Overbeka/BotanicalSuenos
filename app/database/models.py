# import os
# from dotenv import load_dotenv
#
# from sqlalchemy import BigInteger, String, ForeignKey
# from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
#
# load_dotenv()
#
# engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'),
#                              echo=True)
#
# async_session = async_sessionmaker(engine)
#
#
# class Base(AsyncAttrs, DeclarativeBase):
#     pass
#
#
# class Category(Base):
#     __tablename__ = 'Категории'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(20))
#
#
# class SubCategory(Base):
#     __tablename__ = 'Подкатегории'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     category: Mapped[int] = mapped_column(ForeignKey('Категории.id'))
#     name: Mapped[str] = mapped_column(String(20))
#
#
# class Bouquets(Base):
#     __tablename__ = 'Букеты'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     sub_category: Mapped[int] = mapped_column(ForeignKey('Подкатегории.id'))
#     name: Mapped[str] = mapped_column(String(30))
#     photo_url: Mapped[str] = mapped_column(String(50))
#
#
# class Size(Base):
#     __tablename__ = 'Размеры'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(2))
#
#
# class Price(Base):
#     __tablename__ = 'Цены'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     bouquet: Mapped[int] = mapped_column(ForeignKey('Букеты.id'))
#     size: Mapped[int] = mapped_column(ForeignKey('Размеры.id'))
#     price: Mapped[str] = mapped_column((String(5)))
#
#
# async def add_data():
#     async with async_session() as session:
#         async with session.begin():
#             category1 = Category(name='Универсальные')
#             category2 = Category(name='Сезонные')
#             session.add(category1)
#             session.add(category2)
#             print(f"Категория '{category1.name}' добавлена")
#             print(f"Категория '{category2.name}' добавлена")
#             await session.commit()
#
#
# async def async_main():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
