from handlers.db import create_order # type: ignore #
from aiogram import Router, types # type: ignore
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # type: ignore
from keyboards.main_kb import buyer_keyboard, seller_keyboard  # type: ignore
import itertools

NEW = "new"
WAITING_PAYMENT = "waiting_payment"
PAID = "paid"
PUBLISHED = "published"
IN_PROGRESS = "in_progress"
SUBMITTED = "submitted"
REVISION = "revision"
COMPLETED = "completed"
CANCELLED = "cancelled"




router = Router()
def get_user_display(user):
    if user.username:
        return f"@{user.username}"

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if full_name:
        return full_name

    return f"ID {user.id}"


user_state = {}
orders = {}
order_counter = itertools.count(1)

SERVICES = [
    "Монтаж видео",
    "Графический дизайн",
    "Создание сайтов",
    "Продвижение в соц. сетях",
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
    "Создание сайтов": {
        "chat_id": -1003988228980,
        "thread_id": 4,
    },
    "Продвижение в соц. сетях": {
        "chat_id": -1003988228980,
        "thread_id": 21,
    },
}


def get_take_order_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Взять заказ",
                    callback_data=f"take_order:{order_id}"
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
                    text="🔁 Доработка",
                    callback_data=f"revision_order:{order_id}"
                )
            ]
        ]
    )


@router.message(lambda message: message.text == "Покупатель")
async def choose_buyer(message: types.Message):
    user_state[message.from_user.id] = {"role": "buyer"}

    await message.answer(
        "Вы выбрали роль: Покупатель\n\nВыберите нужную услугу:",
        reply_markup=buyer_keyboard
    )


@router.message(lambda message: message.text == "Исполнитель")
async def choose_seller(message: types.Message):
    user_state[message.from_user.id] = {"role": "seller"}

    await message.answer(
        "Вы выбрали роль: Исполнитель\n\nВыберите свою специализацию:",
        reply_markup=seller_keyboard
    )


