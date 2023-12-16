import time
from typing import List
import requests
from autoposting.core import get_attachments, get_name_by_id, get_contact, de_anonymization

from cfg import hv


class Post:
    def __init__(self, data: dict):
        self.post_id = data.get('id')
        self.time = data.get('date')
        self.group_id = data.get('owner_id')
        self.group_name = get_name_by_id(_id=self.group_id)
        self.signer_phone_number = get_contact(text=data.get('text'))
        self.signer_id = de_anonymization(signer_id=data.get('signer_id'),
                                          phone_number=self.signer_phone_number)
        self.signer_name = get_name_by_id(_id=self.signer_id)
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.text = data.get('text')
        self.repost = True if data.get('copy_history') else False
        self.repost_place_id = data['copy_history'][0].get('from_id') if self.repost else None
        self.repost_place_name = get_name_by_id(_id=self.repost_place_id)
        self.attachments = get_attachments(data, repost=self.repost)
        self.source = 'self.source'

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


def connect_wall(group_id: int) -> List:
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': hv.vk_token,
                         'v': 5.199,
                         'owner_id': group_id,
                         'count': hv.posts_quantity,
                         'offset': 0
                     })
    return r.json()['response']['items']


def start_autoposting():
    for group_id in hv.vk_wall_id:
        response = connect_wall(group_id)
        # response.reverse()
        for line in response:
            one_post = Post(line)
            time.sleep(3)
    #         text = line.get('text')
    #         print(get_contact(text=text))
    #         print('---------------------------------')
    #         await asyncio.sleep(1)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Posts.metadata.create_all)
