import json
import os
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
        self.source = f"https://vk.com/wall{data.get('from_id')}_{data.get('id')}"

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
        print('self.attachments', self.attachments)
        print('self.source', self.source)
        print('------------------------------------')

    # @staticmethod
    def send_to_telegram(self, files: list | None):
        exts = {
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
        files_dict = dict()
        if files:
            files = files[0]
            for file in files:
                ext = file.split('.')[-1]
                files_dict[exts.get(ext)] = files_dict.get(exts.get(ext), []) + [file]
            attachments = {f'{item}': open(f'{hv.attach_catalog}/{item}', 'rb')
                           for item in files}
            print(files_dict)
            print(attachments)
            # list_attach = list()
            # photo = files_dict.get('photo')
            # if photo:
            #     for one_p in range(len(photo)):
            #         list_attach.append({'type': 'photo',
            #                              'media': f'attach://attach_unit{one_p}',
            #                              'parse_mode': 'HTML'})
            # video = files_dict.get('video')
            # if video:
            #     for one_v in range(len(video)):
            #         list_attach.append({'type': 'video',
            #                              'media': f'attach://attach_unit{one_v}',
            #                              'parse_mode': 'HTML'})
            # document = files_dict.get('document')
            # if document:
            #     for one_d in range(len(document)):
            #         list_attach.append({'type': 'document',
            #                              'media': f'attach://attach_unit{one_d}',
            #                              'parse_mode': 'HTML'})
            # list_attach[0]['caption'] = 'подпись'
            # print(list_attach)

        # media = json.dumps(list_attach)
        # params = {"chat_id": hv.tg_chat_id,
        #           "media": media,
        #           "disable_notification": True}
        # requests.post(hv.request_url_blank + '/sendMediaGroup', params=params, files=attachments)


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
        volume_posts = connect_wall(group_id)
        # response.reverse()
        for separate in volume_posts:
            one_post = Post(separate)
            files_list = [files for _, _, files in os.walk(hv.attach_catalog)]
            one_post.send_to_telegram(files=files_list)
