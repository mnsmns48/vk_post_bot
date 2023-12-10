from asyncio import current_task
from dataclasses import dataclass
from environs import Env
from pydantic.v1 import BaseSettings
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session


@dataclass
class Hidden:
    tg_bot_admin_id: list[int]
    tg_chat_id: int
    bot_token: str
    vk_api_token: str
    vk_token: str
    vk_wall_id: list
    posts_quantity: int
    notification: bool
    db_username: str
    db_password: str
    db_local_port: int
    db_name: str


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
        notification=env.bool("DISABLE_NOTIFICATION"),
        db_username=env.str("DB_USERNAME"),
        db_password=env.str("DB_PASSWORD"),
        db_local_port=env.int("DB_LOCAL_PORT"),
        db_name=env.str("DB_NAME")

    )


hv = load_hidden_vars(path='.env')


class CoreConfig(BaseSettings):
    base: str = (
        f"postgresql+asyncpg://{hv.db_username}:{hv.db_password}"
        f"@localhost:{hv.db_local_port}/{hv.db_name}"
    )
    db_echo: bool = False


dbconfig = CoreConfig()
async_engine_pg = create_async_engine(url=dbconfig.base,
                                      echo=dbconfig.db_echo,
                                      poolclass=NullPool)
async_session_factory_pg = async_sessionmaker(bind=async_engine_pg,
                                              expire_on_commit=False)
AsyncScopedSessionPG = async_scoped_session(session_factory=async_session_factory_pg,
                                            scopefunc=current_task)
