from unittest import TestCase
from unittest.mock import patch, Mock, ANY

from vk_api.bot_longpoll import VkBotMessageEvent

from chat_bot import VkBot


class ChatTests(TestCase):
    RAW_EVENT = {'group_id': 102260837, 'type': 'message_new', 'event_id': '0a844246825213d6a2e28e7dbedfae1bfa6c0c03',
                 'v': '5.131',
                 'object': {
                     'message':
                         {'date': 1658042320, 'from_id': 83083975, 'id': 81, 'out': 0, 'attachments': [],
                          'conversation_message_id': 81, 'fwd_messages': [], 'important': False, 'is_hidden': False,
                          'peer_id': 83083975, 'random_id': 0, 'text': 'привет'},
                     'client_info':
                         {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback',
                                             'intent_subscribe', 'intent_unsubscribe'],
                          'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}
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

    def test_processing_event(self):
        event = VkBotMessageEvent(raw=self.RAW_EVENT)
        send_mock = Mock()

        with patch('chat_bot.VkApi'):
            with patch('chat_bot.bot_longpoll.VkBotLongPoll'):
                bot = VkBot('', '')
                bot.api = Mock()
                bot.api_method.messages.send = send_mock

                bot.processing_event(event)

        send_mock.assert_called_once_with(
                                     message='Все говорят ' + self.RAW_EVENT['object']['message']['text'] +
                                             ', а ты купи слона',
                                     user_id=self.RAW_EVENT['object']['message']['from_id'],
                                     random_id=ANY
                                            )
