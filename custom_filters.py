from pyrogram import filters
from pyrogram.types import Message


# Изменяем фильтр так, чтобы button мог быть как KeyboardButton, так и обычной строкой str
def button_filter(button):
    async def func(_, __, message: Message):
        # Если это строка, сравниваем напрямую. Если объект — берем .text
        expected_text = button if isinstance(button, str) else button.text
        return message.text == expected_text

    return filters.create(func, "ButtonFilter", button=button)