# -*- coding: UTF-8  -*-

from database.models import FlightSchedule
from pony.orm import db_session
import datetime

'''Use Python 3.9+'''


@db_session
def entering_the_schedule(schedule: list) -> None:
    FlightSchedule.select().delete(bulk=True)
    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    for departure_city, arrival_city, date_corrector, flight_number in schedule:
        date = today + date_corrector
        FlightSchedule(
            departure_city=departure_city,
            arrival_city=arrival_city,
            departure_date=date,
            flight_number=flight_number
        )