@router.message(lambda message: message.text in SERVICES)
async def choose_service(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    role = state.get("role")
    service = message.text

    user_state[message.from_user.id]["service"] = service

    if role == "buyer":
        user_state[message.from_user.id]["step"] = "buyer_form"

        await message.answer(
            f"Услуга: {service}\n\n"
            "Введите заявку по шаблону:\n\n"
            "1. Что нужно:\n"
            "2. Срок:\n"
            "3. Бюджет:\n"
            "4. Telegram для связи:"
        )

    elif role == "seller":
        user_state[message.from_user.id]["step"] = "seller_form"

        await message.answer(
            f"Специализация: {service}\n\n"
            "Отправьте анкету по шаблону:\n\n"
            "1. Имя\n"
            "2. Опыт\n"
            "3. Какие услуги оказываете\n"
            "4. Портфолио / примеры работ\n"
            "5. Telegram для связи"
        )
@router.message(lambda message: user_state.get(message.from_user.id, {}).get("step") == "buyer_form")
async def handle_buyer_form(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    service = state.get("service")

    order_id = await create_order(
        user_id=message.from_user.id,
        username=get_user_display(message.from_user),
        service=service,
        text=message.text
    )

    await message.answer(
        f"Заказ #{order_id} создан\n"
        f"Статус: {WAITING_PAYMENT}"
    )

    del user_state[message.from_user.id]
@router.message(
    lambda message: user_state.get(message.from_user.id, {}).get("step") == "seller_form"
)

async def process_forms(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    role = state.get("role")
    step = state.get("step")
    service = state.get("service")
    text = message.text or ""

    username = message.from_user.username
    user = f"@{username}" if username else "нет username"

    # --------------------
    # Ветка покупателя
    # --------------------
    if role == "buyer" and step == "buyer_form":
        chat_data = SELLER_CHATS.get(service)

        if not chat_data:
            await message.answer("Ошибка: чат для этой категории не найден.")
            return

        chat_id = chat_data["chat_id"]
        thread_id = chat_data["thread_id"]

        order_id = next(order_counter)

        orders[order_id] = {
            "client_id": message.from_user.id,
            "client_username": username,
            "service": service,
            "text": text,
            "status": "published",
            "executor_id": None,
            "executor_username": None,
            "group_chat_id": chat_id,
            "group_message_id": None,
            "result_file_id": None,
            "result_file_type": None,
            "result_text": None,
        }

        await message.answer(
            f"Заявка принята ✅\nНомер заказа: #{order_id}"
        )

        admin_text = (
            f"📦 Новый заказ #{order_id}\n\n"
            f"🛠 Услуга: {service}\n"
            f"👤 Клиент: {user}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"📝 Текст заявки:\n{text}\n\n"
            f"📤 Отправлено в чат: {chat_id}\n"
            f"📌 Статус: published"
        )

        lines = text.splitlines()

        task_line = lines[0] if len(lines) > 0 else "Не указано"
        deadline_line = lines[1] if len(lines) > 1 else "Не указано"
        budget_line = lines[2] if len(lines) > 2 else "Не указано"

        group_text = (
            f"📦 Заказ #{order_id}\n\n"
            f"🛠 Услуга: {service}\n\n"
            f"📝 Что нужно:\n{task_line}\n\n"
            f"⏰ Срок:\n{deadline_line}\n\n"
            f"💰 Бюджет:\n{budget_line}\n\n"
            f"Нажми кнопку ниже, чтобы взять заказ."
       )

        await message.bot.send_message(ADMIN_ID, admin_text)

        sent_msg = await message.bot.send_message(
            chat_id=chat_id,
            text=group_text,
            message_thread_id=thread_id,
            reply_markup=get_take_order_kb(order_id)
        )

        orders[order_id]["group_message_id"] = sent_msg.message_id

        del user_state[message.from_user.id]
        return

    # --------------------
    # Ветка исполнителя
    # --------------------
    if role == "seller" and step == "seller_form":
        chat_data = SELLER_CHATS.get(service)

        if not chat_data:
            await message.answer("Ошибка: чат для этой категории не найден.")
            return

        chat_id = chat_data["chat_id"]
        thread_id = chat_data["thread_id"]

        await message.answer("Анкета отправлена ✅")

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
            text=(
                f"🧑‍💻 Новый исполнитель\n\n"
                f"🛠 Специализация: {service}\n"
                f"👤 Контакт: {user}\n"
                f"🆔 ID: {message.from_user.id}\n\n"
                f"📄 Анкета:\n{text}"
            ),
            message_thread_id=thread_id
        )

        del user_state[message.from_user.id]
        return


@router.callback_query(lambda c: c.data.startswith("take_order:"))
async def take_order_callback(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[1])

    order = orders.get(order_id)
    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    if order["status"] != "published":
        await callback.answer("Этот заказ уже взят", show_alert=True)
        return

    user = callback.from_user
    print("USERNAME:", user.username)
    print("FIRST_NAME:", user.first_name)
    print("LAST_NAME:", user.last_name)


    username = user.username
    executor_name = get_user_display(user)

    order["status"] = "taken"
    order["executor_id"] = callback.from_user.id
    order["executor_username"] = username

    lines = order["text"].split("\n")
    safe_lines = []
    for line in lines:
        clean_line = line.strip()
        
        if "." in clean_line[:3]:
            clean_line = clean_line.split(".", 1)[1].strip()

        safe_lines.append(clean_line)

    task = safe_lines[0] if len(safe_lines) > 0 else "-"
    deadline = safe_lines[1] if len(safe_lines) > 1 else "-"
    budget = safe_lines[2] if len(safe_lines) > 2 else "-"

    safe_text = (
        f"📌 Что нужно:\n{task}\n\n"
        f"⏰ Срок:\n{deadline}\n\n"
        f"💰 Бюджет:\n{budget}\n\n"
    )

    new_text = (
        f"📦 Заказ #{order_id}\n\n"
        f"🛠 Услуга: {order['service']}\n\n"
        f"📝 Задача:\n{safe_text}\n\n"
        f"✅ Заказ взят"
    )        


    await callback.message.edit_text(new_text)
    await callback.answer("Ты взял заказ ✅")

    await callback.bot.send_message(
        ADMIN_ID,
        f"✅ Заказ #{order_id} взял исполнитель\n\n"
        f"👤 Исполнитель: {executor_name}\n"
        f"🆔 ID: {callback.from_user.id}\n"
        f"🛠 Услуга: {order['service']}\n"
        f"📌 Статус: taken"
    )

    await callback.bot.send_message(
        order["client_id"],
        f"✅ Ваш заказ #{order_id} взят в работу.\n\n"
        f"🛠 Услуга: {order['service']}\n"
        f"Ожидайте результат."
    )

   # --------------------
   # Принятие результата клиентом
   # --------------------
  
@router.callback_query(lambda c: c.data.startswith("accept_order"))
async def accept_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = orders.get(order_id)

    if not order:
        await callback.answer("Заказ не найден")
        return

    order["status"] = "finished"

    # уведомляем клиента
    await callback.message.edit_text(
        f"✅ Заказ #{order_id} завершен.\nСпасибо!"
    )

    # уведомляем тебя (админа)
    await callback.bot.send_message(
        ADMIN_ID,
        f"💰 Заказ #{order_id} принят клиентом.\nМожно фиксировать прибыль."
    )

    await callback.answer("Вы приняли заказ")
    await callback.bot.send_message(
    callback.from_user.id,
    f"📦 Ты взял заказ #{order_id}\n\n"
    f"Когда закончишь работу, напиши:\n"
    f"/ready_{order_id}\n\n"
    f"После этого бот попросит у тебя готовый материал."
)

    # --------------------
    # Доработка заказа клиентом
    # --------------------


@router.callback_query(lambda c: c.data.startswith("revision_order"))
async def revision_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    order = orders.get(order_id)

    if not order:
        await callback.answer("Заказ не найден")
        return

    order["status"] = "revision"

    # уведомляем исполнителя
    executor_id = order.get("executor_id")

    if executor_id:
        await callback.bot.send_message(
            executor_id,
            f"🔁 Заказ #{order_id} отправлен на доработку.\nИсправь и отправь заново."
        )

    await callback.answer("Отправлено на доработку")    

    # --------------------
    # обработчик сообщений от исполнителя
    # --------------------

@router.message()
async def handle_result(message: types.Message):
    user_id = message.from_user.id

    # ищем заказ, который он выполняет
    for order_id, order in orders.items():
        if order.get("executor_id") == user_id and order["status"] == "taken":

            # сохраняем результат
            if message.video:
                order["result_file_id"] = message.video.file_id
                order["result_file_type"] = "video"

            elif message.document:
                order["result_file_id"] = message.document.file_id
                order["result_file_type"] = "document"

            elif message.photo:
                order["result_file_id"] = message.photo[-1].file_id
                order["result_file_type"] = "photo"

            else:
                order["result_text"] = message.text

            order["status"] = "done"

            client_id = order["client_id"]

            # отправляем клиенту
            if order["result_file_id"]:
                await message.bot.send_document(
                    client_id,
                    order["result_file_id"],
                    caption="📦 Ваш заказ готов",
                    reply_markup=get_client_result_kb(order_id)
                )
            else:
                await message.bot.send_message(
                    client_id,
                    f"📦 Ваш заказ готов:\n\n{order['result_text']}",
                    reply_markup=get_client_result_kb(order_id)
                )

            await message.answer("✅ Отправлено клиенту")
            return
    
    # -----------------
    # ready_номер - команда для исполнителя, чтобы отправить результат без файла
    # -----------------

@router.message(lambda message: message.text and message.text.startswith("/ready_"))
async def start_ready_order(message: types.Message):
    try:
        order_id = int(message.text.replace("/ready_", ""))
    except ValueError:
        await message.answer("Неверный формат. Пример: /ready_1")
        return

    order = orders.get(order_id)
    if not order:
        await message.answer(f"Заказ #{order_id} не найден.")
        return

    if order["status"] not in ["taken", "waiting_upload"]:
        await message.answer("Этот заказ нельзя завершить сейчас.")
        return

    if order["executor_id"] != message.from_user.id:
        await message.answer("Ты не исполнитель этого заказа.")
        return

    user_state[message.from_user.id] = {
        "role": "executor_upload",
        "step": "waiting_upload",
        "order_id": order_id,
    }

    order["status"] = "waiting_upload"

    await message.answer(
        f"Пришли готовый материал по заказу #{order_id}.\n\n"
        f"Можно отправить:\n"
        f"- документ\n"
        f"- фото\n"
        f"- видео\n"
        f"- текст"
    )
# ------------------
# загрузка материала
# ------------------
@router.message(
    lambda message: user_state.get(message.from_user.id, {}).get("step") == "waiting_upload"
    and not (message.text and message.text.startswith("/ready_"))
)
async def upload_ready_material(message: types.Message):
    state = user_state.get(message.from_user.id)

    if not state:
        return

    order_id = state.get("order_id")
    order = orders.get(order_id)

    if order["status"] != "waiting_upload":
        await message.answer("Сейчас нельзя отправить материал.")
        return

    if not order:
        await message.answer("Заказ не найден.")
        del user_state[message.from_user.id]
        return

    if order["executor_id"] != message.from_user.id:
        await message.answer("Ты не исполнитель этого заказа.")
        del user_state[message.from_user.id]
        return

    sent_ok = False

    # текст
    if message.text and not message.text.startswith("/ready_"):
        order["result_text"] = message.text
        order["result_file_id"] = None
        order["result_file_type"] = "text"

        await message.bot.send_message(
            order["client_id"],
            f"📦 Готовый материал по заказу #{order_id}\n\n{message.text}",
            reply_markup=get_client_result_kb(order_id)
        )
        sent_ok = True

    # документ
    elif message.document:
        order["result_file_id"] = message.document.file_id
        order["result_file_type"] = "document"
        order["result_text"] = message.caption or ""

        await message.bot.send_document(
            order["client_id"],
            document=message.document.file_id,
            caption=f"📦 Готовый материал по заказу #{order_id}\n\n{message.caption or ''}",
            reply_markup=get_client_result_kb(order_id)
        )
        sent_ok = True

    # фото
    elif message.photo:
        file_id = message.photo[-1].file_id
        order["result_file_id"] = file_id
        order["result_file_type"] = "photo"
        order["result_text"] = message.caption or ""

        await message.bot.send_photo(
            order["client_id"],
            photo=file_id,
            caption=f"📦 Готовый материал по заказу #{order_id}\n\n{message.caption or ''}",
            reply_markup=get_client_result_kb(order_id)
        )
        sent_ok = True

    # видео
    elif message.video:
        order["result_file_id"] = message.video.file_id
        order["result_file_type"] = "video"
        order["result_text"] = message.caption or ""

        await message.bot.send_video(
            order["client_id"],
            video=message.video.file_id,
            caption=f"📦 Готовый материал по заказу #{order_id}\n\n{message.caption or ''}",
            reply_markup=get_client_result_kb(order_id)
        )
        sent_ok = True

    if not sent_ok:
        await message.answer("Поддерживается только текст, документ, фото или видео.")
        return

    order["status"] = "submitted"

    await message.answer(f"Материал по заказу #{order_id} отправлен клиенту ✅")

    await message.bot.send_message(
        ADMIN_ID,
        f"📨 Исполнитель отправил материал\n\n"
        f"📦 Заказ #{order_id}\n"
        f"👤 Исполнитель ID: {message.from_user.id}\n"
        f"📌 Статус: submitted"
    )

    del user_state[message.from_user.id] 
