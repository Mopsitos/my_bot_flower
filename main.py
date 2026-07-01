import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message

import config
import buttons
import keyboards
from custom_filters import button_filter
from buttons import baza_button

# Инициализируем нашего бота директора школы
bot = Client(
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    name="HotDog_Bot"
)
DB_NAME = 'dog.db'
user_states = {}


def init_and_fill_db():
    """Создает таблицу учеников с полем id (без AUTOINCREMENT) для кастомного заполнения дыр."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # ИСПРАВЛЕНО: Явно добавлено поле id как PRIMARY KEY без AUTOINCREMENT
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                class TEXT,
                zam TEXT
            )
        """)
        conn.commit()


def get_first_free_id(cursor) -> int:
    """Ищет минимальный свободный ID в таблице animals, заполняя дыры."""
    cursor.execute("SELECT id FROM animals ORDER BY id ASC")
    existing_ids = [row[0] for row in cursor.fetchall()]

    target_id = 1
    for current_id in existing_ids:
        if current_id == target_id:
            target_id += 1
        elif current_id > target_id:
            break

    return target_id


@bot.on_message(filters.command('start') | button_filter(buttons.back_button))
async def start_handler(client: Client, message: Message):
    init_and_fill_db()
    user_states.pop(message.chat.id, None)
    await message.reply(
        ' **Привет! Я ХотДог-бот! Я помогу тебе запомнить всё про твоего питомца!**\n\n'
        'Ты можешь написать сюда что надо для твоего питомца, а также я дам тебе полезные советы!',
        reply_markup=keyboards.main_keyboard
    )


def add_animal(name: str, animal_class: str, zam: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        free_id = get_first_free_id(cursor)
        cursor.execute(
            "INSERT INTO animals (id, name, class, zam) VALUES (?, ?, ?, ?)",
            (free_id, name, animal_class, zam)
        )
        conn.commit()


@bot.on_message(button_filter(buttons.delete_button))
async def find_by_id_start(client: Client, message: Message):
    user_states[message.chat.id] = {"state": "waiting_for_id"}
    await message.reply("Введите уникальный ID питомца:", reply_markup=keyboards.back_keyboard)


async def handle_find_by_id(client: Client, message: Message):
    student_id = message.text.strip()
    user_states.pop(message.chat.id, None)

    if not student_id.isdigit():
        await message.reply("❌ Ошибка ввода! ID ученика должен состоять только из цифр.",
                            reply_markup=keyboards.main_keyboard)
        return

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # ИСПРАВЛЕНО: Сначала проверяем наличие питомца и забираем данные
        cursor.execute("SELECT name, class, zam FROM animals WHERE id = ?", (int(student_id),))
        result = cursor.fetchone()

        # ИСПРАВЛЕНО: Только если запись найдена, производим удаление
        if result:
            cursor.execute("DELETE FROM animals WHERE id = ?", (int(student_id),))
            conn.commit()

    if result:
        name, animal_class, zam = result
        await message.reply(
            f"🆔 **Личная карточка питомца №{student_id} удалена**\n\n"
            f"🐾 Было имя: {name}\n"
            f"🗂 Класс: {animal_class}",
            reply_markup=keyboards.main_keyboard
        )
    else:
        await message.reply(f"❌ Питомец с ID {student_id} отсутствует в базе.", reply_markup=keyboards.main_keyboard)


@bot.on_message(button_filter(buttons.sozd_button))
async def animal_bot_handler(client: Client, message: Message):
    user_id = message.chat.id
    state = user_states.get(user_id)

    if not state:
        user_states[user_id] = {"state": "waiting_for_name"}
        await message.reply("Введите имя питомца:")
        return

    current_step = state.get("state")

    if current_step == "waiting_for_name":
        user_states[user_id]["name"] = message.text
        user_states[user_id]["state"] = "waiting_for_class"
        await message.reply("Отлично! Теперь введи класс животного (например: Собака, Птица, Рептилия):")
        return

    elif current_step == "waiting_for_class":
        user_states[user_id]["class"] = message.text
        user_states[user_id]["state"] = "waiting_for_zam"
        await message.reply("И последнее: введи заметку (описание) для этого животного:")
        return

    elif current_step == "waiting_for_zam":
        name = state["name"]
        animal_class = state["class"]
        zam = message.text

        add_animal(name, animal_class, zam)

        await message.reply(
            f"🎉 Карточка животного успешно создана!\n\n"
            f"🐾 Имя: {name}\n"
            f"🗂 Класс: {animal_class}\n"
            f"📝 Заметка: {zam}",
            reply_markup=keyboards.main_keyboard
        )
        user_states.pop(user_id, None)
        return


def get_all_animals():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # ИСПРАВЛЕНО: В SELECT добавлен id, чтобы соответствовать распаковке в цикле ниже
        cursor.execute("SELECT id, name, class, zam FROM animals ORDER BY id")
        return cursor.fetchall()


@bot.on_message(button_filter(baza_button))
async def show_all_handler(client: Client, message: Message):
    animals = get_all_animals()

    if not animals:
        await message.reply("📭 В базе пока нет ни одного питомца.", reply_markup=keyboards.main_keyboard)
        return

    lines = []
    for animal_id, name, animal_class, zam in animals:
        lines.append(
            f"🆔 {animal_id} | 🐾 {name} | 🗂 {animal_class} | 📝 {zam}"
        )

    text = "**📋 Вся база питомцев:**\n\n" + "\n".join(lines)

    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        await message.reply(text[i:i + chunk_size])

    await message.reply("Выберите дальнейшее действие:", reply_markup=keyboards.main_keyboard)


@bot.on_message(filters.text & ~filters.regex(r"^/"))
async def text_dispatcher(client: Client, message: Message):
    chat_id = message.chat.id

    if chat_id not in user_states:
        return

    state = user_states[chat_id]["state"]

    if state == "waiting_for_id":
        await handle_find_by_id(client, message)
    elif state in ["waiting_for_name", "waiting_for_class", "waiting_for_zam"]:
        await animal_bot_handler(client, message)


bot.run()
