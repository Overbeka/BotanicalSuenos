from sqlalchemy import select, update, delete, func, desc


from app.database.models import async_session
from app.database.models import User, Category, SubCategory, Item, Basket, Collage, Order


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


async def count_items():
    async with async_session() as session:
        result = await session.execute(select(func.count()).select_from(Item))
        return result.scalars().first()


async def set_basket(tg_id, item_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        session.add(Basket(user=user.id, item=item_id))
        await session.commit()


async def set_new_price(item_name, item_price):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.name == item_name))
        item = result.scalar_one_or_none()

        if item:
            item.prices = item_price
            session.add(item)
            await session.commit()
            return True
        return False


async def valid_price(prices: str):
    parts = prices.split('/')
    return all(part.isdigit() for part in parts)


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


async def get_item_by_id(item_id: int):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.id == item_id))
    return item


async def get_all_items():
    async with async_session() as session:
        result = await session.execute(select(Item))
        items = result.scalars().all()
    return items


async def get_item_name_by_id(item_id: int):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        return item.name if item else "Неизвестный товар"


async def set_users_order(tg_id, user_name, first_name, contact, items, date):
    async with async_session() as session:
        new_order = Order(
            tg_id=tg_id,
            user_name=user_name,
            first_name=first_name,
            contact=contact,
            items="\n".join(items),
            date=date
        )
        session.add(new_order)
        await session.commit()


async def get_orders():
    async with async_session() as session:
        query = select(Order).order_by(desc(Order.id)).limit(5)
        orders = await session.execute(query)
        orders_list = orders.scalars().all()
        orders_list.sort(key=lambda order: order.id)
        return orders_list


async def get_user_orders(tg_id):
    async with async_session() as session:
        user_order = await session.execute(select(Order).where(Order.tg_id == tg_id))
        user_order_list = user_order.scalars().all()
        return user_order_list


async def get_item_price(item_name):
    async with async_session() as session:
        result = select(Item).where(Item.name == item_name)
        result_1 = await session.execute(result)

        item = result_1.scalar_one_or_none()
        if item:
            return item.prices
        return None


async def valid_number(message):

    if message.contact and message.contact.phone_number:
        phone_number = message.contact.phone_number
    elif message.text:
        phone_number = message.text.strip()
    else:
        await message.answer("Пожалуйста, предоставьте номер телефона.")
        return None

    if len(phone_number) != 11 or not phone_number.isdigit() or not phone_number.startswith('7'):
        await message.answer("Номер телефона должен начинаться с 7 и содержать 11 цифр. Попробуйте еще раз.")
        return None

    return phone_number
