import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from typing import Any
import requests
import tzlocal
import yt_dlp
import random
from requests import Response
from autoposting.crud import check_phone_number
from cfg import hv


def date_transform(date: int) -> datetime:
    local_timezone = tzlocal.get_localzone()
    return datetime.fromtimestamp(date, local_timezone).replace(tzinfo=None)


def clear_attachments_path():
    files = [files for _, _, files in os.walk(hv.attach_catalog)]
    if len(files[0]) > 0:
        for path in Path(hv.attach_catalog).iterdir():
            if path.is_dir():
                rmtree(path)
            else:
                path.unlink()


def get_name_by_id(_id: int) -> str:
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
    return output


def get_contact(data: dict, is_repost: bool) -> int | None:
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
                return int(r)
    except IndexError:
        return None


def de_anonymization(data: dict, is_repost: bool, phone_number: int | None) -> int | None:
    if is_repost:
        signer_id = data['copy_history'][0].get('signer_id')
    else:
        signer_id = data.get('signer_id')
    if signer_id is None and phone_number is None:
        return None
    elif isinstance(signer_id, int) and phone_number is None:
        return signer_id
    elif signer_id is None and phone_number:
        find_signer_in_db = check_phone_number(number=phone_number)
        if find_signer_in_db:
            return find_signer_in_db
    return signer_id


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


def get_attachments(data: dict, repost: bool) -> dict | None:
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
                            'format': '[height<720]',
                            # 'format': 'worst'
                            }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(video)
                    title = ydl.prepare_filename(result)
                    if '.unknown_video' in title:
                        os.rename(f"{hv.attach_catalog}{name}.unknown_video", f"{hv.attach_catalog}{name}.mp4")
                out_list.append(title.replace('.unknown_video', '.mp4').split('\\')[-1])

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

        """ Checking DOCS in attachments and downloading """

        docs = att_dict.get('doc')
        if docs:
            for doc in docs:
                with open(f"{hv.attach_catalog}{doc.get('title')}.{doc.get('ext')}", 'wb') as fd:
                    for chunk in requests.get(doc.get('link')).iter_content(100000):
                        fd.write(chunk)
                        time.sleep(2.3)
                out_list.append(f"{doc.get('title')}.{doc.get('ext')}")
        out_dict = {'to_db_str': ''.join([f'{key.capitalize()}:{len(value)}' for key, value in att_dict.items()]),
                    'out_list': out_list}
        return out_dict
    return None


def send_media_group(attachments: list, files: list, caption: str | None) -> Response:
    attachment_files = {f'{item}': open(f'{hv.attach_catalog}/{item}', 'rb')
                        for item in files}
    if caption:
        attachments[0]['caption'] = caption if len(caption) <= 1024 else caption[:1024]
    media = json.dumps(attachments)
    params = {"chat_id": hv.tg_chat_id,
              'media': media,
              "disable_notification": hv.notification}
    response = requests.post(hv.request_url_blank + '/sendMediaGroup',
                             params=params,
                             files=attachment_files,
                             timeout=10000)
    return response


def send_only_text(text: str) -> Response:
    params = {"chat_id": hv.tg_chat_id,
              "text": text,
              "parse_mode": 'HTML',
              "disable_web_page_preview": True,
              "disable_notification": hv.notification
              }
    response = requests.post(hv.request_url_blank + '/sendMessage', params=params)
    return response


""" Attachments Dependencies """

attachment_depends = {
    'video': lambda x: f"https://vk.com/video{x['owner_id']}_{x['id']}",
    'photo': lambda x: x['sizes'][-1].get('url'),
    'doc': docs_attachment_parsing,
    'link': lambda x: x.get('url'),
    'audio': lambda x: x.get('url'),
    'poll': lambda x: x.get('question')
}
