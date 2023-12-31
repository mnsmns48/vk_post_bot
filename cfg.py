from dataclasses import dataclass
from environs import Env
from pydantic.v1 import BaseSettings
from sqlalchemy import create_engine


@dataclass
class Hidden:
    tg_bot_admin_id: list[int]
    tg_chat_id: int
    bot_token: str
    vk_api_token: str
    vk_token: str
    vk_wall_id: list
    posts_quantity: int
    posts_offset: int
    notification: bool
    db_username: str
    db_password: str
    db_local_port: int
    db_name: str
    attach_catalog: str
    request_url_blank: str
    filter_words: list[str]


def load_hidden_vars(path: str):
    env = Env()
    env.read_env()

    return Hidden(
        tg_bot_admin_id=list(map(int, env.list("TELEGRAM_BOT_ADMIN_ID"))),
        tg_chat_id=env.int("TELEGRAM_CHAT_ID"),
        bot_token=env.str("BOT_TOKEN"),
        vk_api_token=env.str("VK_API_TOKEN"),
        vk_token=env.str("VK_TOKEN"),
        vk_wall_id=list(map(int, env.list("VK_WALL_ID"))),
        posts_quantity=env.int("POSTS_QUANTITY"),
        posts_offset=env.int("POSTS_OFFSET"),
        notification=env.bool("DISABLE_NOTIFICATION"),
        db_username=env.str("DB_USERNAME"),
        db_password=env.str("DB_PASSWORD"),
        db_local_port=env.int("DB_LOCAL_PORT"),
        db_name=env.str("DB_NAME"),
        attach_catalog=env.str("ATTACH_CATALOG"),
        request_url_blank=env.str("REQUEST_URL_BLANK") + env.str("BOT_TOKEN"),
        filter_words=list(env.str("FILTER_WORDS").split(',')),
    )


hv = load_hidden_vars(path='.env')


class CoreConfig(BaseSettings):
    base: str = (
        f"postgresql+psycopg://{hv.db_username}:{hv.db_password}"
        f"@localhost:{hv.db_local_port}/{hv.db_name}"
    )
    db_echo: bool = False


dbconfig = CoreConfig()
engine = create_engine(url=dbconfig.base,
                       echo=dbconfig.db_echo)
