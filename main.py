import asyncio 
from aiogram import Bot, Dispatcher, types # type: ignore
from aiogram.filters import CommandStart # type: ignore
from keyboards.main_kb import main_keyboard # type: ignore
from handlers.order import router as order_router  # type: ignore
from handlers.db import init_db  # type: ignore

TOKEN = "8099643683:AAFvkURV3viUMMyZUoFZowQOe0P3jFO7itA"
 

async def main() -> None:
    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(order_router)

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


    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



