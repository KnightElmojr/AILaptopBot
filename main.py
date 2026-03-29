import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import router
from database import init_db


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот вимкнений")