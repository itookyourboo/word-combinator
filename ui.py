from copy import deepcopy
from states import State
from strings import *


class UI:
    @staticmethod
    def button(text, hide=True):
        return {
            'title': text,
            'hide': hide
        }

    @staticmethod
    def add_default_buttons(res, user):
        if 'buttons' in res['response']:
            user['last_btns'] = deepcopy(res['response']['buttons'])
        else:
            res['response']['buttons'] = deepcopy(user.get('last_btns', []))

        if user['state'] == State.PLAY:
            for button in (HINT_BTN, CHANGE_BTN, HELP_BTN):
                btn = UI.button(button)
                if btn not in res['response'].get('buttons', []):
                    res['response'].get('buttons', []).append(btn)

        elif user['state'] == State.HELLO:
            for button in [get(HELP_BTN), get(WHAT_YOU_CAN_BTN)]:
                button_dict = UI.button(button)
                if button_dict not in res['response']['buttons']:
                    res['response']['buttons'].append(button_dict)
