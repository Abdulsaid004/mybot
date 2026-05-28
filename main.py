import asyncio
import os

from aiogram import Bot, Dispatcher, types # type: ignore
from aiogram.filters import CommandStart # type: ignore

from keyboards.main_kb import main_keyboard # type: ignore
from handlers.order import router as order_router # type: ignore
from handlers.db import init_db, save_executor_payment_info # type: ignore




BOT_TOKEN = "8099643683:AAGbB6QxDSU8-f0MLYSKkKgdzJ_34-LKcLM"


async def main() -> None:
    # 1. Инициализация БД
    init_db()

    # 2. Бот и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 3. Подключаем роутеры
    dp.include_router(order_router)

    # 4. Хендлеры
    @dp.message(CommandStart())
    async def start(message: types.Message) -> None:
        await message.answer(
            "👋 Добро пожаловать в Dealix\n\n"
            "Здесь всё просто:\n\n"
            "💼 Нужна услуга? — оставьте заказ\n"
            "🛠 Есть навык? — сможете зарабатывать\n\n"
            "Мы делаем работу удобнее и быстрее\n"
            "без лишних действий и сложностей\n\n"
            "🚀 Это только начало — мы строим новую платформу\n\n"
            "👇 Выберите свою роль:",
            reply_markup=main_keyboard
        )

    
    await dp.start_polling(bot)




if __name__ == "__main__":
    asyncio.run(main())

    

     

