from typing import List

import requests
from cfg import hv


def connect(posts_quantity: int) -> List:
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': hv.vk_token,
                         'v': 5.199,
                         'owner_id': hv.vk_wall_id,
                         'count': posts_quantity,
                         'offset': 0
                     })

    return r.json()['response']['items']


async def start_autoposting():
    response = connect(hv.posts_quantity)
    response.reverse()
    for line in response:
        print(line)

