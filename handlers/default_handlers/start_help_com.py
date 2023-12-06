from aiogram import types
from aiogram.filters import Command
from config_data.config_reader import DEFAULT_COMMANDS
from keyboards.reply.start_keyboard import markup_1
from loader import dp


@dp.message(Command("start"))
async def bot_start(message: types.Message) -> None:
    """
    Стартовая функция для начала работы бота.
    :param message: введеная команда пользователем.
    """
    await message.answer(
        f"Здравствуйте ✌ {message.from_user.first_name}, "
        f" если Вы ищите лучшее предложение по отелям нажмите '🚀 Старт 🚀'!",
        reply_markup=markup_1,
    )


@dp.message(Command("help"))
async def bot_help(message: types.Message) -> None:
    """
    Функция для работы команды help.
    :param message: введенная команда пользователем.
    """
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    await message.answer("\n".join(text))
