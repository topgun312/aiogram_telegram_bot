from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    rapid_api_key: SecretStr
    rapid_api_host: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()


DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("lowprice", "Узнать топ самых дешёвых отелей в городе"),
    ("highprice", "Узнать топ самых дорогих отелей в городе"),
    ("bestdeal", "Узнать топ отелей, наиболее подходящих по цене "
        "и расположению от центра (самые дешёвые и находятся ближе всего к центру)",
    ),
)
