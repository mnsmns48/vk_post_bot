import os

from autoposting.core import get_name_by_id, get_contact, de_anonymization, get_attachments, send_media_group, \
    send_only_text, date_transform
from cfg import hv


class Post:
    def __init__(self, data: dict):
        self.post_id = data.get('id')
        self.time = date_transform(data.get('date'))
        self.group_id = data.get('owner_id')
        self.group_name = get_name_by_id(_id=self.group_id)
        self.signer_phone_number = get_contact(text=data.get('text'))
        self.signer_id = de_anonymization(signer_id=data.get('signer_id'),
                                          phone_number=self.signer_phone_number)
        self.signer_name = get_name_by_id(_id=self.signer_id)
        self.marked_as_ads = True if data.get('marked_as_ads') == 1 else False
        self.repost = True if data.get('copy_history') else False
        self.text = data.get('text') if self.repost is False else data['copy_history'][0].get('text')
        self.repost_place_id = data['copy_history'][0].get('from_id') if self.repost else None
        self.repost_place_name = get_name_by_id(_id=self.repost_place_id) if self.repost else None
        self.attachments = get_attachments(data, repost=self.repost)
        self.source = f"https://vk.com/wall{data.get('from_id')}_{data.get('id')}"

    def caption_preparation(self) -> str | None:
        caption = self.text
        if self.repost:
            repost_place = 'public' if self.repost_place_id < 0 else 'id'
            repost = f"<b> → → → → Р Е П О С Т ↓ ↓ ↓ ↓</b>\n" \
                     f"<a href='https://vk.com/{repost_place}{self.repost_place_id}'>{self.repost_place_name}</a>\n\n"
            caption = repost + caption
        caption = f"{caption}\n<a href='https://vk.com/id{self.signer_id}'>" \
                  f" → → →  {self.signer_name}</a>\n" if self.signer_name != 'Анонимно' else f"{caption}"
        if self.marked_as_ads:
            caption = caption + '\n<i>          Платная реклама</i>\n'
        return caption

    def send_to_telegram(self, files: list | None):
        caption = self.caption_preparation()
        if files:
            ext_s = {
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
            for file in files:
                ext = file.split('.')[-1]
                files_dict[file] = ext_s.get(ext)
            list_attach = list()
            list_attach_docs = list()
            for key, value in files_dict.items():
                if value != 'document':
                    list_attach.append({
                        'type': value, 'media': f"attach://{key}", 'parse_mode': 'HTML'
                    })
                if value == 'document' or value == 'audio':
                    list_attach_docs.append({
                        'type': value, 'media': f"attach://{key}", 'parse_mode': 'HTML'
                    })
            if list_attach:
                if len(caption) < 1024:
                    send_media_group(attachments=list_attach, files=files, caption=caption)
                else:
                    send_media_group(attachments=list_attach, files=files, caption=None)
                    send_only_text(text=caption)
            if list_attach_docs:
                send_media_group(attachments=list_attach_docs, files=files, caption=None)
        else:
            send_only_text(text=caption)
