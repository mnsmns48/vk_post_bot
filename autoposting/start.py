import os
from pathlib import Path
from shutil import rmtree
from typing import List
import requests
from autoposting.cls import Post
from autoposting.crud import write_post_data
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


def start_autoposting():
    for group_id in hv.vk_wall_id:
        volume_posts = connect_wall(group_id)
        volume_posts.reverse()
        for separate in volume_posts:
            one_post = Post(separate)
            files_list = [files for _, _, files in os.walk(hv.attach_catalog)]
            one_post.send_to_telegram(files=files_list[0])
            for path in Path(hv.attach_catalog).iterdir():
                if path.is_dir():
                    rmtree(path)
                else:
                    path.unlink()
            write_post_data(one_post)
