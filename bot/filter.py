from aiogram.filters import BaseFilter
from aiogram.types import Message

from cfg_and_engine import hv


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message):
        return (obj.from_user.id in hv.tg_bot_admin_id) == self.is_admin
