from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from config_data.config_reader import DEFAULT_COMMANDS
from database.aiosqlite_db import delete_info, get_sql_db
from handlers.command_handlers.low_high_best_command import user_query
from keyboards.reply.history_keyboard import markup_db
from keyboards.reply.start_keyboard import markup_2, markup_3
from loader import dp
from states.hotels_information import Hotel_Info


bot_menu_items = [
    "🔝 Дешевых отелей 🏠",
    "🔝 Дорогих отелей 🏡",
    "🔝 Наилучшее предложение 🏘",
    "🔎 История поиска 📖",
    "🚨 Помощь 🚨",
]


@dp.message(F.text == "🚀 Старт 🚀")
async def bot_message(message: Message, state: FSMContext) -> None:
    """
    Функция для начала поиска вариантов размещения (отелей).
    :param message: введенное пользователем сообщение.
    """
    await message.answer(
        "Выберите для себя наилучшее предложение 👌", reply_markup=markup_2
    )
    await state.set_state(Hotel_Info.bot_work_menu)


@dp.message(Hotel_Info.bot_work_menu, F.text.in_(bot_menu_items))
async def bot_menu(message: Message, state: FSMContext) -> None:
    """
    Функция для выбора вариантов размещения (отеля), истории поиска и помощи при выборе.
    :param message: введенное пользователем сообщение.
    """
    if (
        message.text == "🔝 Дешевых отелей 🏠"
        or message.text == "🔝 Дорогих отелей 🏡"
        or message.text == "🔝 Наилучшее предложение 🏘"
    ):
        await user_query(message, state)

    elif message.text == "🔎 История поиска 📖":
        await message.answer(
            "Нажмите на кнопки для просмотра или очистки истории поиска  📜",
            reply_markup=markup_db,
        )
        await state.set_state(Hotel_Info.bot_work_db)

    elif message.text == "🚨 Помощь 🚨":
        await message.answer(
            "Список команда нашего телеграм бота: 🗒 ",
            reply_markup=ReplyKeyboardRemove(),
        )
        text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
        await message.answer("\n".join(text))


@dp.message(Hotel_Info.bot_work_db)
async def bot_db(message: Message, state: FSMContext) -> None:
    """
    Функция для работы с БД (просмотром и очисткой истории поиска вариантов размещения).
    :param message: введенное пользователем сообщение.
    """
    if message.text == "🕵🏻‍♂Показать историю поиска📜":
        history = await get_sql_db()
        if history:
            for part in history:
                url = "https://hotels.com/ho" + str(part[2])
                name = part[3]
                name_url = f'<a href="{url}">"{name}"</a> '

                history_info = (
                    f"Введенная команда: {part[0]} \n"
                    + f"Город поиска: {part[1]} \n"
                    + f"Название отеля: {name_url} \n"
                    + f"Дата и время поиска: {part[5]}"
                )

                await message.answer_photo(
                    photo=(f"{part[4]}"),
                    caption=history_info,
                    parse_mode="html",
                    reply_markup=markup_3,
                )
            await state.set_state(Hotel_Info.bot_work_back)

        else:
            await message.answer("История поиска пуста 💭", reply_markup=markup_3)
            await state.set_state(Hotel_Info.bot_work_back)

    elif message.text == "🧹Очистить историю поиска🗑":
        await delete_info()
        await message.answer("История поиска удалена 👌", reply_markup=markup_3)
        await state.set_state(Hotel_Info.bot_work_back)


@dp.message(Hotel_Info.bot_work_back)
async def bot_back(message: Message, state: FSMContext) -> None:
    """
    Функция выхода с истории поиска назад или в главное меню.
    :param message: введенное пользователем сообщение.
    """
    if message.text == "🔙 Назад 🔙":
        await message.answer(
            "Выберите просмотр истории или удаление 👌", reply_markup=markup_db
        )
        await state.set_state(Hotel_Info.bot_work_db)

    elif message.text == "🔙 В главное меню 🔙":
        await message.answer(
            "Выберите для себя наилучшее предложение 👌", reply_markup=markup_2
        )
        await state.set_state(Hotel_Info.bot_work_menu)
