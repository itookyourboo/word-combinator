import logging
import json
from flask import Flask, request
from commands import DialogManager, State, COMMANDS
from ui import UI


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    res = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    req = request.json
    handle_dialog(res, req)
    user_id = get_user_id(req)
    if req["request"]["original_utterance"] != 'ping':
        logging.info(f"{user_id[:5]}\n"
                     f"REQ: {req['request']['original_utterance']}\n"
                     f"RES: {res['response']['text']}\n"
                     f"----------------------")
    return json.dumps(res)


def handle_dialog(res, req):
    user_id = get_user_id(req)
    original = req['request']['original_utterance']

    if original == 'ping':
        res['response']['text'] = 'Всё работает!'
        return

    if req['session']['new']:
        user = sessionStorage[user_id] = {}
        DialogManager.hello(res, user)
    else:
        if user_id not in sessionStorage:
            sessionStorage[user_id] = {'state': State.HELLO}

        user = sessionStorage[user_id]
        tokens = req['request']['nlu']['tokens']

        for cmd in COMMANDS:
            if any(word in tokens for word in cmd):
                COMMANDS[cmd]()(res, user)
                UI.add_default_buttons(res, user)
                return

        DialogManager.wtf(res, tokens, user)

    UI.add_default_buttons(res, user)


def get_user_id(req):
    return req['session']['user_id']
