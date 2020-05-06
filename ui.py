from copy import deepcopy


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

        for button in ['Помощь', 'Что ты умеешь?']:
            button_dict = UI.button(button)
            if button_dict not in res['response']['buttons']:
                res['response']['buttons'].append(button_dict)

