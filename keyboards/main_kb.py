from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # type: ignore


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Покупатель")],
        [KeyboardButton(text="Исполнитель")],
    ],
    resize_keyboard=True
)

buyer_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Монтаж видео")],
        [KeyboardButton(text="Графический дизайн")],
        [KeyboardButton(text="Создание сайтов")],
        [KeyboardButton(text="Продвижение в соц. сетях")],

    ],
    resize_keyboard=True
)

seller_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Монтаж видео")],
        [KeyboardButton(text="Графический дизайн")],
        [KeyboardButton(text="Создание сайтов")],
        [KeyboardButton(text="Продвижение в соц. сетях")],
    ],
    resize_keyboard=True
)