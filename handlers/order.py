from .db import create_order, add_order_file, get_order_files, get_order, take_order, update_order_status, update_order_materials
from aiogram import Router, types, F # type: ignore
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton # type: ignore
from keyboards.main_kb import buyer_keyboard, seller_keyboard, materials_done_kb    # type: ignore
from handlers.db import get_final_file, save_final_file, save_executor_payment_info # type: ignore 
import re

def calc_payout(price: int, commission: int = 15):
    platform_profit = int(price * commission / 100)
    executor_payout = price - platform_profit
    return platform_profit, executor_payout 

router = Router()

def get_order_interest_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🙋 Готов выполнить",
                    callback_data=f"interested_order:{order_id}"
                )
            ]
        ]
    )

def get_payment_confirm_kb(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Оплата подтверждена",
                    callback_data=f"payment_ok:{order_id}"
                )
            ]
        ]
    )

def get_client_result_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"accept_order:{order_id}"
                ),
                InlineKeyboardButton(
                    text="🔄 Доработка",
                    callback_data=f"revision_order:{order_id}"
                )
            ]
        ]
    )

executor_rules_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Я готов и соблюдаю правила")],
        [KeyboardButton(text="👤 Связаться с оператором")]
    ],
    resize_keyboard=True
)

specialization_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Монтаж видео")],
        [KeyboardButton(text="Графический дизайн")],
        [KeyboardButton(text="Программирование")],
        [KeyboardButton(text="Продвижение в соц. сетях")],
    ],
    resize_keyboard=True
)

GROUP_LINK = "https://t.me/DealixNetwork"

NEW = "new"
WAITING_PAYMENT = "waiting_payment"
PAID = "paid"
PUBLISHED = "published"
IN_PROGRESS = "in_progress"
SUBMITTED = "submitted"
REVISION = "revision"
COMPLETED = "completed"
CANCELLED = "cancelled"

def get_user_display(user):
    if user.username:
        return f"@{user.username}"

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if full_name:
        return full_name

    return f"ID {user.id}"

user_state = {}
reply_map = {}

SERVICES = [
    "Монтаж видео",
    "🎬 Монтаж видео",
    "Графический дизайн",
    "🎨 Графический дизайн",
    "Программирование",
    "💻 Программирование",
    "Продвижение в соц. сетях",
    "📱 SMM",
]

ADMIN_ID = 8549756250

SELLER_CHATS = {
    "Монтаж видео": {
        "chat_id": -1003988228980,
        "thread_id": 5,
    },
    "Графический дизайн": {
        "chat_id": -1003988228980,
        "thread_id": 6,
    },
    "Программирование": {
        "chat_id": -1003988228980,
        "thread_id": 4,
    },
    "Продвижение в соц. сетях": {
        "chat_id": -1003988228980,
        "thread_id": 21,
    },
}

@router.message(lambda message: message.text == "Покупатель")
async def choose_buyer(message: types.Message):
    user_state[message.from_user.id] = {"role": "buyer"}

    await message.answer(
        "👤 Вы выбрали роль: Покупатель\n\n"
        "Добро пожаловать в Dealix.\n\n"
        "Здесь вы можете заказать услуги у исполнителей в разных направлениях:\n\n"
        "🎬 Монтаж видео\n"
        "— Reels / Shorts / YouTube / TikTok / реклама\n\n"
        "🎨 Графический дизайн\n"
        "— логотипы / баннеры / превью / оформление\n\n"
        "💻 Программирование\n"
        "— Telegram-боты / сайты / backend / automation\n\n"
        "📱 SMM / продвижение\n"
        "— Instagram / TikTok / Telegram / контент\n\n"
        "💰 Минимальный заказ: от 500 сом\n\n"
        "⚠️ Перед созданием заявки:\n\n"
        "— описывайте задачу максимально подробно\n"
        "— прикрепляйте материалы при наличии\n"
        "— указывайте реальные сроки и бюджет\n"
        "— вся работа проходит через систему\n"
        "— уважайте время и труд исполнителей\n\n"
        "🤝 Мы стремимся строить честную систему,\n"
        "где навык, ответственность и польза ценятся выше слов.\n\n"
        "📌 Пусть каждая работа будет выполнена качественно,\n"
        "а сотрудничество принесёт пользу обеим сторонам.\n\n"
        "BarakAllahu feekum.\n\n"
        "📋 После этого выберите нужную категорию услуги ниже.",
        reply_markup=buyer_keyboard
    )

@router.message(lambda message: message.text == "Исполнитель")
async def choose_seller(message: types.Message):
    user_state[message.from_user.id] = {"role": "seller"}

    text =  """
    🚀 Добро пожаловать в Dealix!

    Перед началом работы ознакомьтесь с правилами платформы.

    📌 Как работает Dealix:

    1️⃣ Клиент оставляет заявку через бота  
    2️⃣ Заказ публикуется по нужной категории  
    3️⃣ Исполнитель откликается на заказ  
    4️⃣ После назначения исполнитель выполняет работу  
    5️⃣ Готовый результат отправляется через бота  
    6️⃣ Клиент принимает работу или просит доработку  
    7️⃣ После подтверждения исполнитель получает оплату

    ⭐ Как повысить уровень:

    — Выполняйте заказы качественно  
    — Соблюдайте сроки  
    — Не берите заказ, если не уверены  
    — Не пропадайте после принятия заказа  

    Чем выше доверие к исполнителю — тем больше заказов и выше приоритет.

    💰 Комиссия платформы:

    Комиссия Dealix составляет 10–15% от суммы заказа.

    Зависит от уровня исполнителя:
    — 🆕 Новый: 15%
    — ✅ Проверенный: 12%
    — 🏆 Топ: 10%

    ⛔ Нарушения (приводят к бану):

    — Срыв сроков без предупреждения  
    — Отказ от заказа после принятия  
    — Некачественная работа  
    — Попытка связаться с клиентом вне платформы  
    — Обман клиента или платформы  
    — Грубое общение  
    — Спам  

    📩 Поддержка:

    Если возникли вопросы или проблемы — пишите оператору:
    👉 @asa_d28

    Оператор помогает:
    — разобраться с заказом  
    — объяснить процесс работы  
    — решить спорные ситуации  

    ⚠️ Важно:

    — Вся работа проходит только через Dealix  
    — Все действия фиксируются системой  
    — Нарушения влияют на ваш уровень и доступ к заказам  

    ⚠️ Если вы согласны с правилами — нажмите кнопку ниже.
    """

    await message.answer(
        text,
        reply_markup=executor_rules_keyboard
    )

