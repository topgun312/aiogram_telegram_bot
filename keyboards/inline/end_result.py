from contextlib import suppress
from datetime import datetime
from typing import Optional
from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from botrequest import rapidapi
from database.aiosqlite_db import sql_add_command
from keyboards.reply.start_keyboard import markup_1
from loader import dp
from states.hotels_information import Hotel_Info


async def count_hotels() -> InlineKeyboardMarkup:
    """
    Функция выбора количества вариантов размещения (отелей) для просмотра.
    :return: клавиатура для выбора количества отелей
    """
    count_hotels_inline = [
        [InlineKeyboardButton(text="3 🏠", callback_data="hotels_count:3")],
        [InlineKeyboardButton(text="6 🏠", callback_data="hotels_count:6")],
        [InlineKeyboardButton(text="9 🏠", callback_data="hotels_count:9")],
        [InlineKeyboardButton(text="12 🏠", callback_data="hotels_count:12")],
        [InlineKeyboardButton(text="15 🏠", callback_data="hotels_count:15")],
        [InlineKeyboardButton(text="Все 🏘", callback_data="hotels_count:25")],
    ]
    markup_inline = InlineKeyboardMarkup(
        row_width=2, inline_keyboard=count_hotels_inline
    )
    return markup_inline


@dp.callback_query(Hotel_Info.hotels_count, F.data.startswith("hotels_count"))
async def answer(call: CallbackQuery, state: FSMContext) -> int:
    """
    Функция для вывода полной информации о результатах поиска вариантов размещения (отеля).
    :param state: аргумент типа FSMContext, содержащий информацию о пользователе, его состоянии и данных, полученных от пользователя внутри состояний
    :param call: выбор пользователем количества отелей для поиска
    :return: вывод количества отелей для просмотра.
    """
    global hotels_info, hotel
    if call.message:
        await state.update_data(hotels_count=call.data.split(":")[1])
        hotels = call.data.split(":")[1]
        data = await state.get_data()
        date_1 = datetime.strptime(str(data["check_in"]), "%Y-%m-%d")
        date_2 = datetime.strptime(str(data["check_out"]), "%Y-%m-%d")
        days = date_2 - date_1
        period = str(days).split()[0]

        if data["user_command"] in [
            "/lowprice",
            "🔝 Дешевых отелей 🏠",
            "/highprice",
            "🔝 Дорогих отелей 🏡",
        ]:
            text_low_high = (
                f'<b>Параметры запроса.</b> \nГород поиска 🗺: {data["city_loc"]} \n'
                + f"Количество отелей 🎲: {hotels} \n"
                + f'Въезд ➡: {data["check_in"]} \n'
                + f'Выезд ⬅: {data["check_out"]} \n'
                + f"Веду поиск...🕵🏻‍♂"
            )
            await call.message.answer(
                text_low_high, reply_markup=markup_1, parse_mode="html"
            )
            await call.message.delete()
            hotels_info = await rapidapi.search_hotels(data)

        elif data["user_command"] in ["/bestdeal", "🔝 Наилучшее предложение 🏘"]:
            text_bst = (
                f'<b>Параметры запроса.</b> \nГород поиска 🗺: {data["city_loc"]} \n'
                + f'Количество отелей 🎲: {data["hotels_count"]} \n'
                + f'Въезд ➡: {data["check_in"]} \n'
                + f'Выезд ⬅: {data["check_out"]} \n'
                + f'Минимальная цена ⬇: {data["price_min"]} \n'
                + f'Максимальная цена ⬆: {data["price_max"]} \n'
                + f"Веду поиск...🕵🏻‍♂"
            )
            await call.message.answer(
                text_bst, reply_markup=markup_1, parse_mode="html"
            )
            await call.message.delete()
            hotels_info = await rapidapi.search_hotels(data)

        for hotel in hotels_info.values():
            info = (
                f' \nНаименование отеля 🏨: {hotel["name"]} \n'
                + f'Местоположение отеля 📪: {hotel["loc"]} \n'
                + f'Рейтинг отеля 🏆: {hotel["reviews"]} \n'
                + f'Расстояние от центра города 🚕: {round(hotel["landmarks"] * 1.61, 1)} км \n'
                + f'Цена за сутки 💳: {hotel["price"]} $\n'
                + f'Цена за период проживания 💰: {int(hotel["price"]) * int(period)} $'
            )
            await call.message.answer_photo(
                photo=(f'{hotel["fonfoto"]}'),
                caption=info,
                reply_markup=await hotel_inline(hotel),
            )
            date_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            message_db = [
                data["user_command"],
                data["city_loc"],
                hotel["id"],
                hotel["name"],
                hotel["fonfoto"],
                date_time,
            ]
            await sql_add_command(message_db)
        return hotel


