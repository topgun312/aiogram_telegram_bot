from datetime import datetime, timedelta
from typing import Union
from aiogram import F
from aiogram3_calendar import simple_cal_callback
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from botrequest.rapidapi import search_location
from keyboards.inline.calendar.calendar import SimpleCalendar
from keyboards.inline.calendar.calendar_types import SimpleCalendarCallback
from loader import dp
from states.hotels_information import Hotel_Info


async def city_markup(message: str) -> InlineKeyboardMarkup:
    """
    Функция для поиска локации вариантов размещения(отелей) и создания инлайн-клавиатуры с результатами поиска.
    :param message: введеное пользователем название города.
    :return: инлайн - клавиатура с локацией.
    """
    cities = await search_location(message)
    if cities:
        buttons = []
        for city in cities:
            button = [
                InlineKeyboardButton(
                    text=city["city_name"],
                    callback_data=f'destination:{city["destination_id"]}',
                )
            ]
            buttons.append(button)
        destinations = InlineKeyboardMarkup(inline_keyboard=buttons)
        return destinations


@dp.callback_query(F.data.startswith("destination"))
async def nav_cal_handler(call: CallbackQuery, state: FSMContext) -> None:
    """
    Функция для обработки нажатия инлайн-клавиатуры при  локации и вызова работы календаря
    :param call: выбор пользователя при нажатии на клавиатуру.
    :param state: аргумент типа FSMContext, содержащий информацию о пользователе, его состоянии и данных, полученных от пользователя внутри состояний
    """
    if call.message:
        await state.update_data(location=call.data.split(":")[1])
        for keyboard in call.message.reply_markup.inline_keyboard:
            for i in keyboard:
                if i.callback_data == call.data:
                    await state.update_data(city_loc=i.text)
        await state.set_state(Hotel_Info.check_in)
        await call.message.answer(
            "Введите дату заезда: ",
            reply_markup=await SimpleCalendar().start_calendar(),
        )
        await call.message.delete()


@dp.callback_query(simple_cal_callback.filter(), Hotel_Info.check_in)
async def process_simple_calendar_in(
    call: CallbackQuery,
    callback_data: Union[CallbackData, SimpleCalendarCallback],
    state: FSMContext,
) -> None:
    """
    Функция обработки выбора даты заезда в календаре при нажатии на инлайн-клавиатуру
    :param call: выбор пользователя при нажатии на клавиатуру.
    :param callback_data:  словарь, заданный calendar_callback
    :param state: аргумент типа FSMContext, содержащий информацию о пользователе, его состоянии и данных, полученных от пользователя внутри состояний
    """
    selected, date = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        if date < datetime.utcnow() - timedelta(days=1):
            await call.message.answer(
                "Введите корректную дату",
                reply_markup=await SimpleCalendar().start_calendar(),
            )
            await call.message.delete()
        else:
            await state.update_data(check_in=date.strftime("%Y-%m-%d"))
            await state.set_state(Hotel_Info.check_out)
            await call.message.answer(
                f"Введите дату выезда:",
                reply_markup=await SimpleCalendar().start_calendar(),
            )
            await call.message.delete()


@dp.callback_query(simple_cal_callback.filter(), Hotel_Info.check_out)
async def process_simple_calendar_out(
    call: CallbackQuery,
    callback_data: Union[CallbackData, SimpleCalendarCallback],
    state: FSMContext,
) -> None:
    """
    Функция обработки выбора даты выезда в календаре при нажатии на инлайн-клавиатуру
    :param call: выбор пользователя при нажатии на клавиатуру.
    :param callback_data:  словарь, заданный calendar_callback
    :param state: аргумент типа FSMContext, содержащий информацию о пользователе, его состоянии и данных, полученных от пользователя внутри состояний
    """
    selected, date = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        check_in = await state.get_data()
        check_in_date = datetime.strptime(check_in["check_in"], "%Y-%m-%d")
        if date < check_in_date + timedelta(days=1):
            await call.message.answer(
                "Введите корректную дату",
                reply_markup=await SimpleCalendar().start_calendar(),
            )
            await call.message.delete()
        else:
            await state.update_data(check_out=date.strftime("%Y-%m-%d"))
            await call.message.delete()
            data = await state.get_data()

            if data["user_command"] in [
                "/lowprice",
                "🔝 Дешевых отелей 🏠",
                "/bestdeal",
                "🔝 Наилучшее предложение 🏘",
            ]:
                await call.message.answer("Введите минимальную цену за сутки ($) 💰")
                await state.set_state(Hotel_Info.price_min)

            if data["user_command"] in ["/highprice", "🔝 Дорогих отелей 🏡"]:
                await call.message.answer("Введите максимальную цену за сутки ($) 💰")
                await state.set_state(Hotel_Info.price_max)
