# -*- coding: UTF-8  -*-
"""Use Python 3.9+"""

import re
from datetime import date
from utils.generate_ticket import COMMENT_THIRD_STRING_LEN

re_name = r"[а-яё]+\s[а-яё]+$"


def handle_departure_city(text: str, choices: str, context: dict) -> bool:
    if text in choices:
        context['departure_city'] = text.title()
        return True
    else:
        return False


def handle_arrival_city(text: str, choices: str, context: dict) -> bool:
    if text in choices:
        context['arrival_city'] = text.title()
        return True
    else:
        return False


def handle_date(text: str, choices: str, context: dict) -> bool:
    try:
        year, month, day = [int(i) for i in text.split('-')]
        departure_date = str(date(year, month, day))
    except ValueError:
        return False
    if departure_date in choices:
        context['departure_date'] = departure_date
        return True
    else:
        return False


def handle_flight_number(text: str, choices: str, context: dict) -> bool:
    if text in choices:
        context['flight_number'] = text.upper()
        return True
    else:
        return False


def handle_number_of_seats(text: str, choices: str, context: dict) -> bool:
    if text.isdigit() and 0 < int(text) <= 224:
        context['number_of_seats'] = int(text)
        return True
    else:
        return False


def handle_comment(text: str, choices: str, context: dict) -> bool:
    if len(text) <= COMMENT_THIRD_STRING_LEN:
        context['comment'] = text.capitalize()
        return True
    else:
        return False


def handle_confirmation(text: str, choices: str, context: dict) -> bool:
    return 'да' in text or 'нет' in text


def handle_name(text: str, choices: str, context: dict) -> bool:
    """
    вкусовщина, но я бы сделал так:

    result = False
    if re.search(re_name, text):
        context['name'] = text.title()
        result = True
    return result


    """
    if re.search(re_name, text):
        context['name'] = text.title()
        return True
    else:
        return False
