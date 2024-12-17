import asyncio
from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command


from config import ADMIN_ID, phone_number, vk, inst, individual, greeting
from app.states import Add
import app.keyboards as kb
from app.database.requests import (set_user, set_basket, set_users_order,
                                   get_basket, get_item_by_id, get_user_orders, get_item_name_by_id, get_collage_by_sub,
                                   valid_number, delete_basket)


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer(greeting, reply_markup=kb.main)


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(greeting, reply_markup=kb.main)


@router.callback_query(F.data == 'to_cat')
@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите основную категорию товара:',
                                     reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Какой из доступных разделов вас интересует?',
                                     reply_markup=await kb.sub_categories(callback.data.split('_')[1]))


@router.callback_query(F.data == 'sub_Индивидуальные')
async def author(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(individual)
    await state.set_state(Add.add_questions)
    await callback.answer('')


@router.message(Add.add_questions)
async def add_questions(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await state.set_state(Add.answer_contact)
    await message.answer('Пожалуйста, введите ваш номер телефона в формате "71234567890" '
                         'или нажмите на кнопку "Отправить контакт".', reply_markup=kb.contact)


@router.message(Add.answer_contact)
async def answer_contact(message: Message, state: FSMContext):
    phone = await valid_number(message)
    if phone is None:
        return
    await state.update_data(contact=phone)

    data = await state.get_data()
    user_name = message.from_user.username
    first_name = message.from_user.first_name

    answer_message = (f"Новый ответ от {first_name} (@{user_name})\n"
                      f"Телефон: +{data['contact']}\n"
                      f"Ответ:\n\n{data['answer']}")

    for admin_id in ADMIN_ID:
        await message.bot.send_message(admin_id, answer_message)

    message = await message.answer("Спасибо за ваши ответы! Мы свяжемся с вами в ближайшее время.",
                                   reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await asyncio.sleep(5)
    await message.delete()


@router.callback_query(F.data.startswith('sub_'))
async def item_names(callback: CallbackQuery):
    subcategory_id = callback.data.split('_')[1]
    collage = await get_collage_by_sub(subcategory_id)

    await callback.answer('')
    await callback.message.answer_photo(
        photo=collage.photo,
        caption='Какой товар вы хотите рассмотреть?',
        reply_markup=await kb.items_name(subcategory_id))


@router.callback_query(F.data.startswith('item_'))
async def item_handler(callback: CallbackQuery):
    item_id = int(callback.data.split('_')[1])
    item = await get_item_by_id(item_id)

    await callback.answer('')
    await callback.message.answer_photo(photo=item.photo,
                                        caption=f'{item.name}\n\n'
                                                f'{item.description}'
                                                f'Размеры: {item.sizes}\n\n'
                                                f'Цены: {item.prices}р\n\n'
                                                'Выберите нужный размер:',
                                        reply_markup=await kb.sizes_keyboard(item_id))


@router.callback_query(F.data.startswith('size_'))
async def to_basket(callback: CallbackQuery):
    _, item_id, size, price = callback.data.split('_')
    item_name = await get_item_name_by_id(item_id)
    basket_entry = f"{item_name}, Размер: {size}, Цена: {price}"
    await set_basket(callback.from_user.id, basket_entry)

    await callback.answer('')
    await callback.message.answer('Товар добавлен в корзину. '
                                  'Вы можете оформить заказ или продолжить покупки.',
                                  reply_markup=kb.add_keyboard)


# @router.callback_query(F.data.startswith('size_'))
# async def to_basket(callback: CallbackQuery):
#     _, item_id, size, price = callback.data.split('_')
#     item_name = await get_item_name_by_id(item_id)
#     basket_entry = f"{item_name}, Размер: {size}, Цена: {price}"
#     await set_basket(callback.from_user.id, basket_entry)
#
#     await callback.answer('')
#     await callback.message.answer('Товар добавлен в корзину. '
#                                   'Вы можете оформить заказ или продолжить покупки',
#                                   reply_markup=kb.add_keyboard)


@router.callback_query(F.data == 'to_sub')
@router.callback_query(F.data == 'to_col')
@router.callback_query(F.data == 'cont')
async def to_main(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.delete()


@router.callback_query(F.data == 'basket')
async def basket(callback: CallbackQuery):
    await callback.answer('')
    basket_items, total_price = await get_basket(callback.from_user.id)
    if not basket_items:
        await callback.message.answer('В вашей корзине нет товаров.')
        return
    basket_output = '\n'.join(basket_items)
    basket_output += f'\n\nОбщая сумма: {total_price}р'
    await callback.message.edit_text(basket_output,
                                     reply_markup=kb.basket_keyboard)


@router.callback_query(F.data.startswith('clear_basket'))
async def delete_from_basket(callback: CallbackQuery):
    await delete_basket(callback.from_user.id)
    await callback.message.delete()
    message = await callback.message.answer('Корзина очищена.')
    await asyncio.sleep(3)
    await message.delete()
    await callback.message.answer(greeting, reply_markup=kb.main)


@router.callback_query(F.data.startswith('make_order'))
async def make_order(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer('Пожалуйста, введите ваш номер телефона в формате "71234567890" '
                                  'или нажмите на кнопку "Отправить контакт".',
                                  reply_markup=kb.contact)
    await state.set_state(Add.order_contact)
    await callback.answer()


@router.message(Add.order_contact)
async def receive_phone(message: Message, state: FSMContext):
    phone = await valid_number(message)
    if phone is None:
        return
    await state.update_data(contact=phone)

    data = await state.get_data()
    date = datetime.now().strftime("%d/%m/%Y")
    baskets = await get_basket(message.from_user.id)
    basket_items = baskets[0]
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    tg_id = message.from_user.id

    basket_message = (f"Новый заказ от {first_name} (@{user_name})\n"
                      f"Телефон: +{data['contact']}\n") + "\n".join(basket_items)

    for admin_id in ADMIN_ID:
        await message.bot.send_message(admin_id, basket_message)

    await set_users_order(tg_id, user_name, first_name, data['contact'], basket_items, date)

    await delete_basket(message.from_user.id)

    message = await message.answer("Благодарим вас за заказ!"
                                   "Мы свяжемся с вами в ближайшее время для уточнения деталей.",
                                   reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(5)
    await message.delete()
    await message.answer(greeting, reply_markup=kb.main)
    await state.clear()


@router.message(Command('contacts'))
@router.callback_query(F.data == 'contacts')
async def contacts(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await message.answer(f'Номер телефона: {phone_number}\n'
                             f'ВК: {vk}\n'
                             f'Instagram: {inst}')
    else:
        await message.answer('')
        await message.message.answer(f'Номер телефона: {phone_number}\n'
                                     f'ВК: {vk}\n'
                                     f'Instagram: {inst}')


@router.message(Command('my_orders'))
async def my_orders(message: Message):
    user_order_list = await get_user_orders(message.from_user.id)
    if not user_order_list:
        await message.answer('У вас пока нет заказов.')
        return
    orders_text = 'Список ваших заказов:\n\n'
    for order in user_order_list:
        orders_text += (f"Заказ №{order.id}\n\n"
                        f"Товары:\n{order.items}\n\n"
                        f"Дата заказа: {order.date}\n\n\n")

    await message.answer(orders_text)
