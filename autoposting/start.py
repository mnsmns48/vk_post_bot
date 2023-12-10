import asyncio
import time
from typing import List

import requests
from cfg import hv


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


async def start_autoposting():
    for group_id in hv.vk_wall_id:
        response = connect_wall(group_id)
        response.reverse()
        for line in response:
            print(line)
        print('-------------')
        await asyncio.sleep(2)

