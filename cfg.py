from dataclasses import dataclass
from environs import Env


@dataclass
class Hidden:
    tg_bot_admin_id: list[int]
    tg_chat_id: int
    bot_token: str
    vk_api_token: str
    vk_token: str
    vk_wall_id: int
    posts_quantity: int
    notification: bool


def load_hidden_vars(path: str):
    env = Env()
    env.read_env()

    return Hidden(
        tg_bot_admin_id=list(map(int, env.list("TELEGRAM_BOT_ADMIN_ID"))),
        tg_chat_id=env.int("TELEGRAM_CHAT_ID"),
        bot_token=env.str("BOT_TOKEN"),
        vk_api_token=env.str("VK_API_TOKEN"),
        vk_token=env.str("VK_TOKEN"),
        vk_wall_id=env.int("VK_WALL_ID"),
        posts_quantity=env.int("POSTS_QUANTITY"),
        notification=env.bool("DISABLE_NOTIFICATION"),
    )


hv = load_hidden_vars(path='.env')
