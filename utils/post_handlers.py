# -*- coding: UTF-8  -*-
"""Use Python 3.9+"""

from pony.orm import db_session


@db_session
def confirm_post_handler(func, *args, **kwargs):
    if 'нет' in kwargs['text']:
        state = kwargs['state']
        state.delete()
        func(state.scenario_name, *args)
        return True
    else:
        return False
