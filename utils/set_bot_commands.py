from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_default_commands(bot: Bot) -> None:
    """
    Функция для установки стандартных команд бота.
    :param bot: телеграмм бот
    """
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="help", description="Вывести справку"),
            BotCommand(
                command="lowprice",
                description="Узнать топ самых дешёвых отелей в городе",
            ),
            BotCommand(
                command="highprice",
                description="Узнать топ самых дорогих отелей в городе",
            ),
            BotCommand(
                command="bestdeal",
                description="Узнать топ отелей, наиболее подходящих по цене "
                "и расположению от центра (самые дешёвые и находятся ближе всего к центру)",
            ),
        ],
        BotCommandScopeDefault(),
    )
