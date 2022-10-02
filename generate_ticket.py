# -*- coding: UTF-8  -*-
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import requests

TEMPLATE_PATH = 'files/Билет.jpg'
FONT_PATH = 'files/calibri.ttf'
FONT_SIZE = 25
BLACK = (0, 0, 0, 255)
NAME_OFFSET = (237, 127)
EMAIL_OFFSET = (237, 164)
AVATAR_SIZE = (95, 95)
AVATAR_OFFSET = (50, 110)


def generate_ticket(name: str, email: str) -> BytesIO:
    base = Image.open(TEMPLATE_PATH)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw = ImageDraw.Draw(base)
    draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
    draw.text(EMAIL_OFFSET, email, font=font, fill=BLACK)
    response = requests.get(url=f'https://avatars.dicebear.com/api/micah/{email}.jpg')
    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)
    mini_avatar = avatar.resize(AVATAR_SIZE)
    base.paste(mini_avatar, AVATAR_OFFSET)

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file


generate_ticket('qwq', 'fdv')