#@router.message(lambda message: message.text is not None and "✅ Готово" in message.text)
#async def executor_accept_rules(message: types.Message):
#    await message.answer(
#        "Выберите свою специализацию:",
#        reply_markup=specialization_keyboard
#    )  

@router.message(lambda message: message.text == "👤 Связаться с оператором")
async def contact_operator(message: types.Message):
    username = message.from_user.username
    full_name = message.from_user.full_name
    user_id = message.from_user.id

    sent = await message.bot.send_message(
        ADMIN_ID,
        f"""
        📩 Запрос оператору

        👤 Имя: {full_name}
        🔗 Username: @{username if username else "нет username"}
        🆔 ID: {user_id}
        """
    )

    reply_map[sent.message_id] = user_id

    await message.answer("✅ Запрос отправлен оператору")

@router.message(lambda message: message.from_user.id == ADMIN_ID and message.reply_to_message)
async def admin_reply(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        return

    msg_id = message.reply_to_message.message_id

    if msg_id not in reply_map:
        return

    user_id = reply_map[msg_id]

    await message.bot.send_message(
        user_id,
        f"👤 Оператор:\n{message.text}"
    )

    await message.answer("✅ Ответ отправлен") 
       
@router.message(lambda message: (
    message.text in ["🎬 Монтаж видео", "Монтаж видео"]
    and user_state.get(message.from_user.id, {}).get("role") == "seller"
))
async def choose_edit_seller(message: types.Message):
    user_state[message.from_user.id]["category"] = "edit"
    user_state[message.from_user.id]["service"] = "Монтаж видео"
    user_state[message.from_user.id]["step"] = "seller_form"

    await message.answer(
        "🎬 Специализация: Монтаж видео\n\n"
        "Отправьте анкету по шаблону:\n\n"
        "1. Имя\n"
        "2. Опыт\n"
        "3. Какие услуги оказываете\n"
        "4. Портфолио / примеры работ\n"
        "5. Telegram для связи"
    )

@router.message(lambda message: (
    message.text in ["🎨 Графический дизайн", "Графический дизайн"]
    and user_state.get(message.from_user.id, {}).get("role") == "seller"
))
async def choose_design_seller(message: types.Message):
    user_state[message.from_user.id]["category"] = "design"
    user_state[message.from_user.id]["service"] = "Графический дизайн"
    user_state[message.from_user.id]["step"] = "seller_form"

    await message.answer(
        "🎨 Специализация: Графический дизайн\n\n"
        "Отправьте анкету по шаблону:\n\n"
        "1. Имя\n"
        "2. Опыт\n"
        "3. Какие услуги оказываете\n"
        "4. Портфолио / примеры работ\n"
        "5. Telegram для связи"
    )

@router.message(lambda message: (
    message.text in ["💻 Программирование", "Программирование"]
    and user_state.get(message.from_user.id, {}).get("role") == "seller"
))
async def choose_programming_seller(message: types.Message):
    user_state[message.from_user.id]["category"] = "programming"
    user_state[message.from_user.id]["service"] = "Программирование"
    user_state[message.from_user.id]["step"] = "seller_form"

    await message.answer(
        "💻 Специализация: Программирование\n\n"
        "Отправьте анкету по шаблону:\n\n"
        "1. Имя\n"
        "2. Опыт\n"
        "3. Какие услуги оказываете\n"
        "4. Портфолио / примеры работ\n"
        "5. Telegram для связи"
    )

@router.message(lambda message: (
    message.text in ["📱 SMM", "SMM", "Продвижение в соц. сетях"]
    and user_state.get(message.from_user.id, {}).get("role") == "seller"
))
async def choose_smm_seller(message: types.Message):
    user_state[message.from_user.id]["category"] = "smm"
    user_state[message.from_user.id]["service"] = "SMM"
    user_state[message.from_user.id]["step"] = "seller_form"

    await message.answer(
        "📱 Специализация: SMM\n\n"
        "Отправьте анкету по шаблону:\n\n"
        "1. Имя\n"
        "2. Опыт\n"
        "3. Какие услуги оказываете\n"
        "4. Портфолио / примеры работ\n"
        "5. Telegram для связи"
    )

@router.message(
    lambda message:
    message.text
    and message.text.strip() in SERVICES
    and user_state.get(message.from_user.id, {}).get("step") is None
)
async def choose_service(message: types.Message):
    print("CHOOSE_SERVICE:", repr(message.text))
    state = user_state.get(message.from_user.id)
    print("STATE IN SERVICE:", state)

    if not state:
        await message.answer("Сначала выберите роль: /start")
        return

    role = state.get("role")
    service = message.text.strip()

    user_state[message.from_user.id]["service"] = service

    if role == "buyer":
        user_state[message.from_user.id]["step"] = "buyer_form"

        if service == "Монтаж видео":
            form_text = (
                f"🎬 Услуга: {service}\n\n"
                "📋 Заполните заявку:\n\n"
                "1️⃣ 🎞 Что нужно смонтировать:\n"
                "(Reels / Shorts / YouTube / реклама / TikTok)\n\n"
                "2️⃣ ✨ Формат и стиль:\n"
                "(динамичный / cinematic / minimal / viral)\n\n"
                "3️⃣ 📂 Исходные материалы:\n"
                "(видео / фото / музыка / озвучка)\n\n"
                "4️⃣ 🔗 Референсы:\n"
                "(примеры или ссылки на стиль)\n\n"
                "5️⃣ ⏳ Срок:\n"
                "(когда нужен готовый результат)\n\n"
                "6️⃣ 💰 Бюджет:\n"
                "(сумма или диапазон)\n\n"
                "7️⃣ 📱 Telegram для связи:\n"
                "(@username)\n\n"
                "⚡ Чем подробнее заявка — тем лучше результат."
            )
        elif service == "Графический дизайн":
            form_text = (
                f"🎨 Услуга: {service}\n\n"
                "📋 Заполните заявку:\n\n"
                "1️⃣ 🖌 Что нужно создать:\n"
                "(логотип / баннер / постер / превью / бренд)\n\n"
                "2️⃣ 🎯 Стиль дизайна:\n"
                "(minimal / modern / dark / premium)\n\n"
                "3️⃣ 📂 Материалы:\n"
                "(текст / фото / цвета / логотипы)\n\n"
                "4️⃣ 🔗 Референсы:\n"
                "(примеры или ссылки)\n\n"
                "5️⃣ ⏳ Срок:\n"
                "(когда нужен готовый результат)\n\n"
                "6️⃣ 💰 Бюджет:\n"
                "(сумма или диапазон)\n\n"
                "7️⃣ 📱 Telegram для связи:\n"
                "(@username)\n\n"
                "⚡ Чем подробнее заявка — тем лучше результат."
            )
        elif service == "Программирование":
            form_text = (
                f"💻 Услуга: {service}\n\n"
                "📋 Заполните заявку:\n\n"
                "1️⃣ ⚙️ Что нужно разработать:\n"
                "(бот / сайт / приложение / парсер)\n\n"
                "2️⃣ 🧩 Функции проекта:\n"
                "(что именно должно работать)\n\n"
                "3️⃣ 📂 Материалы:\n"
                "(дизайн / тз / примеры / api)\n\n"
                "4️⃣ 🔗 Примеры:\n"
                "(ссылки или референсы)\n\n"
                "5️⃣ ⏳ Срок:\n"
                "(когда нужен готовый результат)\n\n"
                "6️⃣ 💰 Бюджет:\n"
                "(сумма или диапазон)\n\n"
                "7️⃣ 📱 Telegram для связи:\n"
                "(@username)\n\n"
                "⚡ Чем подробнее заявка — тем лучше результат."
            )
        elif service == "Продвижение в соц. сетях":
            form_text = (
                f"📈 Услуга: {service}\n\n"
                "📋 Заполните заявку:\n\n"
                "1️⃣ 🚀 Что нужно продвигать:\n"
                "(Instagram / TikTok / YouTube / Telegram)\n\n"
                "2️⃣ 🎯 Цель продвижения:\n"
                 "(подписчики / продажи / охваты / бренд)\n\n"
                "3️⃣ 📂 Материалы:\n"
                "(аккаунт / контент / ссылки)\n\n"
                "4️⃣ 🔗 Примеры:\n"
                "(конкуренты или референсы)\n\n"
                "5️⃣ ⏳ Срок:\n"
                "(на какой период нужно продвижение)\n\n"
                "6️⃣ 💰 Бюджет:\n"
                "(сумма или диапазон)\n\n"
                "7️⃣ 📱 Telegram для связи:\n"
                "(@username)\n\n"
                "⚡ Чем подробнее заявка — тем лучше результат."
            )
        else:
            form_text = (
                f"📦 Услуга: {service}\n\n"
                "📋 Заполните заявку:\n\n"
                "1️⃣ Что нужно сделать\n"
                "2️⃣ Срок\n"
                "3️⃣ Бюджет\n"
                "4️⃣ Материалы / ссылки\n"
                "5️⃣ Telegram (@username)"
            )

        await message.answer(form_text)

    elif role == "seller":
        user_state[message.from_user.id]["step"] = "seller_form"

        await message.answer(
            f"💻 Специализация: {service}\n\n"
            "📋 Отправьте анкету по шаблону:\n\n"
            "1️⃣ Имя\n"
            "2️⃣ Опыт\n"
            "3️⃣ Какие услуги оказываете\n"
            "4️⃣ Портфолио / примеры работ\n"
            "🔗 Добавьте ссылку на Google Drive / Яндекс Диск / Behance / GitHub / облачное хранилище\n"
            "5️⃣ Telegram для связи\n\n"
            "⚠️ Чем сильнее и понятнее ваше портфолио — "
            "тем выше шанс получать хорошие заказы.\n\n"
            "🤝 В Dealix ценятся ответственность, "
            "качество и честная работа.\n\n"
            "BarakAllahu feekum."
        )

@router.message(
    lambda message: user_state.get(
        message.from_user.id, {}
    ).get("step") == "waiting_receipt"
)
async def process_receipt(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    order_id = state["order_id"]
    order = get_order(order_id)

    if not order:
        await message.answer("Заказ не найден.")
        del user_state[message.from_user.id]
        return

    if not message.photo and not message.document:
        await message.answer(
            "❌ Отправьте чек фото или документом."
        )
        return

    if message.photo:
        receipt_file_id = message.photo[-1].file_id
        receipt_type = "photo"
    else:
        receipt_file_id = message.document.file_id
        receipt_type = "document"

    order["receipt_file_id"] = receipt_file_id
    order["receipt_type"] = receipt_type

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить оплату",
                    callback_data=f"confirm_payment:{order_id}"
                )
            ]
        ]
    )

    caption = (
        f"💳 Новый чек оплаты\n\n"
        f"📦 Заказ #{order_id}\n"
        f"👤 Клиент ID: {message.from_user.id}"
    )

    if receipt_type == "photo":
        await message.bot.send_photo(
            ADMIN_ID,
            photo=receipt_file_id,
            caption=caption,
            reply_markup=kb
        )
    else:
        await message.bot.send_document(
            ADMIN_ID,
            document=receipt_file_id,
            caption=caption,
            reply_markup=kb
        )

    await message.answer(
        "✅ Чек отправлен на проверку оператору.\n\n"
        "Ожидайте подтверждения оплаты."
    )

    del user_state[message.from_user.id]  

