from random import randint
from vk_api import bot_longpoll, VkApi
from _token import token


class VkBot:

    def __init__(self, vk_token, group_id=102260837):
        self.api = VkApi(token=vk_token)
        self.group_id = group_id
        self.vk_bot = bot_longpoll.VkBotLongPoll(self.api, self.group_id)
        self.api_method = self.api.get_api()

    def act(self):
        for event in self.vk_bot.listen():
            try:
                self.processing_event(event)
            except Exception as exc:
                print(exc)

    def processing_event(self, event):
        if event.type is bot_longpoll.VkBotEventType.MESSAGE_NEW:
            self.api_method.messages.send(message='Все говорят ' + event.message.text + ', а ты купи слона',
                                          user_id=event.message.from_id,
                                          random_id=randint(0, 2 ** 20)
                                          )
        else:
            print('неизвестное событие')


if __name__ == '__main__':
    bot = VkBot(vk_token=token)
    bot.act()