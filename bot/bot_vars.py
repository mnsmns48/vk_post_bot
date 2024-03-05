from aiogram import Bot, Dispatcher

from config.cfg_and_engine import hv

bot = Bot(token=hv.bot_token)
dp = Dispatcher()
