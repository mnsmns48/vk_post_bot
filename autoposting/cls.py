import asyncio
import os
import random
import re
import time
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from typing import Any

import requests
import tzlocal
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from yt_dlp import YoutubeDL

from autoposting.crud import check_phone_number
from bot.bot_vars import bot
from cfg import hv, engine
from logger_cfg import logger


class Post:
    def __init__(self, data: dict, *args, **kwargs):
        self.data = data
        self.repost = True if data.get('copy_history') else False
        self.repost_place_id = self.data['copy_history'][0].get('from_id') if self.repost else None
        self.post_id = data.get('id')
        self.time = datetime.fromtimestamp(data.get('date'), tzlocal.get_localzone()).replace(tzinfo=None)
        self.group_id = data.get('owner_id')
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.text = data.get('text') if self.repost is False else data['copy_history'][0].get('text')
        self.source = f"https://vk.com/wall{data.get('from_id')}_{data.get('id')}"
        self.__storedargs = args, kwargs
        self.async_initialized = False

    async def __ainit__(self, *args, **kwargs):
        self.group_name = await get_name_by_id(_id=self.group_id)
        self.signer_phone_number = await get_contact(data=self.data, is_repost=self.repost)
        self.signer_id = await de_anonymization(data=self.data,
                                                is_repost=self.repost,
                                                phone_number=self.signer_phone_number)
        self.signer_name = await get_name_by_id(_id=self.signer_id)
        self.repost_place_name = await get_name_by_id(_id=self.repost_place_id) if self.repost else None
        self.attachments = await get_attachments(self.data, repost=self.repost)

    async def __initobj(self):
        assert not self.async_initialized
        self.async_initialized = True
        await self.__ainit__(*self.__storedargs[0],
                             **self.__storedargs[1])
        return self

    def __await__(self):
        return self.__initobj().__await__()

    def __init_subclass__(cls, **kwargs):
        assert asyncio.iscoroutinefunction(cls.__ainit__)

    @property
    def async_state(self):
        if not self.async_initialized:
            return "[initialization pending]"
        return "[initialization done and successful]"

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
        await asyncio.sleep(0.1)
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
            await asyncio.sleep(3)
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


def docs_attachment_parsing(data: dict) -> dict[str, Any]:
    """ Docs types:
        1 — text docs;
        3 — gif;
        4 — pics;"""
    docs_depends = {
        1: lambda x: {
            'link': x.get('url'),
            'title': x.get('title'),
            'ext': x.get('ext')},
        3: lambda x: {
            'link': x['preview']['video'].get('src'),
            'title': x.get('title'),
            'ext': x.get('ext')},
        4: lambda x: {
            'link': x['preview']['photo']['sizes'][-1].get('src'),
            'title': x.get('title'),
            'ext': x.get('ext')}
    }
    func = docs_depends.get(data.get('type'))
    response = func(data)
    return response