@router.message(
    lambda message: user_state.get(message.from_user.id, {}).get("role") == "executor_upload"
)
async def upload_ready_material(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    order_id = state["order_id"]
    order = get_order(order_id)

    if not order:
        await message.answer("❌ Заказ не найден.")
        del user_state[message.from_user.id]
        return

    if str(order["executor_id"]) != str(message.from_user.id):
        await message.answer("❌ Ты не исполнитель этого заказа.")
        del user_state[message.from_user.id]
        return

    file_type = None
    file_id = None

    if message.photo:
        file_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        file_type = "video"
        file_id = message.video.file_id
    elif message.document:
        file_type = "document"
        file_id = message.document.file_id
    else:
        await message.answer(
            "📤 Теперь отправьте готовый файл.\n\n"
            "Поддерживаются:\n"
            "🎬 Видео\n"
            "🖼 Фото\n"
            "📄 Документ\n\n"
            "⚠️ Не отправляйте текст отдельно.\n"
            "Просто прикрепите исправленный материал."
        )
        return

    if state.get("step") == "waiting_preview":
        state["preview_file_type"] = file_type
        state["preview_file_id"] = file_id
        state["preview_caption"] = message.caption or ""

        state["step"] = "waiting_final"

        await message.answer(
            "✅ Preview получен.\n\n"
            "Теперь отправьте финальный файл в хорошем качестве.\n"
            "Он будет сохранён и отправлен клиенту только после оплаты."
        )
        return
    
    if state.get("step") == "waiting_final":
        state["final_file_type"] = file_type
        state["final_file_id"] = file_id
        state["final_caption"] = message.caption or ""

        save_final_file(order_id, file_type, file_id)

        preview_type = state["preview_file_type"]
        preview_id = state["preview_file_id"]

        caption = (
            f"📦 Preview по заказу #{order_id}\n\n"
            f"Проверьте результат.\n"
            f"Если всё подходит — нажмите «✅ Принять».\n"
            f"Финальный файл будет отправлен после оплаты."
        )

        if preview_type == "photo":
            await message.bot.send_photo(
                order["client_id"],
                photo=preview_id,
                caption=caption,
                reply_markup=get_client_result_kb(order_id)
            )
        elif preview_type == "video":
            await message.bot.send_video(
                order["client_id"],
                video=preview_id,
                caption=caption,
                reply_markup=get_client_result_kb(order_id)
            )
        elif preview_type == "document":
            await message.bot.send_document(
                order["client_id"],
                document=preview_id,
                caption=caption,
                reply_markup=get_client_result_kb(order_id)
            )

        update_order_status(order_id, SUBMITTED)

        await message.answer("✅ Preview отправлен клиенту. Финальный файл сохранён.")

        await message.bot.send_message(
            ADMIN_ID,
            f"📨 Исполнитель отправил preview и final\n\n"
            f"📦 Заказ #{order_id}\n"
            f"👤 Исполнитель ID: {message.from_user.id}\n"
            f"📌 Статус: {SUBMITTED}"
        )

        return

@router.message(F.photo | F.video | F.document | F.audio | F.voice)
async def save_client_materials(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Сначала заполните заявку текстом.")
        return 

    if state.get("step") == "waiting_upload":
        return

    if state.get("step") != "waiting_files":
        await message.answer("Сначала заполните заявку текстом.")
        return

    order_id = state["order_id"]

    if message.photo:
        add_order_file(order_id, "photo", message.photo[-1].file_id)
    elif message.video:
        add_order_file(order_id, "video", message.video.file_id)
    elif message.document:
        add_order_file(order_id, "document", message.document.file_id)
    elif message.audio:
        add_order_file(order_id, "audio", message.audio.file_id)
    elif message.voice:
        add_order_file(order_id, "voice", message.voice.file_id)

    await message.answer(
        "✅ Материал получен.\n"
        "Можете отправить ещё файл или нажать «Готово».",
        reply_markup=materials_done_kb
    )

@router.message(F.text == "✅ Я готов и соблюдаю правила")
async def executor_ready(message: types.Message):
    user_state[message.from_user.id] = {
        "role": "seller",
        "step": "choose_specialization"
    }

    await message.answer(
        "Выберите направление:",
        reply_markup=specialization_keyboard
    )

@router.message(lambda message: message.text and message.text.startswith("/ready_"))
async def start_ready_order(message: types.Message):
    try:
        order_id = int(message.text.replace("/ready_", ""))
    except ValueError:
        await message.answer("Неверный формат. Пример: /ready_1")
        return

    order = get_order(order_id)

    if not order:
        await message.answer(f"Заказ #{order_id} не найден.")
        return

    print("ORDER STATUS:", order["status"])
    print("ORDER EXECUTOR_ID:", order["executor_id"])
    print("MESSAGE USER_ID:", message.from_user.id)

    if order["status"] not in ["taken", "waiting_upload", "revision", "submitted"]:
        await message.answer("Этот заказ нельзя завершить сейчас.")
        return

    if str(order["executor_id"]) != str(message.from_user.id):
        await message.answer("Ты не исполнитель этого заказа.")
        return

    user_state[message.from_user.id] = {
        "role": "executor_upload",
        "step": "waiting_preview",
        "order_id": order_id,
    }

    update_order_status(order_id, "waiting_upload")
    await message.answer(
        "📤 Сначала отправьте Preview-файл.\n\n"
        "Это файл для проверки клиентом:\n"
        "— можно с водяным знаком\n"
        "— можно в низком качестве\n\n"
        "После этого бот попросит финальный файл."
    )
 
@router.message(lambda message: user_state.get(message.from_user.id, {}).get("step") == "waiting_revision_text")
async def process_revision_text(message: types.Message):
    state = user_state.get(message.from_user.id)
    order_id = state["order_id"]
    order = get_order(order_id)

    if not order:
        await message.answer("Заказ не найден.")
        del user_state[message.from_user.id]
        return
    
    executor_id = order["executor_id"]

    user_state.pop(executor_id, None)

    user_state[executor_id] = {
        "role": "executor_upload",
        "step": "waiting_preview",
        "order_id": order_id
    }

    await message.bot.send_message(
        order["executor_id"],
        f"🔁 Клиент отправил заказ #{order_id} на доработку.\n\n"
        f"📝 Что исправить:\n{message.text}\n\n"
        f"После исправления отправьте результат снова:\n"
        f"/ready_{order_id}"
    )

    update_order_status(order_id, REVISION)

    await message.answer("✅ Доработка отправлена исполнителю.")
    del user_state[message.from_user.id]

@router.message(
    lambda message: user_state.get(
        message.from_user.id, {}
    ).get("step") == "waiting_payment_check"
)
async def process_payment_check(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    order_id = state["order_id"]
    order = get_order(order_id)

    if not order:
        await message.answer("Заказ не найден.")
        return

    update_order_status(order_id, "payment_check")

    text = (
        f"💳 Клиент отправил чек по заказу #{order_id}\n\n"
        f"Проверь оплату вручную.\n"
        f"Если всё верно — нажми кнопку ниже."
    )

    if message.photo:
        await message.bot.send_photo(
            ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=text,
            reply_markup=get_payment_confirm_kb(order_id)
        )
    elif message.document:
        await message.bot.send_document(
            ADMIN_ID,
            document=message.document.file_id,
            caption=text,
            reply_markup=get_payment_confirm_kb(order_id)
        )
    else:
        await message.bot.send_message(
            ADMIN_ID,
            text,
            reply_markup=get_payment_confirm_kb(order_id)
        )

    await message.answer(
        "✅ Чек отправлен администрации.\n"
        "После проверки бот выдаст финальный файл."
    )

    del user_state[message.from_user.id]

@router.message(
    lambda message: user_state.get(
        message.from_user.id, {}
    ).get("step") == "waiting_review"
)
async def process_review(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    order_id = state["order_id"]
    executor_id = state["executor_id"]
    executor_username = state["executor_username"]

    review_text = message.text or "Без текста"
    lines = review_text.splitlines()

    executor_review = ""
    if len(lines) >= 2:
        executor_review = f"{lines[0]}\n{lines[1]}"
    else:
        executor_review = review_text

    await message.bot.send_message(
        ADMIN_ID,
        f"⭐ Новый отзыв по заказу #{order_id}\n\n"
        f"👤 Исполнитель: @{executor_username}\n"
        f"🆔 ID: {executor_id}\n\n"
        f"📝 Отзыв клиента:\n{review_text}"
    )

    order = get_order(order_id)

    price_text = str(order.get("price", "")) + "\n" + str(order.get("description", ""))
    numbers = re.findall(r"\d+", price_text)
    price = max([int(n) for n in numbers], default=0)

    commission = 15
    platform_profit = int(price * commission / 100)
    executor_payout = price - platform_profit

    await message.bot.send_message(
        executor_id,
        f"⭐ Отзыв по заказу #{order_id}\n\n"
        f"📝 Отзыв клиента:\n{review_text}\n\n"
        f"📄 Чек по заказу #{order_id}\n\n"
        f"✅ Работа принята клиентом\n"
        f"💰 Сумма заказа: {price} сом\n"
        f"💼 Комиссия Dealix: {commission}%\n"
        f"📌 К выплате: {executor_payout} сом\n\n"
        f"⏳ Статус выплаты: ожидает перевода оператором"
    )

    await message.bot.send_message(
        executor_id,
        "🤝 ДжазакаЛлаху хайран за ваш труд.\n"
        "Пусть Аллах примет ваши старания "
        "и даст баракат в вашем ризке.\n\n"
        "📿 В Dealix мы хотим строить работу "
        "на честности, аманате и уважении "
        "между людьми.\n\n"
        "⚙️ Каждый выполненный вами заказ — "
        "это не только работа, но и ответственность "
        "перед людьми за качество и сроки.\n\n"
        "📈 Чем лучше вы работаете — "
        "тем выше ваше доверие и положение "
        "внутри Dealix.\n\n"
        "🤲 Пусть Аллах откроет для вас "
        "двери полезного ризка, защитит от "
        "нечестного заработка и даст успех "
        "в ваших делах.\n\n"
        "🕌 Мы ценим исполнителей, "
        "которые работают искренне и достойно.\n\n"
        "BarakAllahu feekum."
    )

    await message.answer(
        "✅ ДжазакаЛлаху хайран за отзыв.\n\n"
        "🤝 Ваш заказ успешно завершён через Dealix.\n"
        "Пусть Аллах даст баракат в вашем деле "
        "и принесёт пользу через этот проект.\n\n"
        "📌 Если вам снова понадобится:\n"
        "🎬 Монтаж видео\n"
        "🎨 Дизайн\n"
        "💻 Программирование\n"
        "📈 Продвижение\n\n"
        "— вы всегда можете обратиться через Dealix.\n\n"
        "⚙️ Наша цель — строить систему "
        "без хаоса, обмана и лишних сложностей, "
        "где люди могут честно работать и сотрудничать.\n\n"
        "🤲 Пусть Аллах облегчит ваши дела "
        "и даст вам пользу в том, что вы делаете.\n\n"
        "BarakAllahu feekum."
   )

    del user_state[message.from_user.id]
    
@router.message(F.text)
async def process_forms(message: types.Message):
    print("PROCESS_FORMS STARTED")
    print("TEXT:", repr(message.text))
    print("STATE:", user_state.get(message.from_user.id))
    
    state = user_state.get(message.from_user.id)
    if state and state.get("step") == "waiting_files":
        if message.text == "✅ Готово, отправить заказ":
            materials_text = state.get("materials_text", "не указано")
            update_order_materials(state["order_id"], materials_text)

            await message.bot.send_message(
                state["chat_id"],
                state["executor_text"] + f"\n\n📁 Материалы / информация:\n{materials_text}",
                message_thread_id=state["thread_id"],
                reply_markup=get_order_interest_kb(state["order_id"])
            )
            
            await message.bot.send_message(
                ADMIN_ID,
                state["admin_text"] + f"\n\n📁 Материалы / информация:\n{materials_text}"
            )

            await message.answer("✅ Заказ отправлен оператору.")
            del user_state[message.from_user.id]
            return

        state["materials_text"] += message.text + "\n"
        await message.answer("Материалы / информация сохранены ✅")
        return

    if state and state.get("step") == "waiting_executor_payment_info":
        order_id = state["order_id"]
        payment_info = message.text or "Без текста"

        order = get_order(order_id)
        if not order:
            await message.answer("Заказ не найден.")
            del user_state[message.from_user.id]
            return

        executor_username = order.get("executor_username", "нет username")
        price_raw = str(order.get("price", "0"))
        numbers = re.findall(r"\d+", price_raw)
        price = int(numbers[-1]) if numbers else 0

        platform_profit, executor_payout = calc_payout(price)

        try:
            await message.bot.send_message(
                ADMIN_ID,
                f"💳 Исполнитель отправил реквизиты\n\n"
                f"📦 Заказ #{order_id}\n"
                f"👤 Исполнитель: {executor_username}\n"
                f"🆔 ID: {message.from_user.id}\n"
                f"💰 Сумма заказа: {price} сом\n"
                f"💼 Комиссия Dealix: 15% = {platform_profit} сом\n"
                f"📌 Перевести исполнителю: {executor_payout} сом\n\n"
                f"🏦 Реквизиты:\n{payment_info}"
            )
        except Exception as e:
            print("ERROR SEND PAYMENT INFO:", e)
            await message.answer(
                "❌ Ошибка отправки реквизитов оператору."
            )
            return

        await message.answer(
            "✅ Реквизиты успешно приняты.\n\n"
            "💸 После проверки оператор отправит выплату "
            "на указанные реквизиты.\n\n"
            "🤲 Пусть Аллах даст баракат "
            "в вашем ризке и вашем труде.\n\n"
            "BarakAllahu feekum."
        )

        del user_state[message.from_user.id]
        return

    if message.text is None:
        return

    if not state:
        return
    
    if state.get("step") == "waiting_upload":
        return

    role = state.get("role")
    step = state.get("step")
    service = state.get("service")
    if not service:
        await message.answer("Ошибка: услуга не выбрана. Начни заново: /start")
        return
    
    text = message.text or ""

    lines = text.splitlines()

    if step == "seller_form":
        if len(lines) < 5:
            await message.answer(
                "❌ Анкета заполнена неполностью\n\n"
                "Нужно 5 пунктов:\n"
                "1. Имя\n"
                "2. Опыт\n"
                "3. Услуги\n"
                "4. Портфолио\n"
                "5. Telegram (@username)"
            )
            return

    if "@" not in text:
        await message.answer("❌ Укажите Telegram: @username")
        return

    username = message.from_user.username
    user = f"@{username}" if username else "нет username"
    
    if role == "buyer" and step == "buyer_form":
        user_state[message.from_user.id]["order_text"] = message.text
        user_state[message.from_user.id]["step"] = "waiting_files"
        chat_data = SELLER_CHATS.get(service)

        if not chat_data:
            await message.answer("Ошибка: чат для этой категории не найден.")
            return

        chat_id = chat_data["chat_id"]
        thread_id = chat_data["thread_id"]

        raw_lines = text.splitlines()

        clean_text = "\n".join(
            line for line in raw_lines
            if "@" not in line
            and "t.me" not in line.lower()
            and "telegram" not in line.lower()
        )

        lines = clean_text.splitlines()

        task_line = lines[0] if len(lines) > 0 else "Не указано"
        style_line = lines[1] if len(lines) > 1 else "Не указано"
        materials_line = lines[2] if len(lines) > 2 else "Не указано"
        reference_line = lines[3] if len(lines) > 3 else "Не указано"
        deadline_line = lines[4] if len(lines) > 4 else "Не указано"
        budget_line = lines[5] if len(lines) > 5 else "Не указано"

        order_id = create_order(
            client_id=message.from_user.id,
            client_username=username,
            category=service,
            description=text,
            price=budget_line
        )

        executor_text = (
            f"📦 Новый заказ #{order_id}\n\n"
            f"🔧 Услуга: {service}\n\n"
            f"📝 Что нужно:\n{task_line}\n\n"
            f"🎨 Стиль:\n{style_line}\n\n"
            f"📂 Материалы:\n{materials_line}\n\n"
            f"🔗 Референсы:\n{reference_line}\n\n"
            f"⏰ Срок:\n{deadline_line}\n\n"
            f"💰 Бюджет:\n{budget_line} сом\n\n"
            f"🔒 Клиент скрыт. Работа только через бота.\n"
            f"📌 Статус: waiting_executor"
        )     
        
        admin_text = (
            f"📦 Новый заказ #{order_id}\n\n"
            f"🔧 Услуга: {service}\n"
            f"👤 Клиент: {user}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"📄 Текст заявки:\n{text}\n\n"
            f"📨 Отправлено в чат: {chat_id}\n"
            f"📌 Статус: published"
        )  

        user_state[message.from_user.id] = {
            "role": "buyer",
            "service": service,
            "step": "waiting_files",
            "order_id": order_id,
            "chat_id": chat_id,
            "thread_id": thread_id,
            "executor_text": executor_text,
            "admin_text": admin_text,
            "materials_text": ""
        }

        await message.answer(
            "📁 Теперь отправьте материалы или информацию для заказа.\n\n"
            "🎞 Можно отправить несколько файлов подряд:\n"
            "— фото\n"
            "— видео\n"
            "— документы\n"
            "— ссылки\n"
            "— техническое задание\n\n"
            "❓ Если материалов нет — просто опишите:\n"
            "— что именно вам нужно\n"
            "— какой стиль или результат вы хотите\n"
            "— примеры или референсы (если есть)\n"
            "— сроки и важные детали\n\n"
            "🆓 На данный момент Dealix может помочь с подбором материалов или референсов бесплатно.\n\n"
            "✅ Когда закончите — нажмите «Готово, отправить заказ».",
            reply_markup=materials_done_kb
        )
        return

    if role == "seller" and step == "seller_form":
        chat_data = SELLER_CHATS.get(service)

        if not chat_data:
            await message.answer("Ошибка: чат для этой категории не найден.")
            return

        chat_id = chat_data["chat_id"]
        thread_id = chat_data["thread_id"]

        await message.answer(
            "✅ Анкета отправлена\n\n"
            "Теперь вступите в рабочую группу:\n"
           f"{GROUP_LINK}\n\n"
            "После вступления вы сможете видеть заказы и откликаться на них."
        )

        await message.bot.send_message(
            ADMIN_ID,
            f"🧑‍💻 Новый исполнитель\n\n"
            f"🛠 Специализация: {service}\n"
            f"👤 Контакт: {user}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"📄 Анкета:\n{text}"
        )

        await message.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=(
                f"👨‍💻 Новый исполнитель\n\n"
                f"🛠 Специализация: {service}\n"
                f"👤 Контакт: {user}\n"
                f"🆔 ID: {message.from_user.id}\n\n"
                f"📄 Анкета:\n{text}"
            )
        )

        del user_state[message.from_user.id]
        return

@router.callback_query(lambda c: c.data.startswith("interested_order:"))
async def interested_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)

    print("ORDER DETAILS:", order) 
    

    if not order:
        await callback.answer("❌ Заказ не найден", show_alert=True)
        return

    if order.get("status") != "waiting_executor":
        await callback.answer("❌ Заказ уже закреплён", show_alert=True)
        return

    user = callback.from_user
    username = f"@{user.username}" if user.username else "нет username"

    ok, msg = take_order(
        order_id=order_id,
        executor_id=user.id,
        executor_username=username
    )

    if not ok:
        await callback.answer(msg, show_alert=True)
        return

    if ok:
        try:
            await callback.message.delete()
        except:
            pass

        text = order.get("description", "")
        service = order.get("category") or order.get("service") or "Не указано"

        lines = text.splitlines()

        clean_text = "\n".join(
            line for line in lines
            if "@" not in line
            and "telegram" not in line.lower()
            and "t.me" not in line.lower()
        )

        materials_text = order.get("materials_text", "не указано")

        await callback.bot.send_message(
            user.id,
            f"🔒 Заказ #{order_id} закреплён за вами.\n\n"
            f"📋 Детали заказа:\n"
            f"🛠 Услуга: {service}\n\n"
            f"📝 Заявка:\n{clean_text}\n\n"
            f"📁 Материалы / информация:\n{materials_text}\n\n"
            f"⏰ Старайтесь соблюдать сроки.\n"
            f"Если пропадёте или не отправите материал вовремя — рейтинг может быть снижен.\n\n"
            f"📤 Когда закончите работу:\n"
            f"/ready_{order_id}\n\n"
            f"📩 По вопросам: @asa_d28\n\n"
            f"🤝 Пусть Аллах облегчит вашу работу и даст вам пользу.\n"
            f"BarakAllahu feekum."
        )
        
    files = get_order_files(order_id)

    for file_type, file_id in files:
        if file_type == "photo":
            await callback.bot.send_photo(user.id, file_id)
        elif file_type == "video":
            await callback.bot.send_video(user.id, file_id)
        elif file_type == "document":
            await callback.bot.send_document(user.id, file_id)   
        elif file_type == "audio":
            await callback.bot.send_audio(user.id, file_id)
        elif file_type == "voice":
            await callback.bot.send_voice(user.id, file_id)

    await callback.message.answer(
        f"🔒 Заказ #{order_id} закреплён\n\n"
        f"👤 Исполнитель: {username}\n"
        f"📌 Статус: taken"
    )

    await callback.bot.send_message(
        ADMIN_ID,
        f"🔒 Заказ #{order_id} закреплён\n\n"
        f"👤 Исполнитель: {username}\n"
        f"🆔 ID: {user.id}\n"
        f"🛠 Услуга: {service}"
    )

    await callback.answer("✅ Заказ закреплён за вами", show_alert=True)

@router.callback_query(lambda c: c.data.startswith("accept_order"))
async def accept_order(callback: types.CallbackQuery):
    await callback.answer()

    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)

    if not order:
        await callback.answer("Заказ не найден")
        return

    price = str(order["price"]).replace("3.", "").strip()

    update_order_status(order_id, WAITING_PAYMENT)

    await callback.message.answer(
        f"✅ Работа принята.\n\n"
        f"💰 Сумма к оплате: {price} сом\n\n"
        "💳 Реквизиты для оплаты:\n"
        "📌 Demirbank / карта: 4215890130058859\n"
        "📞 Телефон: +996 (556) 200 428\n\n"
        "После оплаты нажмите кнопку ниже и отправьте чек.\n\n"
        "📩 Если возникла проблема с оплатой — оператор: @asa_d28",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Я оплатил",
                        callback_data=f"paid_order:{order_id}"
                    )
                ]
            ]
        )
    )
    
    price_text = str(order.get("price", "")) + "\n" + str(order.get("description", ""))
    numbers = re.findall(r"\d+", price_text)
    price = max([int(n) for n in numbers], default=0)

    commission = 15
    platform_profit = int(price * commission / 100)
    executor_payout = price - platform_profit

    executor_id = order["executor_id"]

    print("PAYMENT BLOCK START")
    print("EXECUTOR_ID:", executor_id)
    print("ORDER_ID:", order_id)
    print("PAYOUT:", executor_payout)

    await callback.bot.send_message(
        executor_id,
        "💳 Отправьте реквизиты для выплаты одним сообщением.\n\n"
        "Формат:\n"
        "1️⃣ Банк\n"
        "2️⃣ Номер телефона или номер карты\n"
        "3️⃣ Имя получателя\n\n"
        "Пример:\n"
        "MBANK\n"
        "+996 XXX XXX XXX\n"
        "Имя получателя\n\n"
        "⚠️ Отправляйте только текстом.\n"
        "После проверки оператор отправит выплату."
    )

    user_state[executor_id] = {
        "step": "waiting_executor_payment_info",
        "order_id": order_id
    }

    await callback.bot.send_message(
        ADMIN_ID,
        f"💰 Заказ #{order_id} принят клиентом.\nМожно фиксировать прибыль."
    )

    user_state[callback.from_user.id] = {}

