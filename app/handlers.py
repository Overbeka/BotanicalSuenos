from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

import app.keyboards as kb
from app.database.requests import (set_user, set_basket, get_basket, get_item_by_id,
                                   delete_basket, get_item_name_by_id, get_collage_by_sub)

from config import ADMIN_ID

router = Router()


class AddNumber(StatesGroup):
    contact = State()


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await set_user(message.from_user.id)
        await message.answer('Добро пожаловать в Botanical Sueños!',
                             reply_markup=kb.main)
    else:
        await message.answer('')
        await message.message.answer("Добро пожаловать в Botanical Sueños!",
                                     reply_markup=kb.main)


@router.callback_query(F.data == 'to_cat')
@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите интересующий вас товар:',
                                     reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите категорию:',
                                     reply_markup=await kb.sub_categories(
                                         callback.data.split('_')[1]
                                     ))


@router.callback_query(F.data.startswith('sub_'))
async def number(callback: CallbackQuery):
    subcategory_id = callback.data.split('_')[1]
    collage = await get_collage_by_sub(subcategory_id)
    await callback.answer('')
    await callback.message.answer_photo(
        photo=collage.photo,
        caption='Выберите товар:',
        reply_markup=await kb.get_items_number(subcategory_id))


@router.callback_query(F.data.startswith('item_'))
async def item_handler(callback: CallbackQuery):
    item_id = int(callback.data.split('_')[1])
    item = await get_item_by_id(item_id)
    await callback.answer('')
    await callback.message.answer_photo(photo=item.photo,
                                        caption=f'{item.name}\n\nОписание: {item.description}\n\nРазмеры: {item.sizes}\n\n'
                                                f'Цены: {item.prices}\n\n'
                                                'Выберите размер:', reply_markup=await kb.get_sizes_keyboard(item_id))


@router.callback_query(F.data.startswith('size_'))
async def to_basket(callback: CallbackQuery):
    _, item_id, size, price = callback.data.split('_')
    item_name = await get_item_name_by_id(item_id)
    basket_entry = f"{item_name}, Размер: {size}, Цена: {price}"
    await set_basket(callback.from_user.id, basket_entry)
    await callback.answer('')
    await callback.message.answer('Товар добавлен в корзину')


@router.callback_query(F.data == 'basket')
async def basket(callback: CallbackQuery):
    await callback.answer('')
    basket_items, total_price = await get_basket(callback.from_user.id)
    if not basket_items:
        await callback.message.answer('Ваша корзина пуста')
        return
    basket_output = '\n'.join(basket_items)
    basket_output += f'\n\nОбщая сумма: {total_price}'
    await callback.message.answer(basket_output, reply_markup=await kb.get_basket_keyboard())


@router.callback_query(F.data.startswith('clear_basket'))
async def delete_from_basket(callback: CallbackQuery):
    await delete_basket(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer('Вы удалили товары из корзины')


@router.callback_query(F.data.startswith('make_order'))
async def make_order(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer("Пожалуйста, отправьте контакт для связи:", reply_markup=kb.contact)
    await state.set_state(AddNumber.contact)
    await callback.answer()


@router.message(AddNumber.contact)
async def receive_phone(message: Message, state: FSMContext):
    await state.update_data(contact=message.contact.phone_number)
    baskets = await get_basket(message.from_user.id)
    basket_items = baskets[0]
    user_name = message.from_user.username or "Нет username"
    full_name = message.from_user.full_name

    basket_message = f"Новый заказ от {full_name} ({user_name}):\nТелефон: {message.contact.phone_number}\n" + "\n".join(basket_items)

    for admin_id in ADMIN_ID:
        await message.bot.send_message(admin_id, basket_message)

    await delete_basket(message.from_user.id)

    await message.answer("Спасибо за заказ. Мы свяжемся с Вами в ближайшее время", reply_markup=ReplyKeyboardRemove())
    await message.answer("Добро пожаловать в Botanical Sueños!", reply_markup=kb.main)
    await state.clear()


@router.message(Command('contacts'))
@router.callback_query(F.data == 'contacts')
async def contacts(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await message.answer('''Наш номер телефона: 8911*******, наш instagram:''')
    else:
        await message.answer('')
        await message.message.answer('''Наш номер телефона: 8911*******, наш instagram:''')
