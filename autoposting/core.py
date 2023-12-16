import re
import time
import random
from typing import Callable, Any, Dict

import requests
import yt_dlp
from autoposting.crud import check_phone_number
from cfg import hv


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
            'group_id',
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


def get_contact(text: str | None) -> str | None:
    edit_text = text.replace('-', '').replace(')', '').replace('(', '')
    match = re.findall(r'\b\+?[7,8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b', edit_text)
    try:
        if match[0]:
            response = match[0].replace(' ', '')
            if len(response) == 10:
                return f"7{response}"
    except IndexError:
        return None


def de_anonymization(signer_id: int | None, phone_number: str | None) -> int | None:
    if signer_id is None and phone_number is None:
        return None
    elif isinstance(signer_id, int) and phone_number is None:
        return signer_id
    elif signer_id is None and phone_number:
        find_signer_in_db = check_phone_number(number=int(phone_number))
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


def get_attachments(data: dict, repost: bool) -> str | None:
    if repost:
        data.update(attachments=data['copy_history'][0]['attachments'])
    attachments = data.get('attachments')

    """ Checking attachments in post """

    if attachments:
        att_dict = dict()
        for attachment in attachments:
            att_type = attachment.get('type')
            depends_func = attachment_depends.get(att_type)
            att_dict[att_type] = att_dict.get(att_type, []) + [depends_func(attachment.get(att_type))]

        """ Checking VIDEOS in attachments and downloading """

        # videos = att_dict.get('video')
        # if videos:
        #     ydl_opts = {'outtmpl': '{hv.attach_catalog}%(title)s.%(ext)s'}
        #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #         try:
        #             ydl.download(videos)
        #         except yt_dlp.utils.DownloadError:
        #             pass
        #         time.sleep(3)

        """ Checking PHOTOS in attachments and downloading """

        # photos = att_dict.get('photo')
        # if photos:
        #     for photo in photos:
        #         name = random.randrange(10000)
        #         with open(f'{hv.attach_catalog}{str(name)}.jpg', 'wb') as fd:
        #             for chunk in requests.get(photo).iter_content(100000):
        #                 fd.write(chunk)
        #                 time.sleep(2.3)
        #         print(f'photo--{name}--downloaded')

        """ Checking DOCS in attachments and downloading """

        # docs = att_dict.get('doc')
        # if docs:
        #     for doc in docs:
        #         with open(f"{hv.attach_catalog}{doc.get('title')}.{doc.get('ext')}", 'wb') as fd:
        #             for chunk in requests.get(doc.get('link')).iter_content(100000):
        #                 fd.write(chunk)
        #                 time.sleep(2.3)
        #         print('doc downloaded')

        dict_variable = ' '.join([f'{key.capitalize()}:{len(value)}' for key, value in att_dict.items()])
        return dict_variable


""" Attachments Dependencies """

attachment_depends = {
    'video': lambda x: f"https://vk.com/video{x['owner_id']}_{x['id']}",
    'photo': lambda x: x['sizes'][-1].get('url'),
    'doc': docs_attachment_parsing,
    'link': lambda x: x.get('url'),
    'audio': lambda x: x.get('url'),
    'poll': lambda x: x.get('question')
}
