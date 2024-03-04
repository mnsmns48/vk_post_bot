import asyncio
from typing import List

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from autoposting.cls import Post, clear_attachments_path
from autoposting.crud import read_post_data, write_post_data
from autoposting.db_models import Base
from cfg_and_engine import hv, engine
from logger_cfg import logger


async def connect_wall(group_id: int) -> List:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.get('https://api.vk.com/method/wall.get',
                               params={
                                   'access_token': hv.vk_token,
                                   'v': 5.199,
                                   'owner_id': group_id,
                                   'count': hv.posts_quantity,
                                   'offset': hv.posts_offset,
                               }) as response:
            if response.status == 200:
                r = await response.json()
                return r['response']['items']


async def start_autoposting():
    async with engine.engine.begin() as as_session:
        await as_session.run_sync(Base.metadata.create_all)
    print('start autoposting')
    while True:
        for group_id in hv.vk_wall_id:
            volume_posts = await connect_wall(group_id=group_id)
            volume_posts.reverse()
            for separate in volume_posts:
                check = await read_post_data(post_id=separate.get('id'),
                                             group_id=separate.get('owner_id'),
                                             text=separate.get('text'))
                if check:
                    logger.debug(f"{separate.get('id')} {separate.get('owner_id')} {separate.get('text')[:20]}")
                    one_post = await Post(separate)
                    await one_post.send_to_telegram()
                    async with engine.scoped_session() as session:
                        await write_post_data(data=one_post, session=session)
            await clear_attachments_path()
        await asyncio.sleep(100)