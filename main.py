import asyncio
import os

from aiogram import Bot, Dispatcher, types # type: ignore
from aiogram.filters import CommandStart # type: ignore

from keyboards.main_kb import main_keyboard # type: ignore
from handlers.order import router as order_router # type: ignore
from handlers.db import init_db # type: ignore


BOT_TOKEN = "ТВОЙ_ТОКЕН_СЮДА"


async def main() -> None:
    # 1. Инициализация БД
    await init_db()

    # 2. Бот и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 3. Подключаем роутеры
    dp.include_router(order_router)

    # 4. Хендлеры
    @dp.message(CommandStart())
    async def start(message: types.Message) -> None:
        await message.answer(
            "Добро пожаловать в Dealix 🚀\n\n"
            "Выберите свою роль:",
            reply_markup=main_keyboard
        )

    @dp.message(lambda message: message.chat.type in ["supergroup"])
    async def debug_topic(message: types.Message):
        print("CHAT ID:", message.chat.id)
        print("THREAD ID:", message.message_thread_id)
        print("TEXT:", message.text)

    # ❗ ВАЖНО: только ОДИН запуск в самом конце
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



