from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command


from app import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Добро пожаловать в Botanical Sueños!')
    await message.answer('Выберите пункт меню:', reply_markup=kb.main)


@router.callback_query(F.data == 'back_to_bouquets')
@router.callback_query(F.data == 'back_to_category')
@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    if callback.data == 'back':
        await callback.answer('')
        await callback.message.edit_text('Выберите пункт меню', reply_markup=kb.main)
    elif callback.data == 'back_to_category':
        await callback.answer('')
        await callback.message.edit_text('Выберите категорию товара', reply_markup=kb.category)
    elif callback.data == 'back_to_bouquets':
        await callback.answer('')
        await callback.message.edit_text('Выберите категорию букета:', reply_markup=kb.bouquets)


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите категорию товара:', reply_markup=kb.category)


@router.callback_query(F.data == 'basket')
async def basket(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('В вашей корзине пока-что нет товаров')


@router.callback_query(F.data == 'contacts')
async def contacts(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('''Наш номер телефона: 8911*******, наш instagram:''')


@router.callback_query(F.data == 'comp')
async def composition(callback: CallbackQuery):
    await callback.answer('Вы выбрали Композиции!')
    await callback.message.edit_text('Выберите категорию композиции', reply_markup=await kb.get_composition())


@router.callback_query(F.data == 'bouquets')
async def bouquets(callback: CallbackQuery):
    await callback.answer('Вы выбрали Букеты!')
    await callback.message.edit_text('Выберите категорию букета:', reply_markup=kb.bouquets)


@router.callback_query(F.data == 'unic')
async def bouquet1(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Здесь скоро будут товары!')


@router.callback_query(F.data == 'season')
async def bouquet2(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите сезонность букета:', reply_markup=await kb.get_bouquets())


@router.callback_query(F.data.startswith("page_"))
async def pagination(callback: CallbackQuery):
    pass
