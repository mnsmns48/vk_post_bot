from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, CallbackQuery, KeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy import select, Result, and_

from bot.bot_vars import bot
from cfg_and_engine import dobro_engine
from send_own_posts.models import Dobrotsen

dbt = Router()

dobrotsen_kb = InlineKeyboardBuilder()
dobrotsen_kb.add(InlineKeyboardButton(text='Цены в доброцене',
                                      callback_data='dobrotsen_start')
                 )


async def construct_dobrotsen_menu_kb() -> list:
    async with dobro_engine.scoped_session() as session:
        sub = select(Dobrotsen.parent).scalar_subquery()
        result: Result = await session.execute(select(Dobrotsen.title)
                                               .filter(and_(Dobrotsen.id.in_(sub), (Dobrotsen.parent == 0))))
    return list(result.scalars().all())


async def main_kb() -> ReplyKeyboardBuilder:
    buttons = await construct_dobrotsen_menu_kb()
    db_main_kb = ReplyKeyboardBuilder()
    for line in buttons:
        db_main_kb.row(KeyboardButton(text=line))
    return db_main_kb


async def dobrotsen_adv(c: CallbackQuery):
    m_kb = await main_kb()
    await c.answer('Запуск')
    await c.message.answer('Главное меню:', reply_markup=m_kb.as_markup())


async def dobrotsen_adv_m(m: Message):
    m_kb = await main_kb()
    await m.answer('Главное меню:', reply_markup=m_kb.as_markup())


async def get_dirs(title: str) -> dict:
    result_dict = dict()
    async with dobro_engine.scoped_session() as session:
        subquery = select(Dobrotsen.id).filter(Dobrotsen.title == title).scalar_subquery()
        query = select(Dobrotsen).filter(Dobrotsen.parent.in_(subquery)).order_by(Dobrotsen.price)
        result: Result = await session.execute(query)
    response = result.scalars().all()
    try:
        result_dict['items'] = [line for line in response]
        result_dict['end'] = True if response[0].price is not None else False
        return result_dict
    except IndexError as e:
        print(e)
        result_dict['error'] = True
        return result_dict


async def walking_dirs(m: Message):
    answer = await get_dirs(title=m.text)
    if answer.get('error') is True:
        kb = await main_kb()
        await m.answer(f'Нет товаров в категории - {m.text}', reply_markup=kb.as_markup(resize_keyboard=True,
                                                                                           is_persistent=True))
    else:
        if answer.get('end'):
            dbt2_ik = InlineKeyboardBuilder()
            for line in answer.get('items'):
                dbt2_ik.row(InlineKeyboardButton(text=f"{line.price}₽ {line.title[:35]}",
                                                 callback_data=str(line.id))
                            )
            await m.answer(f'Товары в {m.text}:', reply_markup=dbt2_ik.as_markup(resize_keyboard=True,
                                                                                 is_persistent=True))
        else:
            dbt2_rk = ReplyKeyboardBuilder()
            dbt2_rk.add(KeyboardButton(text='- - - Главное меню - - -'))
            for line in answer.get('items'):
                button = KeyboardButton(text=line.title)
                dbt2_rk.add(button)
                dbt2_rk.adjust(1)
            await m.answer(f'В меню {m.text} такие категории:',
                           reply_markup=dbt2_rk.as_markup(resize_keyboard=True,
                                                          is_persistent=True))


async def show_product(c: CallbackQuery):
    await c.answer('Загружаю картинку')
    query = select(Dobrotsen).filter(Dobrotsen.id == int(c.data))
    async with dobro_engine.scoped_session() as session:
        r: Result = await session.execute(query)
        result = r.scalars().one()
    await bot.send_photo(chat_id=c.from_user.id,
                         photo=result.image,
                         caption=f"{result.title}\n{result.price} руб.")


async def register_dbt_handlers():
    dbt.callback_query.register(dobrotsen_adv, F.data == 'dobrotsen_start')
    dbt.callback_query.register(show_product)
    dbt.message.register(dobrotsen_adv_m, F.text == '- - - Главное меню - - -')
    dbt.message.register(walking_dirs)
