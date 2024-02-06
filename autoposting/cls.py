from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from autoposting.core import \
    get_name_by_id, \
    get_contact, \
    de_anonymization, \
    get_attachments, \
    date_transform
from bot.bot_vars import bot
from cfg import hv


class Post:
    def __init__(self, data: dict):
        self.repost = True if data.get('copy_history') else False
        self.post_id = data.get('id')
        self.time = date_transform(data.get('date'))
        self.group_id = data.get('owner_id')
        self.group_name = get_name_by_id(_id=self.group_id)
        self.signer_phone_number = get_contact(data=data, is_repost=self.repost)
        self.signer_id = de_anonymization(data=data,
                                          is_repost=self.repost,
                                          phone_number=self.signer_phone_number)
        self.signer_name = get_name_by_id(_id=self.signer_id)
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.text = data.get('text') if self.repost is False else data['copy_history'][0].get('text')
        self.repost_place_id = data['copy_history'][0].get('from_id') if self.repost else None
        self.repost_place_name = get_name_by_id(_id=self.repost_place_id) if self.repost else None
        self.attachments = get_attachments(data, repost=self.repost)
        self.source = f"https://vk.com/wall{data.get('from_id')}_{data.get('id')}"

    async def caption_preparation(self) -> str | None:
        caption = self.text
        if self.repost:
            repost_place = 'public' if self.repost_place_id < 0 else 'id'
            repost = f"<b> → → → → Р Е П О С Т ↓ ↓ ↓ ↓</b>\n" \
                     f"<a href='https://vk.com/{repost_place}{abs(self.repost_place_id)}'>{self.repost_place_name}</a>\n"
            caption = repost + caption
        caption = f"{caption}\n<a href='https://vk.com/id{self.signer_id}'>" \
                  f"   👉  {self.signer_name}</a>" if self.signer_name != 'Анонимно' else f"{caption}"
        if self.marked_as_ads:
            caption = caption + '\n<i>          Платная реклама</i>\n'
        return caption

    async def send_to_telegram(self):
        caption = await self.caption_preparation()
        if self.attachments:
            files = self.attachments.get('out_list')
            ext_s = {
                'jpg': 'photo',
                'png': 'photo',
                'gif': 'photo',
                'jpeg': 'photo',
                'mp4': 'video',
                'mov': 'video',
                'mkv': 'video',
                'm4v': 'video',
                'txt': 'document',
                'pdf': 'document',
                'doc': 'document',
                'docx': 'document',
                'xls': 'document',
                'xlsx': 'document',
                'mp3': 'audio',
                'aac': 'audio'
            }
            media_group = MediaGroupBuilder()
            for file in files:
                media_group.add(type=str(ext_s.get(file.split('.')[-1])),
                                media=FSInputFile(f"{hv.attach_catalog}{file}"),
                                parse_mode='HTML'
                                )
            if len(caption) < 1024:
                media_group.caption = caption
                await bot.send_media_group(chat_id=hv.tg_chat_id,
                                           media=media_group.build(),
                                           disable_notification=hv.notification,
                                           request_timeout=1000)
            else:
                await bot.send_media_group(chat_id=hv.tg_chat_id,
                                           media=media_group.build(),
                                           disable_notification=hv.notification,
                                           request_timeout=1000)
                await bot.send_message(chat_id=hv.tg_chat_id,
                                       text=caption,
                                       parse_mode='HTML',
                                       disable_web_page_preview=True,
                                       disable_notification=hv.notification)
        else:
            await bot.send_message(chat_id=hv.tg_chat_id,
                                   text=caption,
                                   parse_mode='HTML',
                                   disable_web_page_preview=True,
                                   disable_notification=hv.notification
                                   )
