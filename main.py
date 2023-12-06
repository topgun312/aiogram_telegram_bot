import asyncio
from loguru import logger
import handlers
from database.aiosqlite_db import sql_start
from loader import bot, dp
from utils.set_bot_commands import set_default_commands


async def main():
    await sql_start()
    await set_default_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.add(
        "logs/logs_{time}.log",
        format="{time} {level} {message}",
        level="DEBUG",
        rotation="08:00",
        compression="zip",
    )
    logger.debug("Error")
    logger.info("Information message")
    logger.warning("Warning")
    asyncio.run(main())
