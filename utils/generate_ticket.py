# -*- coding: UTF-8  -*-

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

'''Use Python 3.9+'''

TEMPLATE_PATH = '../chat_bot/files/Билет.jpg'
FONT_PATH = '../chat_bot/files/calibri.ttf'
FONT_SIZE = 25
BLACK = (0, 0, 0, 255)
DEPARTURE_CITY_OFFSET = (147, 130)
ARRIVAL_CITY_OFFSET = (120, 182)
DEPARTURE_DATE_OFFSET = (578, 460)
FLIGHT_NUMBER_OFFSET = (600, 234)
NUMBER_OF_SEATS_OFFSET = (250, 234)
NAME_OFFSET = (205, 283)
COMMENT_FIRST_STRING_OFFSET = (188, 333)
COMMENT_FIRST_STRING_LEN = 45
COMMENT_SECOND_STRING_OFFSET = (30, 370)
COMMENT_SECOND_STRING_LEN = 104
COMMENT_THIRD_STRING_OFFSET = (30, 408)
COMMENT_THIRD_STRING_LEN = 163


def generate_ticket(context: dict) -> BytesIO:
    departure_city = context['departure_city']
    arrival_city = context['arrival_city']
    departure_date = context['departure_date']
    flight_number = context['flight_number']
    number_of_seats = str(context['number_of_seats'])
    comment = context['comment']
    name = context['name']
    base = Image.open(TEMPLATE_PATH)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    draw = ImageDraw.Draw(base)
    draw.text(DEPARTURE_CITY_OFFSET, departure_city, font=font, fill=BLACK)
    draw.text(ARRIVAL_CITY_OFFSET, arrival_city, font=font, fill=BLACK)
    draw.text(DEPARTURE_DATE_OFFSET, departure_date, font=font, fill=BLACK)
    draw.text(FLIGHT_NUMBER_OFFSET, flight_number, font=font, fill=BLACK)
    draw.text(NUMBER_OF_SEATS_OFFSET, number_of_seats, font=font, fill=BLACK)
    draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
    if len(comment) > COMMENT_SECOND_STRING_LEN:
        draw.text(COMMENT_THIRD_STRING_OFFSET, comment[COMMENT_SECOND_STRING_LEN:], font=font, fill=BLACK)
        comment = comment[:COMMENT_SECOND_STRING_LEN]
    if len(comment) > COMMENT_FIRST_STRING_LEN:
        draw.text(COMMENT_SECOND_STRING_OFFSET, comment[COMMENT_FIRST_STRING_LEN:], font=font, fill=BLACK)
        comment = comment[:COMMENT_FIRST_STRING_LEN]
    draw.text(COMMENT_FIRST_STRING_OFFSET, comment, font=font, fill=BLACK)

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