async def hotel_inline(hotel: int) -> InlineKeyboardMarkup:
    """
    Функция для создания инлайн - клавиатуры с локациией, ссылкой на отель, фотографиями отеля.
    :param hotel: количество отелей выбранных пользователем.
    :return: вывод инлайн - клавиатуры
    """
    kb_hotel_inline = [
        [
            InlineKeyboardButton(
                text="🌍  На Google Maps 📌",
                url=f'http://maps.google.com/maps?z=12&t=m&q=loc:{hotel["coordinate"]}',
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 На страницу 📲",
                url=f'https://www.hotels.com/h{hotel["id"]}.Hotel-information/',
            )
        ],
        [
            InlineKeyboardButton(
                text="📸 Фотографии 🏙", callback_data=f'id:{hotel["id"]}'
            )
        ],
    ]
    markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=kb_hotel_inline)
    return markup


@dp.callback_query(F.data.startswith("id"))
async def send_photo(call: CallbackQuery, state: FSMContext) -> Optional[list]:
    """
    Функция запроса поиска фото вариантов размещения (отеля) для создания пагинатора.
    :param state: аргумент типа FSMContext, содержащий информацию о пользователе, его состоянии и данных, полученных от пользователя внутри состояний
    :param call: выбор пользователя при нажатии на клавиатуру.
    :return: список url-адресов фото варианта размещения (отеля).
    """
    if call.message:
        id_hotel = call.data.split(":")[1]
        images = await rapidapi.search_photo_hotel(id_hotel)
        await state.set_state(Hotel_Info.images)
        await state.update_data(images=images)
        data = await state.get_data()
        photos = data["images"]
        await call.message.answer_photo(
            photos[0], reply_markup=paginator(), parse_mode="Markdown"
        )
        return images


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


def paginator(page: int = 0) -> InlineKeyboardMarkup:
    """
    Функция создания инлайн-клавиатуры пагинатора
    :param page: текущая страница отображаемая в пагинаторе
    :return: вывод инлайн - клавиатуры
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⬅️", callback_data=Pagination(action="prev", page=page).pack()
        ),
        InlineKeyboardButton(
            text="➡️", callback_data=Pagination(action="next", page=page).pack()
        ),
        width=2,
    )
    builder.add(InlineKeyboardButton(text="Закрыть ❌ ", callback_data="back"))
    return builder.as_markup()


@dp.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(
    call: CallbackQuery, callback_data: Pagination, state: FSMContext
) -> None:
    """
    Функция обработки нажатия на инлайн-клавиатуру при переключении пагинатора
    :param call: выбор пользователя при нажатии на клавиатуру.
    :param callback_data: экземпляр класса Pagination, содержащий данные о номере страницы и действии пагинатора
    :param state: аргумент типа FSMContext, содержащий информацию о пользователе, его состоянии и данных, полученных от пользователя внутри состояний
    """
    data = await state.get_data()
    photos = data["images"]
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 0 else 0

    if callback_data.action == "next":
        page = page_num + 1 if page_num < (len(photos) - 1) else page_num
    with suppress(TelegramBadRequest):
        await call.message.edit_media(
            media=InputMediaPhoto(media=photos[page], caption=None),
            reply_markup=paginator(page),
        )


@dp.callback_query(F.data.startswith("back"))
async def close_paginator(call: CallbackQuery) -> None:
    """
    Функция закрытия просмотра фотографий с пагинатора.
    :param call: выбор пользователя при нажатии на клавиатуру.
    """
    await call.message.delete()
