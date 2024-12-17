from aiogram.fsm.state import State, StatesGroup


class Add(StatesGroup):
    order_contact = State()
    add_questions = State()
    answer_contact = State()


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


class News(StatesGroup):
    message = State()
