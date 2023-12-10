import requests

from cfg import hv


def get_name_by_id(by_id: int, method: str) -> str:
    r = requests.get(f'https://api.vk.com/method/{method}',
                     params={
                         'access_token': hv.vk_token,
                         'v': 5.199,
                         'user_ids': abs(by_id)
                     })
    return r.json()['response']


class Post:
    def __init__(self, data):
        self.post_id = data.get('id')
        self.time = data.get('time')
        self.group_id = data.get('owner_id')
        self.group_name = get_name_by_id(by_id=self.group_id, method='groups.getById')
        self.signer_id = data.get('signer_id')
        self.signer_name = None
        self.signer_phone_number = None
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.text = data.get('text')
        self.repost = data.get('copy_history')
        self.repost_place_id = data['copy_history'][0].get('from_id') if self.repost else None
        self.repost_place_name = None
        self.attachments = get_attachments(data)
