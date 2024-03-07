import asyncio

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.triggers.cron import CronTrigger

from bot.bot_vars import bot
from cfg_and_engine import hv

bot_adv_trigger = CronTrigger(
    year="*", month="*", day="*", hour="19", minute="28", second="0"
)


async def send_message1():
    bot_kb = InlineKeyboardBuilder()
    bot_kb.add(InlineKeyboardButton(
        text='Жми сюда',
        url="https://t.me/pgtlenino_bot"))
    await bot.send_photo(
        chat_id=hv.tg_chat_id,
        photo='AgACAgIAAxkBAAIn2mXpmRs5aB1Lvfv9J2KV75F8weSaAAJa1jEb6SBRS6fyGk6aOahTAQADAgADeAADNAQ',
        caption='👩‍💻Предложить новость или связаться с администрацией паблика можно через бота',
        reply_markup=bot_kb.as_markup()
    )
    await asyncio.sleep(3)
    await bot.send_photo(
        chat_id=hv.tg_chat_id,
        photo='AgACAgIAAxkBAAIkbmXl7qS83ahNFL8TN9aTJvhfdiwkAAJo1TEbTEcwS3lDW3Qfwu-7AQADAgADbQADNAQ',
        caption='А ещё бот показывает цены в Доброцене',
        reply_markup=bot_kb.as_markup()
    )