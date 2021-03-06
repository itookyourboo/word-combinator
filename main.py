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
    original_utterance = req.get('request', {}).get('original_utterance', 'Empty request')
    if original_utterance != 'ping':
        logging.info(f"\n"
                     f"USR: {user_id[:5]}\n"
                     f"REQ: {original_utterance}\n"
                     f"RES: {res['response']['text']}\n"
                     f"----------------------")
    return json.dumps(res)


def handle_dialog(res, req):
    user_id = get_user_id(req)

    if req.get('request', {}).get('original_utterance', '') == 'ping':
        res['response']['text'] = 'Всё работает!'
        return

    if req['session']['new']:
        user = sessionStorage[user_id] = {}
        DialogManager.hello(res, user, user_id)
    else:
        if user_id not in sessionStorage:
            sessionStorage[user_id] = {'state': State.HELLO}

        user = sessionStorage[user_id]
        tokens = req.get('request', {}).get('nlu', {}).get('tokens', ['Empty'])

        for words, states in COMMANDS:
            if any(word in tokens for word in words) and user['state'] in states:
                COMMANDS[words, states]()(res, req, sessionStorage)
                UI.add_default_buttons(res, user)
                if 'text' in res.get('response', {}):
                    return

        DialogManager.wtf(res, req, sessionStorage)

    UI.add_default_buttons(res, user)


def get_user_id(req):
    return req['session']['user_id']
