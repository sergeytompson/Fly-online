# -*- coding: UTF-8  -*-
from datetime import date
from pony.orm import Database, Required, Json
from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария"""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    choices = Required(str)
    context = Required(Json)


class FlightSchedule(db.Entity):
    """Расписание полетов"""
    departure_city = Required(str)
    arrival_city = Required(str)
    departure_date = Required(date)
    flight_number = Required(str)


db.generate_mapping(create_tables=True)
