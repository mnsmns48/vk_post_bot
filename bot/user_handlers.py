from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.utils.media_group import MediaGroupBuilder

from bot.middleware import MediaGroupMiddleware
from bot.bot_db_func import write_user
from bot.bot_vars import bot
from bot.fsm import ListenUser
from bot.keyboards import main_kb, public
from cfg import hv

user_ = Router()
user_.message.middleware(MediaGroupMiddleware())


def receive_attach(album: MediaGroupBuilder, m: Message) -> MediaGroupBuilder:
    if m.content_type == ContentType.PHOTO:
        album.add_photo(m.photo[-1].file_id)
    if m.content_type == ContentType.VIDEO:
        album.add_video(m.video.file_id)
    return album


async def start(m: Message):
    write_user(m)
    await m.answer_photo(photo='AgACAgIAAxkBAAITZmQlo77a9vGGy1DlE30EBC652E9-AAIyxjEbbWMpSZgCRTKnxt4VAQADAgADeQADLwQ',
                         caption='Этот бот принимает посты в телеграм канал @leninocremia\n'
                                 'Нажимаем кнопочки под этим текстом\n',
                         reply_markup=main_kb.as_markup())


async def suggest_post_callback(c: CallbackQuery, state=FSMContext):
    await c.answer(text='Выбрано')
    await state.set_state(ListenUser.suggest_)
    await c.message.answer(text='Пиши текст, отправляй вложения\n\n'
                                'ВАЖНО!\n'
                                'Прислать нужно одним сообщением!\n\n'
                                'Если пост содержит фото и/или видеофайл, сначала добавьте эти файлы, '
                                'а текст прикрепите, как подпись к ним\n'
                                'Допускается до 10 медиафайлов\n\n'
                                'Жду пост....')


async def to_admin_callback(c: CallbackQuery, state=FSMContext):
    await c.answer(text='Выбрано')
    await state.set_state(ListenUser.to_admin_)
    await c.message.answer(text='АДМИН этого канала готов выслушать все предложения и пожелания')


async def to_admin(m: Message, state: FSMContext):
    text = f'Сообщение админу\nОт {m.from_user.full_name} {m.from_user.username}\n{m.text}'
    await bot.send_message(chat_id=hv.tg_bot_admin_id[0], text=text)
    await m.answer('Сообщение админу отправлено', reply_markup=main_kb.as_markup())
    await state.clear()


async def suggest_post(m: Message, state: FSMContext, album: list[Message] = None):
    answer_text = 'Твой пост будет выглядит так:\n'
    if m.content_type == ContentType.TEXT:
        await m.answer(f"{answer_text}\n\n{m.text}")
        await m.answer("Публикуем?", reply_markup=public.as_markup())
        return await state.clear()
    album_builder = MediaGroupBuilder(
        caption=m.caption
    )
    response = receive_attach(album=album_builder, m=m)
    if album:
        for i in range(1, len(album)):
            response.build().append(receive_attach(album=response, m=album[i]))
    await m.answer(f"{answer_text}\n\n{m.text if m.text else ' '}")
    await m.answer_media_group(response.build())
    await state.update_data(post=response)
    await m.answer("Публикуем?", reply_markup=public.as_markup())


async def callback_handler_public(c: CallbackQuery, state=FSMContext):
    await c.answer(text='Выбор сделан')
    a = await state.get_data()
    await bot.send_message(chat_id=hv.tg_bot_admin_id[0], text='!!!!!!!!!!Пост!!!!!!\n')
    await bot.send_media_group(chat_id=hv.tg_bot_admin_id[0], media=a.get('post').build())
    await c.message.answer('Отправлено. Ожидайте публикации', reply_markup=main_kb.as_markup())
    await state.clear()


async def callback_handler_again(c: CallbackQuery, state=FSMContext):
    await c.answer('Отмена')
    await c.message.answer('Попробуйте начать заново', reply_markup=main_kb.as_markup())
    await state.clear()


def register_user_handlers():
    user_.message.register(start, CommandStart())
    user_.callback_query.register(suggest_post_callback, F.data == 'suggest')
    user_.callback_query.register(to_admin_callback, F.data == 'to_admin')
    user_.message.register(to_admin, ListenUser.to_admin_)
    user_.message.register(suggest_post, ListenUser.suggest_)
    user_.callback_query.register(callback_handler_public, F.data == 'public')
    user_.callback_query.register(callback_handler_again, F.data == 'again')
