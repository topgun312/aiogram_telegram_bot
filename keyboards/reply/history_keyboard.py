from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb_history = [
    [KeyboardButton(text="🕵🏻‍♂Показать историю поиска📜")],
    [KeyboardButton(text="🧹Очистить историю поиска🗑")],
]
markup_db = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb_history)
