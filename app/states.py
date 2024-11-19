from aiogram.fsm.state import State, StatesGroup


class PhotoState(StatesGroup):
    viewing = State()