@router.callback_query(lambda c: c.data.startswith("revision_order"))
async def revision_order(callback: types.CallbackQuery):
    await callback.answer()

    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)

    if not order:
        await callback.message.answer("Заказ не найден.")
        return

    user_state[callback.from_user.id] = {
        "role": "buyer_revision",
        "step": "waiting_revision_text",
        "order_id": order_id,
    }

    await callback.message.answer(
        "🔁 Опишите, что нужно исправить:\n\n"
        "Например:\n"
        "— что не понравилось\n"
        "— что изменить\n"
        "— какие правки нужны"
    )

@router.callback_query(lambda c: c.data.startswith("paid_order"))
async def paid_order(callback: types.CallbackQuery):
    print("PAID_ORDER CLICKED")

    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)

    if not order:
        await callback.answer("Заказ не найден")
        return

    user_state[callback.from_user.id] = {
        "step": "waiting_receipt",
        "order_id": order_id
    }
    await callback.message.answer(
        f"📎 Отправьте чек оплаты фото или документом.\n\n"
        "После проверки оператором вы получите финальный файл."
    )

@router.callback_query(lambda c: c.data.startswith("confirm_payment"))
async def confirm_payment(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)

    if not order:
        await callback.answer("Заказ не найден")
        return

    final_data = get_final_file(order_id)

    if not final_data:
        await callback.answer("Финальный файл не найден")
        return

    file_type = final_data["file_type"]
    file_id = final_data["file_id"]

    caption = f"✅ Оплата подтверждена.\n\n📦 Финальный файл заказа #{order_id}"

    if file_type == "photo":
        await callback.bot.send_photo(
            order["client_id"],
            photo=file_id,
            caption=caption
        )
    elif file_type == "video":
        await callback.bot.send_video(
            order["client_id"],
            video=file_id,
            caption=caption
        )
    elif file_type == "document":
        await callback.bot.send_document(
            order["client_id"],
            document=file_id,
            caption=caption
        )

    update_order_status(order_id, COMPLETED)

    user_state[order["client_id"]] = {
        "role": "buyer_review",
        "step": "waiting_review",
        "order_id": order_id,
        "executor_id": order["executor_id"],
        "executor_username": order["executor_username"]
    }

    await callback.bot.send_message(
        order["client_id"],
        "⭐ Оцените работу исполнителя.\n\n"
        "Отправьте отзыв по шаблону:\n\n"
        "1. Оценка от 1 до 5\n"
        "2. Что понравилось\n"
        "3. Что можно улучшить"
    )

    await callback.message.answer(
        f"✅ Оплата заказа #{order_id} подтверждена."
    )

    await callback.answer()   

@router.callback_query(F.data == "materials_done")
async def send_order_after_materials(callback: types.CallbackQuery):
    print("MATERIALS_DONE CLICKED")
    user_id = callback.from_user.id

    if user_id not in user_state:
        await callback.message.answer("Заявка не найдена. Заполните заявку заново.")
        await callback.answer()
        return

    data = user_state[user_id]

    order_id = data["order_id"]
    chat_id = data["chat_id"]
    thread_id = data["thread_id"]
    executor_text = data["executor_text"]
    admin_text = data["admin_text"]

    await callback.message.bot.send_message(ADMIN_ID, admin_text)

    await callback.message.bot.send_message(
        chat_id=chat_id,
        text=executor_text,
        message_thread_id=thread_id,
        reply_markup=get_order_interest_kb(order_id)
    )

    await callback.message.answer("✅ Заказ отправлен исполнителям.")
    del user_state[user_id]
    await callback.answer()
