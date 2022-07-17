# -*- coding: UTF-8  -*-

log_config = {
    "version": 1,
    "formatters": {
        "file_bot_formatter": {
            "format": "%(asctime)s - %(name)s - %(message)s",
            "datefmt":  '%Y-%m-%d %H:%M'
        },
        "stream_bot_formatter": {
            "format": "%(name)s - %(message)s"
        },
    },
    "handlers": {
        "file_bot_handler": {
            "class": "logging.FileHandler",
            "formatter": "file_bot_formatter",
            "filename": "chat_bot.log",
            "encoding": "UTF-8",
            "level": "DEBUG"
        },
        "stream_bot_handler": {
            "class": "logging.StreamHandler",
            "formatter": "stream_bot_formatter",
            "level": "INFO"
        }
    },
    "loggers": {
        "chat_bot": {
            "handlers": ["file_bot_handler", "stream_bot_handler"],
            "level": "DEBUG",
        }
    },
}
