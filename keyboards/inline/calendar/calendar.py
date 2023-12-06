import calendar
from datetime import datetime, timedelta
from typing import Union
from aiogram3_calendar.calendar_types import (
    WEEKDAYS,
    SimpleCalendarAction,
    SimpleCalendarCallback,
)
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


class SimpleCalendar:
    @staticmethod
    async def start_calendar(
        year: int = datetime.now().year, month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        """
        Создает встроенную клавиатуру с указанными годом и месяцем
        :param int year: Год для использования в календаре, если не используется текущий год
        :param int month:  Месяц для использования в календаре, если не используется текущий месяц
        :return: Возвращает объект InlineKeyboardMarkup с календарем.
        """
        day = None
        markup = []
        ignore_callback = SimpleCalendarCallback(
            act=SimpleCalendarAction.IGNORE, year=year, month=month, day=0
        )

        markup.append(
            [
                InlineKeyboardButton(
                    text="<<",
                    callback_data=SimpleCalendarCallback(
                        act=SimpleCalendarAction.PREV_YEAR,
                        year=year,
                        month=month,
                        day=1,
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=f"{calendar.month_name[month]} {str(year)}",
                    callback_data=ignore_callback.pack(),
                ),
                InlineKeyboardButton(
                    text=">>",
                    callback_data=SimpleCalendarCallback(
                        act=SimpleCalendarAction.NEXT_YEAR,
                        year=year,
                        month=month,
                        day=1,
                    ).pack(),
                ),
            ]
        )

        markup.append(
            [
                InlineKeyboardButton(text=day, callback_data=ignore_callback.pack())
                for day in WEEKDAYS
            ]
        )

        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            calendar_row = []
            for day in week:
                if day == 0:
                    calendar_row.append(
                        InlineKeyboardButton(
                            text=" ", callback_data=ignore_callback.pack()
                        )
                    )
                    continue
                calendar_row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=SimpleCalendarCallback(
                            act=SimpleCalendarAction.DAY,
                            year=year,
                            month=month,
                            day=day,
                        ).pack(),
                    )
                )
            markup.append(calendar_row)

        markup.append(
            [
                InlineKeyboardButton(
                    text="<",
                    callback_data=SimpleCalendarCallback(
                        act=SimpleCalendarAction.PREV_MONTH,
                        year=year,
                        month=month,
                        day=day,
                    ).pack(),
                ),
                InlineKeyboardButton(text=" ", callback_data=ignore_callback.pack()),
                InlineKeyboardButton(
                    text=">",
                    callback_data=SimpleCalendarCallback(
                        act=SimpleCalendarAction.NEXT_MONTH,
                        year=year,
                        month=month,
                        day=day,
                    ).pack(),
                ),
            ]
        )

        inline_kb = InlineKeyboardMarkup(inline_keyboard=markup, row_width=7)
        return inline_kb

    async def process_selection(
        self, query: CallbackQuery, data: Union[CallbackData, SimpleCalendarCallback]
    ) -> tuple:
        """
        Обработчик callback_query. Этот метод генерирует новый календарь при нажатии кнопки вперед или
        назад. Этот метод должен вызываться внутри CallbackQueryHandler.
        :param query: callback_query, предоставляемый обработчиком CallbackQueryHandler
        :param data: callback_data, словарь, заданный calendar_callback
        :return: Возвращает кортеж (логическое значение,datetime), указывающий, выбрана ли дата
        , и возвращает дату, если это так.
        """
        return_data = (False, None)
        temp_date = datetime(int(data.year), int(data.month), 1)

        if data.act == SimpleCalendarAction.IGNORE:
            await query.answer(cache_time=60)

        if data.act == SimpleCalendarAction.DAY:
            await query.message.delete_reply_markup()
            return_data = True, datetime(int(data.year), int(data.month), int(data.day))

        if data.act == SimpleCalendarAction.PREV_YEAR:
            prev_date = datetime(int(data.year) - 1, int(data.month), 1)
            await query.message.edit_reply_markup(
                reply_markup=await self.start_calendar(
                    int(prev_date.year), int(prev_date.month)
                )
            )

        if data.act == SimpleCalendarAction.NEXT_YEAR:
            next_date = datetime(int(data.year) + 1, int(data.month), 1)
            await query.message.edit_reply_markup(
                reply_markup=await self.start_calendar(
                    int(next_date.year), int(next_date.month)
                )
            )

        if data.act == SimpleCalendarAction.PREV_MONTH:
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(
                reply_markup=await self.start_calendar(
                    int(prev_date.year), int(prev_date.month)
                )
            )

        if data.act == SimpleCalendarAction.NEXT_MONTH:
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(
                reply_markup=await self.start_calendar(
                    int(next_date.year), int(next_date.month)
                )
            )
        return return_data
