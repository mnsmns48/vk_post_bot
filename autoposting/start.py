import os
import time
from pathlib import Path
from shutil import rmtree
from typing import List
import requests
from autoposting.cls import Post
from autoposting.core import rename_unknown_video_files
from autoposting.crud import write_post_data, read_post_data
from cfg import hv


def connect_wall(group_id: int, offset: int) -> List:
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': hv.vk_token,
                         'v': 5.199,
                         'owner_id': group_id,
                         'count': hv.posts_quantity,
                         'offset': offset,
                     })
    return r.json()['response']['items']


def start_autoposting():
    while True:
        for group_id in hv.vk_wall_id:
            volume_posts = connect_wall(group_id=group_id, offset=hv.posts_offset)
            volume_posts.reverse()
            for separate in volume_posts:
                check = read_post_data(post_id=separate.get('id'),
                                       group_id=separate.get('owner_id'),
                                       text=separate.get('text'))
                if check:
                    one_post = Post(separate)
                    files_list = [files for _, _, files in os.walk(hv.attach_catalog)]
                    files_edited = rename_unknown_video_files(files_list[0])
                    one_post.send_to_telegram(files=files_edited)
                    for path in Path(hv.attach_catalog).iterdir():
                        if path.is_dir():
                            rmtree(path)
                        else:
                            path.unlink()
                    write_post_data(one_post)
        print('Новых постов нет')
        time.sleep(100)
