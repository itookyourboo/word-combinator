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
            txt = get(HINT_BTN) if not user['used_hint'] else get(HELP_BTN)
            if all(x['title'] not in list(HINT_BTN) + list(HELP_BTN) for x in res['response']['buttons']):
                res['response']['buttons'].append(UI.button(txt))

            change_btn = UI.button(get(CHANGE_BTN))
            if change_btn not in res['response'].get('buttons', []):
                res['response'].get('buttons', []).append(change_btn)

        elif user['state'] == State.HELLO:
            for button in [get(HELP_BTN), get(WHAT_YOU_CAN_BTN)]:
                button_dict = UI.button(button)
                if button_dict not in res['response']['buttons']:
                    res['response']['buttons'].append(button_dict)
