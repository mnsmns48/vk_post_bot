import re
from typing import List

import requests

from cfg import hv


def get_name_by_id(_id: int | None, method: str) -> str:
    if _id is None:
        return 'Анонимно'
    else:
        params_depends = {
            'groups.getById': (
                'group_id',
                lambda x: x.json()['response']['groups'][0].get('name')),
            'users.get': (
                'user_ids',
                lambda x: f"{x.json()['response'][0].get('first_name')} {x.json()['response'][0].get('last_name')}")
        }
        params = {
            'access_token': hv.vk_token,
            'lang': 'ru',
            'v': 5.199,
            params_depends.get(method)[0]: abs(_id)
        }

        response = requests.get(f'https://api.vk.com/method/{method}',
                                params=params)
        output = params_depends.get(method)[1](response)
        return output


def get_contact(text: str) -> str | None:
    edit_text = text.replace('-', '').replace(')', '').replace('(', '')
    print(edit_text)
    match = re.findall(r'\b\+?[7,8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b', edit_text)
    try:
        if match[0]:
            response = match[0].replace(' ', '')
            if len(response) == 10:
                return f"7{response}"
    except IndexError:
        return None


class Post:
    def __init__(self, data):
        self.post_id = data.get('id')
        self.time = data.get('time')
        self.group_id = data.get('owner_id')
        self.group_name = get_name_by_id(_id=self.group_id, method='groups.getById')
        self.signer_id = data.get('signer_id')
        self.signer_name = get_name_by_id(_id=self.signer_id, method='users.get')
        self.signer_phone_number = get_contact(text=data.get('text'))
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.text = data.get('text')
        self.repost = data.get('copy_history')
        self.repost_place_id = data['copy_history'][0].get('from_id') if self.repost else None
        self.repost_place_name = None
        self.attachments = get_attachments(data)
