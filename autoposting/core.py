import re
from typing import List

import requests

from autoposting.crud import check_phone_number
from cfg import hv


def get_name_by_id(_id: int, method: str) -> str:
    params_depends = {
        'groups.getById': [
            'group_id',
            lambda x: x.json()['response']['groups'][0].get('name')
        ],
        'users.get': [
            'user_ids',
            lambda x: f"{x.json()['response'][0].get('first_name')} {x.json()['response'][0].get('last_name')}"
        ]
    }
    params = {
        'access_token': hv.vk_token,
        'lang': 'ru',
        'v': 5.199,
    }
    try:
        method = params_depends.setdefault('groups.getById')[0]
        params.update({params_depends.get(method)[0]: abs(_id)})
        params_depends.get(method)[0]: abs(_id)
        response = requests.get(f'https://api.vk.com/method/{method}', params=params)
        out = params_depends.get(method)[1](response)
        params_depends.pop(method)
        print(out)
    except KeyError:
        method = params_depends.setdefault('users.get')[0]
        params.update({params_depends.get(method)[0]: abs(_id)})
        response = requests.get(f'https://api.vk.com/method/{method}', params=params)
        out = params_depends.get(method)[1](response)
        print(out)


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


class Post:
    def __init__(self, data: dict):
        self.post_id = data.get('id')
        self.time = data.get('time')
        self.group_id = data.get('owner_id')
        self.group_name = get_name_by_id(_id=self.group_id, method='groups.getById')
        self.signer_phone_number = get_contact(text=data.get('text'))
        self.signer_id = de_anonymization(signer_id=data.get('signer_id'),
                                          phone_number=self.signer_phone_number)
        self.signer_name = get_name_by_id(_id=self.signer_id, method='users.get')
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.text = data.get('text')
        self.repost = True if data.get('copy_history') else False
        self.repost_place_id = data['copy_history'][0].get('from_id') if self.repost else None
        self.repost_place_name = get_name_by_id(_id=self.repost_place_id)
        # self.attachments = get_attachments(data)

    def display(self):
        print('self.post_id---', self.post_id)
        print('self.time---', self.time)
        print('self.group_id---', self.group_id)
        print('self.group_name---', self.group_name)
        print('self.signer_phone_number--', self.signer_phone_number)
        print('self.signer_id---', self.signer_id)
        print('self.signer_name---', self.signer_name)
        print('self.marked_as_ads---', self.marked_as_ads)
        print('self.text---', self.text)
        print('self.repost---', self.repost)
        print('self.repost_place_id---', self.repost_place_id)
        print('self.repost_place_name---', self.repost_place_name)
        print('------------------------------------')
