from typing import Any, Iterable, List, Union
import aiosqlite as sql
from aiosqlite import Row


DB_FILE = "hotels_db.db"


async def sql_start() -> None:
    """
    Функция для создания БД и создания таблицы hotels_info.
    """
    async with sql.connect(DB_FILE) as base:
        cur = await base.cursor()
        await cur.execute(
            "CREATE TABLE IF NOT EXISTS hotels_info"
            "(user_command, location, id, name, fonfoto, datetime)"
        )
        await base.commit()
    if cur:
        print("База данных подключена!")


async def sql_add_command(message: List[Union[str, Any]]) -> None:
    """
    Функция для записи данных в таблицу hotels_info.
    :param message: список данных для записи в таблицу.
    """
    async with sql.connect(DB_FILE) as base:
        cur = await base.cursor()
        await cur.execute(
            "INSERT INTO hotels_info VALUES(?, ?, ?, ?, ?, ?)", tuple(message)
        )
        await base.commit()


async def get_sql_db() -> Iterable[Row]:
    """
    Функция для получения данных из таблицы hotels_info.
    :return: список данных полученных из таблицы.
    """
    async with sql.connect(DB_FILE) as base:
        cur = await base.cursor()
        await cur.execute("SELECT * FROM hotels_info")
        return await cur.fetchall()


async def delete_info() -> None:
    """
    Функция для удаления данных с таблицы hotels_info.
    """
    async with sql.connect(DB_FILE) as base:
        cur = await base.cursor()
        await cur.execute("DELETE FROM hotels_info")
        await base.commit()
