# -*- coding: UTF-8  -*-
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from vk_api.bot_longpoll import VkBotMessageEvent

import settings
from chat_bot import VkBot


class ChatTests(TestCase):
    RAW_EVENT = {'group_id': 102260837,
                 'type': 'message_new',
                 'object': {
                     'message': {'date': 1658042320, 'from_id': 83083975, 'id': 81, 'out': 0, 'attachments': [],
                                 'conversation_message_id': 81, 'fwd_messages': [], 'important': False,
                                 'is_hidden': False,
                                 'peer_id': 83083975, 'random_id': 0, 'text': 'привет'}
                 }
                 }

    def test_act(self):
        count = 5
        events = [{}] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('chat_bot.VkApi'):
            with patch('chat_bot.bot_longpoll.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = VkBot('', '')
                bot.processing_event = Mock()
                bot.act()

        bot.processing_event.assert_called()
        bot.processing_event.assert_any_call({})
        assert bot.processing_event.call_count == count

    INPUTS = [
        'Привет',
        'А когда?',
        'Где будет конференция?',
        'Зарегистрируй меня',
        'Вениамин',
        'мой адрес email@email',
        'email@email.ru'
    ]

    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='email@email.ru')
    ]

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

        with patch('chat_bot.bot_longpoll.VkBotLongPoll', return_value=long_poller_mock):
            bot = VkBot('', '')
            bot.api_method = api_mock
            bot.act()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS
