# -*- coding: UTF-8  -*-
from io import BytesIO
from random import randint

import requests
from vk_api import bot_longpoll, VkApi
import logging.config
from models import UserState, Registration
import handlers
from logging_config import log_config
import settings
from pony.orm import db_session

logging.config.dictConfig(log_config)
log = logging.getLogger("chat_bot")


# class UserState:
#
#     def __init__(self, scenario_name: str, step_name: str, context: str = None):
#         self.scenario_name = scenario_name
#         self.step_name = step_name
#         self.context = context or {}


class VkBot:
    def __init__(self, vk_token, group_id):
        self.api = VkApi(token=vk_token)
        self.group_id = group_id
        self.vk_bot = bot_longpoll.VkBotLongPoll(self.api, self.group_id)
        self.api_method = self.api.get_api()

    def run(self):
        for event in self.vk_bot.listen():
            try:
                self.processing_event(event)
            except Exception as exc:
                log.exception('событие обработано с ошибкой', exc)

    @db_session
    def processing_event(self, event):
        if event.type != bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info(f'Мы пока не умеем обрабатывать события типа {event.type}')
            return
        _, api_version = event.raw['v'].split('.')
        if int(api_version) >= 103:
            user_id = event.object.message['from_id']
            text = event.object.message['text'].lower()
        else:
            user_id = getattr(event.object, 'peer_id')
            text = getattr(event.object, 'text')
        state = UserState.get(user_id=str(user_id))
        if state is not None:
            self.continue_scenario(text, state, user_id)
        else:
            self.find_intent(text, user_id)

    def find_intent(self, text: str, user_id: int) -> None:
        for intent in settings.INTENTS:
            log.debug(f'User gets {intent}')
            if any(token in text for token in intent['tokens']):
                if intent['answer']:
                    self.send_text(intent['answer'], user_id)
                else:
                    self.start_scenario(intent['scenario'], user_id, text)
                break
        else:
            self.send_text(settings.DEFAULT_ANSWER, user_id)

    def start_scenario(self, scenario_name: str, user_id: int, text: str) -> None:
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})

    def send_text(self, text_to_send: str, user_id: int):
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

    def send_step(self, step, user_id: int, text: str, context: dict) -> None:
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context)
            self.send_img(image, user_id)

    def continue_scenario(self, text: str, state: UserState, user_id: int) -> None:
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            self.send_text(step['failure_text'], user_id)


if __name__ == '__main__':
    bot = VkBot(vk_token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.run()
