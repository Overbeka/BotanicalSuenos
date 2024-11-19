from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Каталог', callback_data='catalog'),
                                              InlineKeyboardButton(text='Корзина', callback_data='basket')],
                                             [InlineKeyboardButton(text='Контакты', callback_data='contacts')]])


category = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Композиции', callback_data='comp'),
                                                 InlineKeyboardButton(text='Букеты', callback_data='bouquets')],
                                                 [InlineKeyboardButton(text='Назад', callback_data='back')]])

bouquets = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Универсальные', callback_data='unic'),
                                                  InlineKeyboardButton(text='Сезонные', callback_data='season')],
                                                 [InlineKeyboardButton(text='Назад', callback_data='back_to_category')]])


category_compositions = ['Осенние', 'Зимние', 'Цветочные']
category_bouquets = ['Осень', 'Весна', 'Лето']


async def get_composition():
    keyboard = InlineKeyboardBuilder()
    for composition in category_compositions:
        keyboard.add(InlineKeyboardButton(text=composition, callback_data=f'composition_{composition}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_category'))
    return keyboard.adjust(2).as_markup()


async def get_bouquets():
    keyboard = InlineKeyboardBuilder()
    for bouquet in category_bouquets:
        keyboard.add(InlineKeyboardButton(text=bouquet, callback_data=f'bouquet_{bouquet}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_bouquets'))
    return keyboard.adjust(2).as_markup()


async def page_inline(current_page, total_pages):
    keyboard = InlineKeyboardBuilder()
    if current_page > 1:
        keyboard.add(InlineKeyboardButton(text='« Назад', callback_data=f'page_{current_page - 1}'))
    if current_page < total_pages:
        keyboard.add(InlineKeyboardButton(text='Вперед »', callback_data=f'page_{current_page + 1}'))
    return keyboard.adjust().as_markup()