async def get_attachments(data: dict, repost: bool) -> dict | None:
    if repost:
        data.update(attachments=data['copy_history'][0]['attachments'])
    attachments = data.get('attachments')

    """ Checking attachments in post """

    if attachments:
        out_list = list()
        att_dict = dict()
        for attachment in attachments:
            att_type = attachment.get('type')
            depends_func = attachment_depends.get(att_type)
            att_dict[att_type] = att_dict.get(att_type, []) + [depends_func(attachment.get(att_type))]

        """ Checking VIDEOS in attachments and downloading """
        videos = att_dict.get('video')
        if videos:
            for video in videos:
                name = random.randint(1, 100)
                ydl_opts = {'outtmpl': f'{hv.attach_catalog}{name}.%(ext)s',
                            'ie': 'vk',
                            'format': '[height<=480]/best',
                            'ignoreerrors': 'True',
                            }
                with YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(video)
                    if result:
                        title = ydl.prepare_filename(result)
                        if '.unknown_video' in title:
                            os.rename(f"{hv.attach_catalog}{name}.unknown_video", f"{hv.attach_catalog}{name}.mp4")
                        out_list.append(
                            title.replace(hv.attach_catalog, '').replace('.unknown_video', '.mp4').split('\\')[-1])
                    else:
                        logger.debug('Error loading video')
                await asyncio.sleep(3)

        """ Checking PHOTOS in attachments and downloading """

        photos = att_dict.get('photo')
        if photos:
            for photo in photos:
                name = random.randint(1, 100)
                with open(f'{hv.attach_catalog}{name}.jpg', 'wb') as fd:
                    for chunk in requests.get(photo).iter_content(100000):
                        fd.write(chunk)
                        time.sleep(2.4)
                out_list.append(f'{name}.jpg')
                await asyncio.sleep(0.1)

        """ Checking DOCS in attachments and downloading """

        docs = att_dict.get('doc')
        if docs:
            for doc in docs:
                with open(f"{hv.attach_catalog}{doc.get('title')}.{doc.get('ext')}", 'wb') as fd:
                    for chunk in requests.get(doc.get('link')).iter_content(100000):
                        fd.write(chunk)
                        time.sleep(2.3)
                await asyncio.sleep(0.1)
                out_list.append(f"{doc.get('title')}.{doc.get('ext')}")
        out_dict = {'to_db_str': ''.join([f'{key.capitalize()}:{len(value)}' for key, value in att_dict.items()]),
                    'out_list': out_list}
        return out_dict
    return None


async def get_name_by_id(_id: int) -> str:
    if _id is None:
        return 'Анонимно'
    params = {
        'access_token': hv.vk_token,
        'lang': 'ru',
        'v': 5.199,
    }
    params_depends = {
        'groups.getById': [
            'group_ids',
            'groups.getById',
            lambda x: x.json()['response']['groups'][0].get('name')
        ],
        'users.get': [
            'user_ids',
            'users.get',
            lambda x: f"{x.json()['response'][0].get('first_name')} {x.json()['response'][0].get('last_name')}"
        ]
    }
    if _id < 0:
        method = params_depends['groups.getById']
    else:
        method = params_depends['users.get']
    params.update({method[0]: abs(_id)})
    response = requests.get(f'https://api.vk.com/method/{method[1]}', params=params)
    output = method[2](response)
    await asyncio.sleep(0.1)
    return output


async def clear_attachments_path():
    files = [files for _, _, files in os.walk(hv.attach_catalog)]
    if len(files[0]) > 0:
        for path in Path(hv.attach_catalog).iterdir():
            if path.is_dir():
                rmtree(path)
            else:
                path.unlink()
    await asyncio.sleep(0.1)


async def get_contact(data: dict, is_repost: bool) -> int | None:
    if is_repost:
        text = data['copy_history'][0].get('text')
    else:
        text = data.get('text')
    edit_text = text.replace('-', '').replace(')', '').replace('(', '')
    match = re.findall(r'\b\+?[7,8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b', edit_text)
    try:
        if match[0]:
            response = match[0].replace(' ', '')
            if len(response) == 10:
                r = '7' + response
                await asyncio.sleep(0.1)
                return int(r)
    except IndexError:
        await asyncio.sleep(0.1)
        return None


async def de_anonymization(data: dict, is_repost: bool, phone_number: int | None) -> Any:
    if is_repost:
        signer_id = data['copy_history'][0].get('signer_id')
    else:
        signer_id = data.get('signer_id')
    if signer_id is None and phone_number is None:
        return None
    elif isinstance(signer_id, int) and phone_number is None:
        return signer_id
    elif signer_id is None and phone_number:
        async with AsyncSession(engine) as session:
            find_signer_in_db = await check_phone_number(number=phone_number, session=session)
        if find_signer_in_db:
            return find_signer_in_db
    return signer_id


""" Attachments Dependencies """
attachment_depends = {
    'video': lambda x: f"https://vk.com/video{x['owner_id']}_{x['id']}",
    'photo': lambda x: x['sizes'][-1].get('url'),
    'doc': docs_attachment_parsing,
    'link': lambda x: x.get('url'),
    'audio': lambda x: x.get('url'),
    'poll': lambda x: x.get('question')
}
