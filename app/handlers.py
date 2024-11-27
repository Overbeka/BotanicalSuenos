from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import app.keyboards as kb
from app.database.requests import (get_item_by_id, set_user,
                                   set_basket, get_basket, get_item_by_id, delete_basket)


router = Router()
ADMIN_ID = '258999004'


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await set_user(message.from_user.id)
        await message.answer('Добро пожаловать в Botanical Sueños!',
                             reply_markup=kb.main)
    else:
        await message.answer('Вы вернулись на главную')
        await message.message.answer("Добро пожаловать в Botanical Sueños!",
                                     reply_markup=kb.main)


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


@router.callback_query(F.data.startswith('sub_category_'))
async def category(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите сезон:',
                                     reply_markup=await kb.sub_sub_categories())


@router.callback_query(F.data.startswith('item_'))
async def category(callback: CallbackQuery):
    item = await get_item_by_id(int(callback.data.split('_')[1]))
    await callback.answer('')
    await callback.message.answer_photo(photo=item.photo, caption=f'{item.name}\n\nЦена: {item.price} рублей',
                                        reply_markup=await kb.basket(item.id))


@router.callback_query(F.data.startswith('order_'))
async def basket(callback: CallbackQuery):
    await set_basket(callback.from_user.id, callback.data.split('_')[1])
    await callback.answer('')
    await callback.message.answer('Товар добавлен в корзину')


@router.callback_query(F.data == 'basket')
async def basket(callback: CallbackQuery):
    await callback.answer('')
    basket = await get_basket(callback.from_user.id)
    counter = 0
    for item_info in basket:
        item = await get_item_by_id(item_info.item)
        await callback.message.answer_photo(photo=item.photo, caption=f'{item.name}\n\nЦена: {item.price} рублей',
                                            reply_markup=await kb.delete_from_basket(item.id))
        counter += 1
    await callback.message.answer('Ваша корзина пуста') if counter == 0 else await callback.answer('')


@router.callback_query(F.data.startswith('delete_'))
async def delete_from_basket(callback: CallbackQuery):
    await delete_basket(callback.from_user.id, callback.data.split('_')[1])
    await callback.message.delete()
    await callback.answer('Вы удалили товар из корзины')


@router.callback_query(F.data.startswith('buy_'))
async def delete_from_basket(callback: CallbackQuery):
    baskets = await get_basket(callback.from_user.id)
    user_name = callback.from_user.username
    basket_items = []
    for basket in baskets:
        item = await get_item_by_id(basket.item)
        if item:
            basket_items.append(f"{item.name} - {item.price} руб.")

    basket_message = f"Новый заказ от @{user_name}:\n" + "\n".join(basket_items)
    await callback.bot.send_message(ADMIN_ID, basket_message)

    await delete_basket(callback.from_user.id, callback.data.split('_')[1])
    await callback.message.delete()
    await callback.message.answer('Спасибо за заказ. Мы свяжемся с Вами в ближайшее время',
                                  reply_markup=kb.main)


@router.message(Command('contacts'))
@router.callback_query(F.data == 'contacts')
async def contacts(message: Message | CallbackQuery):
    response_text = 'Наш номер телефона: 8911*******, наш instagram:'

    if isinstance(message, Message):
        await message.answer(response_text)
    else:
        await message.answer('')
        await message.message.answer(response_text)
