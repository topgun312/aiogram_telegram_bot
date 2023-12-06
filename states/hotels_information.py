from aiogram.fsm.state import State, StatesGroup


class Hotel_Info(StatesGroup):
    """
    Класс состояний пользователя.
    """
    user_command = State()
    city = State()
    location = State()
    city_loc = State()
    check_in = State()
    check_out = State()
    price_min = State()
    price_max = State()
    adults = State()
    childrens = State()
    hotels_count = State()
    images = State()
    bot_work_menu = State()
    bot_work_db = State()
    bot_work_back = State()
