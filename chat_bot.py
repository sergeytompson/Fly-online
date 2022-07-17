# -*- coding: UTF-8  -*-

from random import randint
from vk_api import bot_longpoll, VkApi
import logging.config
from logging_config import log_config

try:
    from settings import TOKEN, GROUP_ID
except ImportError:
    exit("Do cp settings.py.default settings.py and set token")

logging.config.dictConfig(log_config)
log = logging.getLogger("chat_bot")


class VkBot:
    def __init__(self, vk_token, group_id):
        self.api = VkApi(token=vk_token)
        self.group_id = group_id
        self.vk_bot = bot_longpoll.VkBotLongPoll(self.api, self.group_id)
        self.api_method = self.api.get_api()

    def act(self):
        for event in self.vk_bot.listen():
            try:
                self.processing_event(event)
            except Exception as exc:
                log.exception("событие обработано с ошибкой", exc)

    def processing_event(self, event):
        if event.type is bot_longpoll.VkBotEventType.MESSAGE_NEW:
            log.debug("отправляем сообщение назад")
            self.api_method.messages.send(
                message="Все говорят " + event.message.text + ", а ты купи слона",
                user_id=event.message.from_id,
                random_id=randint(0, 2**20),
            )
        else:
            log.info(f"Мы пока не умеем обрабатывать события типа {event.type}")


if __name__ == "__main__":
    bot = VkBot(vk_token=TOKEN, group_id=GROUP_ID)
    bot.act()
