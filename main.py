# -*- coding: utf-8 -*-

"""Use Python 3.9+"""
from app.chat_bot import VkBot
import settings

if __name__ == '__main__':
    bot = VkBot(vk_token=settings.TOKEN, group_id=settings.GROUP_ID)
    bot.run()
