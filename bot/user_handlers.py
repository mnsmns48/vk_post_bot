from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMedia

from bot.middleware import MediaGroupMiddleware
from bot.bot_db_func import write_user
from bot.bot_vars import bot
from bot.fsm import ListenUser
from bot.keyboards import builder
from cfg import hv

user_ = Router()
user_.message.middleware(MediaGroupMiddleware())


async def start(m: Message):
    write_user(m)
    await m.answer_photo(photo='AgACAgIAAxkBAAITZmQlo77a9vGGy1DlE30EBC652E9-AAIyxjEbbWMpSZgCRTKnxt4VAQADAgADeQADLwQ',
                         caption='Этот бот принимает посты в телеграм канал @leninocremia\nНажимаем кнопочки под этим текстом\n',
                         reply_markup=builder.as_markup())


async def callback_handler(c: CallbackQuery, state=FSMContext):
    calls = {
        'suggest': [ListenUser.suggest_state, 'Пиши текст, отправляй вложения\n\n'
                                              'ВАЖНО!\n'
                                              'Прислать нужно одним сообщением!\n\n'
                                              'Если пост содержит фото и/или видеофайл, сначала добавьте эти файлы, '
                                              'а текст прикрепите, как подпись к ним\n'
                                              'Допускается до 10 медиафайлов\n\n'
                                              'Жду пост....'],
        'to_admin': [ListenUser.to_admin, 'АДМИН этого канала готов выслушать все предложения и пожелания']
    }
    await state.set_state(calls.get(c.data)[0])
    await c.message.answer(text=calls.get(c.data)[1])


async def to_admin(m: Message, state: FSMContext):
    text = f'Сообщение админу\nОт {m.from_user.full_name} {m.from_user.username}\n{m.text}'
    await bot.send_message(chat_id=hv.tg_bot_admin_id[0], text=text)
    await state.clear()


def picking_attachments(type_content: str, m: Message, album: list[Message] = None):
    if type_content == 'TEXT':
        return m.text
    media_group = list()
    elif type_content == 'PHOTO'
        media_group.append(InputMedia(media=m.photo[-1].file_id,
                                      type=m.content_type,
                                      caption=m.caption))
    if type_content == 'VIDEO':
        media_group.append(InputMedia(media=m.video['file_id'],
                                      type=m.content_type,
                                      caption=m.caption))

    print(media_group)

async def suggest_post(m: Message, state: FSMContext, album: list[Message] = None):
    answer_text = 'Твой пост будет выглядит так:\n'
    type_s = {'ContentType.PHOTO': picking_attachments(type_content='PHOTO', m=m, album=album),
              'ContentType.VIDEO': picking_attachments(type_content='VIDEO', m=m, album=album),
              'ContentType.TEXT': picking_attachments(type_content='TEXT', m=m, album=album)}
    a = type_s.get(str(m.content_type))
    # print(a)
    # print(m.content_type)
    # print(m.model_dump_json())
    # if album:
    #     print('Album True:')
    #     for i in album:
    #         print(i.model_dump_json())
    # else:
    #     print('album False')
    # print(album.model_dump_json())
    # for msg in album:
    #     print(msg.model_dump_json())
    #     if msg.photo:
    #         file_id = msg.photo[-1].file_id
    #     else:
    #         obj_dict = msg.model_dump_json()
    #         file_id = obj_dict[msg.content_type]['file_id']

    # txt = 'mg'
    # if m:
    #     txt = 'Ты прислал токлько текст'
    #     await m.answer(f'{txt}\n{m.text}')
    # if album:
    #     txt = m.text if m.text else 'Tы прислал только картинки'
    #     media_group: List = list()
    #     for msg in album:
    #         if msg.photo:
    #             file_id = msg.photo[-1].file_id
    #         else:
    #             obj_dict = msg.dict()
    #             file_id = obj_dict[msg.content_type]['file_id']
    #         try:
    #             if msg == album[0]:
    #                 media_group.append(InputMedia(media=file_id,
    #                                               type=msg.content_type,
    #                                               caption=txt))
    #             else:
    #                 media_group.append(InputMedia(media=file_id,
    #                                               type=msg.content_type))
    #         except ValueError:
    #             return await m.answer("This type of album is not supported")
    #     await m.answer_media_group(media_group)
    await state.clear()


def register_user_handlers():
    user_.callback_query.register(callback_handler)
    user_.message.register(suggest_post, ListenUser.suggest_state)
    user_.message.register(to_admin, ListenUser.to_admin)
    user_.message.register(start, CommandStart())
