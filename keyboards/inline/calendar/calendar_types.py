from enum import IntEnum
from aiogram.filters.callback_data import CallbackData


WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


class SimpleCalendarAction(IntEnum):
    IGNORE = 0
    SET_YEAR = 1
    PREV_YEAR = 2
    NEXT_YEAR = 3
    DAY = 4
    PREV_MONTH = 5
    NEXT_MONTH = 6


class SimpleCalendarCallback(CallbackData, prefix=""):
    act: SimpleCalendarAction
    year: int
    month: int
    day: int
