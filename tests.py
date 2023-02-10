# -*- coding: UTF-8  -*-

from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from pony.orm import rollback
from vk_api.bot_longpoll import VkBotMessageEvent

import settings
from app.chat_bot import VkBot
from utils.choice_makers import *
from database.models import FlightSchedule


def isolate_db(func):
    def wrapper(*args, **kwargs):
        with db_session:
            func(*args, **kwargs)
            rollback()

    return wrapper


class ChatTests(TestCase):
    RAW_EVENT = {'group_id': settings.GROUP_ID, 'type': 'message_new',
                 'event_id': '6335c9c205666af5e786f343b2c24b01712d37e9',
                 'v': '5.131', 'object': {
                    'message': {'date': 1665487793, 'from_id': 83083975, 'id': 671, 'out': 0, 'attachments': [],
                                'conversation_message_id': 671, 'fwd_messages': [], 'important': False,
                                'is_hidden': False, 'peer_id': 83083975, 'random_id': 0, 'text': 'Привет'},
                    'client_info': {
                                    'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback',
                                                       'intent_subscribe', 'intent_unsubscribe'],
                                    'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0
                                    }
                    }
                 }

    def test_act(self):
        count = 5
        events = [{}] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('app.chat_bot.VkApi'):
            with patch('app.chat_bot.bot_longpoll.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = VkBot('', 0)
                bot.processing_event = Mock()
                bot.send_img = Mock()
                bot.run()

        bot.processing_event.assert_called()
        bot.processing_event.assert_any_call({})
        assert bot.processing_event.call_count == count

    input_departure_city = settings.FLIGHT_SCHEDULE[0][0]
    input_arrival_city = settings.FLIGHT_SCHEDULE[0][1]
    with db_session:
        input_departure_date = str(select(
            c.departure_date for c in FlightSchedule if c.departure_city == input_departure_city and
            c.arrival_city == input_arrival_city)[:][0])
        input_flight_number = select(
            c.flight_number for c in FlightSchedule if c.departure_city == input_departure_city and
            c.arrival_city == input_arrival_city and
            c.departure_date == datetime.datetime.strptime(input_departure_date, '%Y-%m-%d').date())[:][0]

    INPUTS_CHOICES = {
        'departure_city': input_departure_city,
        'arrival_city': input_arrival_city,
        'departure_date': input_departure_date,
        'flight_number': input_flight_number,
        'number_of_seats': '2',
        'name': 'Богдан Малышонок'
    }

    INPUTS = [
        'Пока',
        'Привет',
        'билет',
        INPUTS_CHOICES['departure_city'],
        'Крпкстан',
        INPUTS_CHOICES['arrival_city'],
        INPUTS_CHOICES['departure_date'],
        INPUTS_CHOICES['flight_number'],
        INPUTS_CHOICES['number_of_seats'],
        ';aslkdf;ahsdfashdjfoawr;oughqeiugh;aoskkdfpasjfndkj;djkansdlkfjbashdbfjbherfukyqbwblfchslidbvfalhdsbfqjhwebfjl'
        'qwbelfbqwasdjfkasdjbfhlkajsdbflkqebflkasjbdsjwflkfjldblqkjwebflkqedbqldkjwf',
        'Бизнес-класс',
        'нет',
        INPUTS_CHOICES['departure_city'],
        INPUTS_CHOICES['arrival_city'],
        INPUTS_CHOICES['departure_date'],
        INPUTS_CHOICES['flight_number'],
        INPUTS_CHOICES['number_of_seats'],
        'Эконом',
        'да',
        INPUTS_CHOICES['name']
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        departure_city_choice_maker({}),
        settings.SCENARIOS['booking']['steps']['step1']['text'],
        arrival_city_choice_maker(INPUTS_CHOICES),
        settings.SCENARIOS['booking']['steps']['step2']['text'],
        settings.SCENARIOS['booking']['steps']['step2']['failure_text'],
        date_choice_maker(INPUTS_CHOICES),
        settings.SCENARIOS['booking']['steps']['step3']['text'],
        flight_number_choice_maker(INPUTS_CHOICES),
        settings.SCENARIOS['booking']['steps']['step4']['text'],
        settings.SCENARIOS['booking']['steps']['step5']['text'],
        settings.SCENARIOS['booking']['steps']['step6']['text'],
        settings.SCENARIOS['booking']['steps']['step6']['failure_text'],
        settings.SCENARIOS['booking']['steps']['step7']['text'].format(**INPUTS_CHOICES, comment='Бизнес-класс'),
        departure_city_choice_maker({}),
        settings.SCENARIOS['booking']['steps']['step1']['text'],
        arrival_city_choice_maker(INPUTS_CHOICES),
        settings.SCENARIOS['booking']['steps']['step2']['text'],
        date_choice_maker(INPUTS_CHOICES),
        settings.SCENARIOS['booking']['steps']['step3']['text'],
        flight_number_choice_maker(INPUTS_CHOICES),
        settings.SCENARIOS['booking']['steps']['step4']['text'],
        settings.SCENARIOS['booking']['steps']['step5']['text'],
        settings.SCENARIOS['booking']['steps']['step6']['text'],
        settings.SCENARIOS['booking']['steps']['step7']['text'].format(**INPUTS_CHOICES, comment='Эконом'),
        settings.SCENARIOS['booking']['steps']['step8']['text'],
        settings.SCENARIOS['booking']['steps']['step9']['text'].format(**INPUTS_CHOICES),
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('app.chat_bot.bot_longpoll.VkBotLongPoll', return_value=long_poller_mock):
            bot = VkBot('', 0)
            bot.api_method = api_mock
            bot.send_img = Mock()
            bot.run()

        assert send_mock.call_count == len(self.EXPECTED_OUTPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS
