# -*- coding: UTF-8  -*-

from random import randint
from vk_api import bot_longpoll, VkApi
import logging.config

import handlers
from logging_config import log_config
import settings

logging.config.dictConfig(log_config)
log = logging.getLogger('chat_bot')


class UserState:

    def __init__(self, scenario_name: str, step_name: str, context: str = None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


class VkBot:

    def __init__(self, vk_token, group_id):
        self.api = VkApi(token=vk_token)
        self.group_id = group_id
        self.vk_bot = bot_longpoll.VkBotLongPoll(self.api, self.group_id)
        self.api_method = self.api.get_api()
        self.user_states = dict()

    def act(self):
        for event in self.vk_bot.listen():
            try:
                self.processing_event(event)
            except Exception as exc:
                log.exception('событие обработано с ошибкой', exc)

    def processing_event(self, event):
        if event.type != bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.info(f'Мы пока не умеем обрабатывать события типа {event.type}')
            return
        user_id = event.object.message['from_id']
        text = event.object.message['text'].lower()
        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id, text)
        else:
            text_to_send = self.find_intent(text, user_id)

        self.api_method.messages.send(message=text_to_send,
                                      user_id=user_id,
                                      random_id=randint(0, 2 ** 20)
                                      )

    def find_intent(self, text: str, user_id: int) -> str:
        for intent in settings.INTENTS:
            log.debug(f'User gets {intent}')
            if any(token in text for token in intent['tokens']):
                if intent['answer']:
                    text_to_send = intent['answer']
                else:
                    text_to_send = self.start_scenario(intent['scenario'], user_id)
                break
        else:
            text_to_send = settings.DEFAULT_ANSWER
        return text_to_send

    def start_scenario(self, scenario_name: str, user_id: int):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id: int, text: str) -> str:
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                self.user_states.pop(user_id)
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
        else:
            text_to_send = step['failure_text']
        return text_to_send


if __name__ == '__main__':
    bot = VkBot(vk_token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.act()
