from copy import deepcopy
from states import State


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
            res['response']['buttons'] = deepcopy(user['last_btns'])

        if user['state'] == State.PLAY:
            txt = 'Подскажи' if not user['used_hint'] else 'Помощь'
            if all(x['title'] not in ('Подскажи', 'Помощь') for x in res['response']['buttons']):
                res['response']['buttons'].append(UI.button(txt))
        elif user['state'] == State.HELLO:
            for button in ['Помощь', 'Что ты умеешь?']:
                button_dict = UI.button(button)
                if button_dict not in res['response']['buttons']:
                    res['response']['buttons'].append(button_dict)