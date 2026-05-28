from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # type: ignore

executor_rules_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Я готов и соблюдаю правила")],
        [KeyboardButton(text="👤 Связаться с оператором")]
    ],
    resize_keyboard=True
)

specialization_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎬 Монтаж видео")],
        [KeyboardButton(text="🎨 Графический дизайн")],
        [KeyboardButton(text="💻 Программирование")],
        [KeyboardButton(text="📱 SMM")]
    ],
    resize_keyboard=True
)