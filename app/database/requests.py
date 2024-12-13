from app.database.models import User, Category, SubCategory, Item, Basket, Collage
from app.database.models import async_session

from sqlalchemy import select, update, delete, func


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def set_item(data):
    async with async_session() as session:
        session.add(Item(**data))
        await session.commit()


async def set_collage(data):
    async with async_session() as session:
        session.add(Collage(**data))
        await session.commit()


async def get_last_item(position):
    async with async_session() as session:
        result = await session.execute(
            select(Item).where(Item.position == position).order_by(Item.id.desc()))
    return result.scalars().first()


async def count_items():
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(Item))
        return result.scalars().first()


async def set_basket(tg_id, item_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Basket(user=user.id, item=item_id))
        await session.commit()


async def get_basket(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return []
        basket_items = await session.scalars(select(Basket.item).where(Basket.user == user.id))
        basket_info = []
        total_price = 0
        for item in basket_items:
            if item:
                basket_info.append(str(item))
                parts = item.split(', ')
                for part in parts:
                    if 'Цена:' in part:
                        price_str = part.split(': ')[1]
                        try:
                            total_price += int(price_str)
                        except ValueError:
                            pass
        return basket_info, total_price


async def delete_basket(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            await session.execute(delete(Basket).where(Basket.user == user.id))
            await session.commit()


async def get_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_sub_categories(cat_id):
    async with async_session() as session:
        return await session.scalars(select(SubCategory).where(SubCategory.category == cat_id))


async def get_collage_by_sub(collage_id):
    async with async_session() as session:
        collage = await session.scalar(select(Collage).where(Collage.subcategory == collage_id))
        return collage


async def get_items_by_subcategory(subcategory_id):
    async with async_session() as session:
        items = await session.scalars(select(Item).where(Item.subcategory == subcategory_id))
        return items.all()


async def get_items_position(item_pos: int):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.position == item_pos))


async def get_items_by_category(category_id: int):
    async with async_session() as session:
        items = await session.scalars(select(Item).where(Item.category == category_id))
        return items


async def get_items_by_collage_id(collage_id):
    async with async_session() as session:
        items = await session.scalars(select(Item).where(Item.collage == collage_id))


async def get_item_by_id(item_id: int):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
    return item


async def get_item_name_by_id(item_id: int):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        return item.name if item else "Неизвестный товар"


async def get_item_by_size_and_price(size: str, price: int):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.sizes.like(f'%{size}%') and Item.prices.like(f'%{price}%')))
        if item:
            sizes = item.sizes.split('/')
            prices = item.prices.split('/')
            sizes_prices = [{'size': size, 'price': int(price)} for size, price in zip(sizes, prices) if size == size and int(price) == price]
            return {
                'item': item,
                'sizes_prices': sizes_prices
            }
        else:
            return None
