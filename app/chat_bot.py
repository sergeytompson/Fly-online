# -*- coding: UTF-8  -*-

from io import BytesIO
from random import randint
from utils.generate_ticket import generate_ticket
import requests
from vk_api import bot_longpoll, VkApi
import logging.config
from database.models import UserState
from utils import handlers, choice_makers
from bot_log.logging_config import log_config
import settings
from pony.orm import db_session
from database.create_schedule import entering_the_schedule

'''Use Python 3.9+'''

entering_the_schedule(settings.FLIGHT_SCHEDULE)

logging.config.dictConfig(log_config)
log = logging.getLogger("chat_bot")


class VkBot:
    def __init__(self, vk_token: str, group_id: int):
        self.api = VkApi(token=vk_token)
        self.group_id = group_id
        self.vk_bot = bot_longpoll.VkBotLongPoll(self.api, self.group_id)
        self.api_method = self.api.get_api()
        self.api_version_map = {(0, 103): self._get_attr_from_api_before_5_103,
                                (103, float('inf')): self._get_attr_from_api_after_5_103}

    def run(self):
        for event in self.vk_bot.listen():
            try:
                self.processing_event(event)
            except Exception as exc:
                log.exception('событие обработано с ошибкой', exc)

    @db_session
    def processing_event(self, event: bot_longpoll.VkBotEvent) -> None:
        if event.type != bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info(f'Мы пока не умеем обрабатывать события типа {event.type}')
            return
        try:
            user_id, text = self._get_attr_depending_api_version(event)
        except TypeError:
            log.exception(f'Некорректно обрабатывается event для версии VkApi {event.raw["v"]}.'
                          f' Необходимо добавить эту логику')
        else:
            state = UserState.get(user_id=str(user_id))
            if state is not None:
                self.continue_scenario(text, state, user_id)
            else:
                self.find_intent(text, user_id)

    def _get_attr_depending_api_version(self, event: bot_longpoll.VkBotEvent) -> tuple[int, str]:
        api_version, api_sub_version = (int(i) for i in event.raw['v'].split('.'))
        if api_version < 5:
            log.info('Внимание! Работаем с версией api старее 5, может сработать некорректно')
            return self._get_attr_from_api_before_5_103(event)
        elif api_version > 5:
            log.info('Внимание! Работаем с версией api новее 5, может сработать некорректно')
            return self._get_attr_from_api_after_5_103(event)
        else:
            for k in self.api_version_map.keys():
                if k[0] <= api_sub_version < k[1]:
                    return self.api_version_map[k](event)

    @staticmethod
    def _get_attr_from_api_before_5_103(event: bot_longpoll.VkBotEvent) -> tuple[int, str]:
        return getattr(event.object, 'peer_id'), getattr(event.object, 'text')

    @staticmethod
    def _get_attr_from_api_after_5_103(event: bot_longpoll.VkBotEvent) -> tuple[int, str]:
        return event.object.message['from_id'], event.object.message['text']

    def find_intent(self, text: str, user_id: int) -> None:
        for intent in settings.INTENTS:
            log.debug(f'User gets {intent}')
            if any(token in text.lower() for token in intent['tokens']):
                if intent['answer']:
                    self.send_text(intent['answer'], user_id)
                else:
                    self.start_scenario(intent['scenario'], user_id)
                break
        else:
            self.send_text(settings.DEFAULT_ANSWER, user_id)

    def start_scenario(self, scenario_name: str, user_id: int) -> None:
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        choices = getattr(choice_makers, step['choice_maker'])()
        self.send_text(choices, user_id)
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, choices=choices.lower(),
                  context={})
        self.send_step(step, user_id, context={})

    def send_text(self, text_to_send: str, user_id: int) -> None:
        self.api_method.messages.send(message=text_to_send,
                                      user_id=user_id,
                                      random_id=randint(0, 2 ** 20)
                                      )

    def send_img(self, image: BytesIO, user_id: int) -> None:
        upload_url = self.api_method.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api_method.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api_method.messages.send(attachment=attachment,
                                      user_id=user_id,
                                      random_id=randint(0, 2 ** 20)
                                      )

    def send_step(self, step, user_id: int, context: dict) -> None:
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            image = generate_ticket(context)
            self.send_img(image, user_id)

    def continue_scenario(self, text: str, state: UserState, user_id: int) -> None:
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text.lower(), choices=state.choices, context=state.context):
            if state.step_name == 'step7' and 'нет' in text.lower():
                state.delete()
                self.start_scenario(state.scenario_name, user_id)
            else:
                next_step = steps[step['next_step']]
                if next_step['next_step']:
                    state.step_name = step['next_step']
                else:
                    log.info('Зарегистрирован - {name}\n'
                             'На рейс - {flight_number}\n'
                             'С датой вылета {departure_date}\n'
                             'Из {departure_city}\n'
                             'В {arrival_city}\n'
                             'Количество мест - {number_of_seats}'.format(**state.context))
                    state.delete()
                if next_step['choice_maker']:
                    choices = getattr(choice_makers, next_step['choice_maker'])(context=state.context)
                    state.choices = choices.lower()
                    self.send_text(choices, user_id)
                self.send_step(next_step, user_id, state.context)
        else:
            self.send_text(step['failure_text'], user_id)
