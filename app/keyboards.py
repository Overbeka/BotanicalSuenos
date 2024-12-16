from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import (get_categories, get_sub_categories,
                                   get_item_by_id, get_items_by_subcategory)

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Каталог', callback_data='catalog')],
    [InlineKeyboardButton(text='Корзина', callback_data='basket'),
     InlineKeyboardButton(text='Контакты', callback_data='contacts')]
])


contact = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить контакт', request_contact=True)]],
    resize_keyboard=True, input_field_placeholder='Отправьте контакт')


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name,
                                          callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def sub_categories(cat_id):
    subcategories = await get_sub_categories(cat_id)
    keyboard = InlineKeyboardBuilder()
    for sub_category in subcategories:
        keyboard.add(InlineKeyboardButton(text=sub_category.name,
                                          callback_data=f'sub_{sub_category.name}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_cat'))
    return keyboard.adjust(2).as_markup()


async def items_name(subcategory_id):
    item_names = await get_items_by_subcategory(subcategory_id)
    keyboard = InlineKeyboardBuilder()
    for item in item_names:
        keyboard.add(InlineKeyboardButton(text=item.name,
                                          callback_data=f'item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_sub'))
    return keyboard.adjust(2).as_markup()


async def sizes_keyboard(item_id: int):
    item = await get_item_by_id(item_id)
    prices_str = item.prices
    sizes_str = item.sizes

    prices = prices_str.split("/") if prices_str else []
    sizes = sizes_str.split("/") if sizes_str else []

    keyboard = InlineKeyboardBuilder()

    if sizes:
        for i in range(len(sizes)):

            keyboard.add(InlineKeyboardButton(
                text=f'{sizes[i]} - {prices[i]}' if i < len(prices) else sizes[i],
                callback_data=f'size_{item.id}_{sizes[i]}_{prices[i] if i < len(prices) else ""}'
            ))
    else:
        for price in prices:
            keyboard.add(InlineKeyboardButton(
                text=price,
                callback_data=f'price_{item.id}_{price}'
            ))

    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_col'))
    return keyboard.adjust(2).as_markup()


basket_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оформить заказ', callback_data='make_order')],
    [InlineKeyboardButton(text='Очистить корзину', callback_data='clear_basket'),
     InlineKeyboardButton(text='Назад', callback_data='to_main')]
])


add_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='cont')],
    [InlineKeyboardButton(text='Оформить заказ', callback_data='make_order'),
     InlineKeyboardButton(text='Корзина', callback_data='basket')]
])
