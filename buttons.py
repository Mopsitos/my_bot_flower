from aiohttp.web_routedef import delete
from pyrogram.types import KeyboardButton
from pyrogram import emoji

# Объявляем кнопки как объекты Pyrogram
delete_button = KeyboardButton(f"{emoji.CROSS_MARK} Удалить питомца")
sozd_button = KeyboardButton(f"{emoji.DOG_FACE} Создать карточку питомца")
baza_button = KeyboardButton(f"{emoji.PEN} Вывести базу данных питомцев")

back_button = KeyboardButton(f"{emoji.BACK_ARROW} Назад")