from pyrogram.types import ReplyKeyboardMarkup
import buttons

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [buttons.baza_button],
        [buttons.delete_button,buttons.sozd_button]
    ],
    resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[[buttons.back_button]],
    resize_keyboard=True
)