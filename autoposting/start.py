import time
from typing import List
import requests
from autoposting.core import Post, get_attachments

from cfg import hv, engine


def connect_wall(group_id: int) -> List:
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': hv.vk_token,
                         'v': 5.199,
                         'owner_id': group_id,
                         'count': hv.posts_quantity,
                         'offset': 2
                     })
    return r.json()['response']['items']


def start_autoposting():
    for group_id in hv.vk_wall_id:
        response = connect_wall(group_id)
        # response.reverse()
        for line in response:
            get_attachments(line)
            time.sleep(1)


    #         text = line.get('text')
    #         print(get_contact(text=text))
    #         print('---------------------------------')
    #         await asyncio.sleep(1)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Posts.metadata.create_all)


