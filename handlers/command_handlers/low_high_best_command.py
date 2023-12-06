from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from keyboards.inline.end_result import count_hotels
from keyboards.inline.location import city_markup
from loader import dp
from states.hotels_information import Hotel_Info


@dp.message(Command(commands=["lowprice", "highprice", "bestdeal"]))
async def user_query(message: types.Message, state: FSMContext) -> None:
    """
    Функция для получения и записи введенной команды в класс состояний пользователя.
    :param message: введенная пользователем команда
    """
    await state.set_state(Hotel_Info.city)
    await state.update_data(user_command=message.text)
    await message.answer(
        f"{message.from_user.first_name}, в каком городе ищем отель? 🗺",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Hotel_Info.city)
async def get_city(message: types.Message, state: FSMContext) -> None:
    """
    Функция для ввода города поиска вариантов размещения (отеля) и сохранение в класс состояний пользователя.
    :param message: введенный пользователем город поиска вариантов размещения (отеля)
    """
    await state.update_data(city=message.text)
    city_keyboard = await city_markup(message.text)
    if city_keyboard:
        await message.answer(
            "Уточните пожалуйста локацию 📌", reply_markup=city_keyboard
        )
    else:
        await message.answer("Город должен содержать только буквы!")


@dp.message(Hotel_Info.price_min)
async def get_min_price(message: types.Message, state: FSMContext) -> None:
    """
    Функция получения минимальной цены за сутки от пользователя и сохранения в класс состояний пользователя.
    :param message: минимальная сумма за сутки, введенная пользователем.
    """
    data = await state.get_data()
    if data["user_command"] in ["/lowprice", "🔝 Дешевых отелей 🏠"]:
        if message.text.isdigit():
            await message.answer("Введите количество взрослых посетителей 👨🏻‍🦰")
            await state.set_state(Hotel_Info.adults)
            await state.update_data(price_min=message.text)
        else:
            await message.answer("Цена должна быть числом!")
    elif data["user_command"] in ["/bestdeal", "🔝 Наилучшее предложение 🏘"]:
        if message.text.isdigit():
            await message.answer("Введите максимальную цену за сутки ($) 💰")
            await state.set_state(Hotel_Info.price_max)
            await state.update_data(price_min=message.text)
        else:
            await message.answer("Цена должна быть числом!")


@dp.message(Hotel_Info.price_max)
async def get_max_price(message: types.Message, state: FSMContext) -> None:
    """
    Функция получения максимальной цены за сутки от пользователя и сохранения в класс состояний пользователя.
    :param message: максимальная сумма за сутки, введенная пользователем.
    """

    if message.text.isdigit():
        await message.answer("Введите количество взрослых посетителей 👨🏻‍🦰")
        await state.set_state(Hotel_Info.adults)
        await state.update_data(price_max=message.text)
    else:
        await message.answer("Цена должна быть числом!")


@dp.message(Hotel_Info.adults)
async def get_adults(message: types.Message, state: FSMContext) -> None:
    """
    Функция получения количества и возраста детей от пользователя и сохранения в класс состояний пользователя.
    :param message: количество и возраст детей, введенные пользователем.
    """
    if message.text.isdigit():
        await message.answer(
            'Если с Вами дети, введите возраст каждого (до 18 лет) через запятую (Например (3-е детей): 3, 5, 6), иначе напишите "нет'
            " 👩🏻‍🦲"
        )
        await state.set_state(Hotel_Info.childrens)
        await state.update_data(adults=message.text)
    else:
        await message.answer("Цена должна быть числом!")


@dp.message(Hotel_Info.childrens)
async def get_childrens(message: types.Message, state: FSMContext) -> None:
    """
    Функция получения количества и возраста детей пользователя.
    :param message: список количества детей и их возраст, введенный пользователем.
    """
    global s
    age_list = []
    for s in message.text.split(","):
        age_list.append(s)
    if age_list[0] == "нет":
        await state.update_data(childrens=0)
        await state.set_state(Hotel_Info.hotels_count)
        await message.answer(
            "Максимальное количество отелей для просмотра 🎲",
            reply_markup=await count_hotels(),
        )
    elif [s for s in age_list if s.isdigit()] and int(s) < 18:
        await state.update_data(childrens=age_list)
        await state.set_state(Hotel_Info.hotels_count)
        await message.answer(
            "Максимальное количество отелей для просмотра 🎲",
            reply_markup=await count_hotels(),
        )
    else:
        await message.answer("Введите один из предложенных ответов!")
