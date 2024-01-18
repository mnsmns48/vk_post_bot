import logging.config
from logger_cfg import logger_config
import asyncio
from typing import List
import requests
from autoposting.cls import Post
from autoposting.core import clear_attachments_path
from autoposting.crud import read_post_data, write_post_data
from cfg import hv

logging.config.dictConfig(logger_config)
logger = logging.getLogger('logger')


def connect_wall(group_id: int) -> List:
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': hv.vk_token,
                         'v': 5.199,
                         'owner_id': group_id,
                         'count': hv.posts_quantity,
                         'offset': hv.posts_offset,
                     })
    return r.json()['response']['items']


async def start_autoposting():
    print('start autoposting')
    while True:
        for group_id in hv.vk_wall_id:
            volume_posts = connect_wall(group_id=group_id)
            volume_posts.reverse()
            for separate in volume_posts:
                logger.debug(f"{separate.get('id')} {separate.get('owner_id')} {separate.get('text')[:20]}")
                check = read_post_data(post_id=separate.get('id'),
                                       group_id=separate.get('owner_id'),
                                       text=separate.get('text'))
                if check:

                    one_post = Post(separate)
                    one_post.send_to_telegram()
                    write_post_data(one_post)
            clear_attachments_path()
        await asyncio.sleep(150)
