from aiogram import Bot, Dispatcher
from aiogram.dispatcher.dispatcher import MemoryStorage
from config_data.config_reader import config


storage = MemoryStorage()
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
