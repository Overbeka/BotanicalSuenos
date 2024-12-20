import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand


from config import TEST_TOKEN
from app.database.models import async_main
from app.handlers import router
from app.admin import admin


async def main():

    await async_main()
    bot_commands = [
        BotCommand(command="/start", description="Начать покупки"),
        BotCommand(command="/contacts", description="Список контактов"),
        BotCommand(command="/my_orders", description="Список ваших заказов"),
        BotCommand(command="/admin", description="Команды для администраторов")
    ]

    bot = Bot(token=TEST_TOKEN)
    dp = Dispatcher()
    dp.include_routers(admin, router)
    await bot.set_my_commands(bot_commands)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
