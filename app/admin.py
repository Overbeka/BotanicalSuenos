from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from app.database.requests import get_users, set_item, set_collage, count_items, get_last_item

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


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [258999004, 1082661645]


admin.message.filter(Admin())


@admin.message(Command('admin'))
async def admin_panel(message: Message):
    await message.answer('Возможные команды:\n/news\n/add_item\n/add_collage')


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
    await state.update_data(description=message.text)
    await state.set_state(AddItem.sizes)
    await message.answer('Введите размеры товара в виде: S/M')


@admin.message(AddItem.sizes)
async def add_item_sizes(message: Message, state: FSMContext):
    await state.update_data(sizes=message.text)
    await state.set_state(AddItem.prices)
    await message.answer('Отправьте цены товара в виде: 4000/5000')


@admin.message(AddItem.prices)
async def add_item_sizes(message: Message, state: FSMContext):
    await state.update_data(prices=message.text)
    await state.set_state(AddItem.photo)
    await message.answer('Отправьте фото товара')


@admin.message(AddItem.photo, F.photo)
async def add_item_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(AddItem.position)
    await message.answer('Введите порядковый номер товара')


@admin.message(AddItem.position)
async def add_item_position(message: Message, state: FSMContext):
    position = message.text

    if await get_last_item(position):
        total = await count_items()
        await message.answer(f'Товар с таким номером уже существует. Всего было добавлено ранее: {total}')
        return

    data = await state.get_data()
    data['position'] = position

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
