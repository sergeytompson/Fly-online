# -*- coding: UTF-8  -*-
'''Use Python 3.9+'''
import re
from io import BytesIO

from generate_ticket import generate_ticket

re_name = r"(^[\w\-\s]{2,30}$)"
re_email = r"(^\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b$)"


def handle_name(text: str, context: dict) -> bool:
    if re.search(re_name, text):
        context['name'] = text.capitalize()
        return True
    else:
        return False


def handle_email(text: str, context: dict) -> bool:
    coincidence = re.search(re_email, text)
    if coincidence:
        context['email'] = coincidence.group()
        return True
    else:
        return False


def generate_ticket_handler(text: str, context: dict) -> BytesIO:
    return generate_ticket(name=context['name'], email=context['email'])
