from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from app.database.requests import get_users, set_item

admin = Router()


class Newsletter(StatesGroup):
    message = State()


class AddItem(StatesGroup):
    name = State()
    category = State()
    sub_category = State()
    size = State()
    photo = State()
    price = State()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [258999004]


admin.message.filter(Admin())


@admin.message(Command('admin'))
async def admin_panel(message: Message):
    await message.answer('Возможные команды:\n/newsletter\n/add_item')


@admin.message(Command('newsletter'))
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.message)
    await message.answer('Введите сообщение для пользователей')


@admin.message(Newsletter.message)
async def newsletter_message(message: Message, state: FSMContext):
    await message.answer('Подождите... идёт рассылка.')
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
    await callback.message.answer('Выберите подкатегорию товара', reply_markup=await kb.sub_categories())


@admin.callback_query(AddItem.sub_category)
async def add_item_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(sub_category=callback.data.split('_')[1])
    await state.set_state(AddItem.size)
    await callback.answer('')
    await callback.message.answer('Введите размеры товара')


@admin.message(AddItem.size)
async def add_item_description(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await state.set_state(AddItem.photo)
    await message.answer('Отправьте фото товара')


@admin.message(AddItem.photo, F.photo)
async def add_item_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(AddItem.price)
    await message.answer('Введите цену товара')


@admin.message(AddItem.price)
async def add_item_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    data = await state.get_data()
    await set_item(data)
    await message.answer('Товар успешно добавлен')
    await state.clear()
