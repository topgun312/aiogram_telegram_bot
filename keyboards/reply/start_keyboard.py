from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb_start = [[KeyboardButton(text="🚀 Старт 🚀")]]
markup_1 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb_start)


kb_menu = [
    [KeyboardButton(text="🔝 Дешевых отелей 🏠")],
    [KeyboardButton(text="🔝 Дорогих отелей 🏡")],
    [KeyboardButton(text="🔝 Наилучшее предложение 🏘")],
    [KeyboardButton(text="🔎 История поиска 📖")],
    [KeyboardButton(text="🚨 Помощь 🚨")],
]
markup_2 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb_menu)


kb_back = [
    [KeyboardButton(text="🔙 Назад 🔙")],
    [KeyboardButton(text="🔙 В главное меню 🔙")],
]
markup_3 = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb_back)
