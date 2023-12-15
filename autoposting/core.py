import re
import requests
import yt_dlp
from autoposting.crud import check_phone_number
from cfg import hv


def get_name_by_id(_id: int) -> str:
    if _id is None:
        return 'Анонимно'
    params = {
        'access_token': hv.vk_token,
        'lang': 'ru',
        'v': 5.199,
    }
    params_depends = {
        'groups.getById': [
            'group_id',
            'groups.getById',
            lambda x: x.json()['response']['groups'][0].get('name')
        ],
        'users.get': [
            'user_ids',
            'users.get',
            lambda x: f"{x.json()['response'][0].get('first_name')} {x.json()['response'][0].get('last_name')}"
        ]
    }
    if _id < 0:
        method = params_depends['groups.getById']
    else:
        method = params_depends['users.get']
    params.update({method[0]: abs(_id)})
    response = requests.get(f'https://api.vk.com/method/{method[1]}', params=params)
    output = method[2](response)
    return output


def get_contact(text: str | None) -> str | None:
    edit_text = text.replace('-', '').replace(')', '').replace('(', '')
    match = re.findall(r'\b\+?[7,8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b', edit_text)
    try:
        if match[0]:
            response = match[0].replace(' ', '')
            if len(response) == 10:
                return f"7{response}"
    except IndexError:
        return None


def de_anonymization(signer_id: int | None, phone_number: str | None) -> int | None:
    if signer_id is None and phone_number is None:
        return None
    elif isinstance(signer_id, int) and phone_number is None:
        return signer_id
    elif signer_id is None and phone_number:
        find_signer_in_db = check_phone_number(number=int(phone_number))
        if find_signer_in_db:
            return find_signer_in_db
    return signer_id


def get_video(attachments: dict):
    video_list = list()
    for video in attachments.get('video'):
        video_list.append(video)
    ydl_opts = {'outtmpl': 'attachments/%(title)s.%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_list)


def get_attachments(data: dict, repost: bool) -> dict:
    attachment_depends = {
        'video': lambda x: f"https://vk.com/video{x['owner_id']}_{x['id']}",
        'photo': lambda x: x['sizes'][-1].get('url'),
        'doc': lambda x: x['doc']['preview']['photo']['sizes'][-1].get('src'),
        'link': lambda x: x.get('url'),
        'audio': lambda x: x.get('url')

    }
    if repost:
        data.update(attachments=data['copy_history'][0]['attachments'])
    atts = data.get('attachments')
    att_dict = dict()
    for attachment in atts:
        att_type = attachment.get('type')
        depends_func = attachment_depends.get(att_type)
        att_dict[att_type] = att_dict.get(att_type, []) + [depends_func(attachment.get(att_type))]
    return att_dict
