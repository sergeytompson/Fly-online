# -*- coding: UTF-8  -*-
"""Use Python 3.9+"""

from database.models import FlightSchedule
from pony.orm import db_session, select
import datetime


def departure_city_choice_maker() -> str:
    with db_session:
        departure_cities = select(c.departure_city for c in FlightSchedule)[:]
    choices = 'Города, из которых летают наши самолеты:\n'
    for departure_city in departure_cities:
        choices += f'    {departure_city}\n'
    return choices


def arrival_city_choice_maker(context: dict) -> str:
    with db_session:
        arrival_cities = select(
            c.arrival_city for c in FlightSchedule if c.departure_city == context['departure_city'])[:]
    choices = f'Города, в которые летают наши самолеты из города {context["departure_city"]}:\n'
    for arrival_city in arrival_cities:
        choices += f'    {arrival_city}\n'
    return choices


def date_choice_maker(context: dict) -> str:
    with db_session:
        departure_dates = select(
            c.departure_date for c in FlightSchedule if c.departure_city == context['departure_city'] and
            c.arrival_city == context['arrival_city'])[:]
    choices = f'Дни, в которые летают наши самолеты из города {context["departure_city"]} в город ' \
              f'{context["arrival_city"]}:\n'
    for departure_date in departure_dates:
        choices += f'    {departure_date}\n'
    return choices


def flight_number_choice_maker(context: dict) -> str:
    departure_date = datetime.datetime.strptime(context['departure_date'], '%Y-%m-%d').date()
    with db_session:
        flight_numbers = select(
            c.flight_number for c in FlightSchedule if c.departure_city == context['departure_city'] and
            c.arrival_city == context['arrival_city'] and c.departure_date == departure_date)[:]
    choices = f'Рейсы из города {context["departure_city"]} в город {context["arrival_city"]}, ' \
              f'которые выполняют наши самолеты {departure_date}:\n'
    for flight_number in flight_numbers:
        choices += f'    {flight_number}\n'
    return choices
