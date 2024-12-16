from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID

import app.keyboards as kb
from app.database.requests import (get_users, set_item, set_collage, count_items,
                                   get_orders, valid_price, set_new_price)

admin = Router()


class News(StatesGroup):
    message = State()


class AddItem(StatesGroup):
    name = State()
    category = State()
    sub_category = State()
    description = State()
    sizes = State()
    prices = State()
    photo = State()
    position = State()


class AddCollage(StatesGroup):
    category = State()
    sub_category = State()
    photo = State()


class SetPrice(StatesGroup):
    item = State()
    price = State()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in ADMIN_ID


admin.message.filter(Admin())


@admin.message(Command('admin'))
async def admin_panel(message: Message):
    await message.answer('Возможные команды:\n/news\n/add_item\n'
                         '/add_collage\n/orders\n/new_price')


@admin.message(Command('news'))
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(News.message)
    await message.answer('Введите сообщение для пользователей')


@admin.message(News.message)
async def newsletter_message(message: Message, state: FSMContext):
    for user in await get_users():
        try:
            await message.send_copy(chat_id=user.tg_id)
        except:
            pass
    await message.answer('Рассылка успешно завершена.')
    await state.clear()


@admin.message(Command('add_item'))
async def add_item(message: Message, state: FSMContext):
    await state.set_state(AddItem.name)
    await message.answer('Введите название товара')


@admin.message(AddItem.name)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddItem.category)
    await message.answer('Выберите категорию товара', reply_markup=await kb.categories())


@admin.callback_query(AddItem.category)
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=callback.data.split('_')[1])
    await state.set_state(AddItem.sub_category)
    await callback.answer('')
    await callback.message.answer('Выберите подкатегорию товара',
                                  reply_markup=await kb.sub_categories(callback.data.split('_')[1]))


@admin.callback_query(AddItem.sub_category)
async def add_item_sub_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategory=callback.data.split('_')[1])
    await state.set_state(AddItem.description)
    await callback.answer('')
    await callback.message.answer('Введите описание товара')


@admin.message(AddItem.description)
async def add_item_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if description == "-":
        description = ""
    await state.update_data(description=description)
    await state.set_state(AddItem.sizes)
    await message.answer('Введите размеры товара в виде: S/M или введите "-" для пропуска.')


@admin.message(AddItem.sizes)
async def add_item_sizes(message: Message, state: FSMContext):
    sizes_input = message.text.strip()

    if sizes_input == "-":
        sizes_input = ""
    await state.update_data(sizes=sizes_input)
    await state.set_state(AddItem.prices)
    await message.answer('Отправьте цены товара в виде: 4/5')


@admin.message(AddItem.prices)
async def add_item_sizes(message: Message, state: FSMContext):
    await state.update_data(prices=message.text)
    await state.set_state(AddItem.photo)
    await message.answer('Отправьте фото товара')


@admin.message(AddItem.photo, F.photo)
async def add_item_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    await set_item(data)
    total = await count_items()
    await message.answer(f'Товар успешно добавлен. Всего товаров: {total}')
    await state.clear()


@admin.message(Command('add_collage'))
async def add_collage(message: Message, state: FSMContext):
    await state.set_state(AddCollage.category)
    await message.answer('Выберите категорию товара', reply_markup=await kb.categories())


@admin.callback_query(AddCollage.category)
async def add_collage_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=callback.data.split('_')[1])
    await state.set_state(AddCollage.sub_category)
    await callback.answer('')
    await callback.message.edit_text('Выберите подкатегорию товара',
                                     reply_markup=await kb.sub_categories(callback.data.split('_')[1]))


@admin.callback_query(AddCollage.sub_category)
async def add_collage_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(subcategory=callback.data.split('_')[1])
    await state.set_state(AddCollage.photo)
    await callback.answer('')
    await callback.message.answer('Отправьте коллаж')


@admin.message(AddCollage.photo, F.photo)
async def add_collage_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    await set_collage(data)
    await message.answer('Коллаж успешно добавлен')
    await state.clear()


@admin.message(Command('orders'))
async def send_orders(message: Message):
    orders = await get_orders()
    if not orders:
        await message.answer("Нет заказов.")
        return
    orders_message = "Список заказов:\n\n"
    for order in orders:
        orders_message += (f"Номер заказа: {order.id}\n"
                           f"Имя пользователя: @{order.user_name}\n"
                           f"Имя: {order.first_name}\n"
                           f"Контакт: +{order.contact}\n"
                           f"Товары:\n{order.items}\n\n"
                           f"Дата заказа: {order.date}\n\n\n")

    await message.answer(orders_message)


@admin.message(Command('new_price'))
async def new_price(message: Message, state: FSMContext):
    await state.set_state(SetPrice.item)
    await message.answer('Введите название товара, у которого хотите поменять цену:')


@admin.message(SetPrice.item)
async def price(message: Message, state: FSMContext):
    await state.update_data(item=message.text)
    await state.set_state(SetPrice.price)
    await message.answer('Введите новую цену в формате 4/5:')


@admin.message(SetPrice.price)
async def set_price(message: Message, state: FSMContext):
    data = await state.get_data()
    item_name = data.get('item')
    item_price = message.text

    if not await valid_price(item_price):
        await message.answer('Введите цену в корректном формате 4, 5/6 или 7/8/9:')
        return

    result = await set_new_price(item_name, item_price)

    if result:
        await message.answer(f'Цена для товара "{item_name}" была успешно обновлена на {item_price}.')
        await state.clear()
    else:
        await message.answer('Не удалось обновить цену, проверьте, существует ли товар.')
        await state.set_state(SetPrice.item)
        await message.answer('Введите название товара, у которого хотите поменять цену:')
