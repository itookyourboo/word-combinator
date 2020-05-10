from ui import UI
from dbhelper import DBHelper
from random import choice, shuffle
from states import State
from strings import *


COMMANDS = {}


def command(words, states):
    def decorator(func):
        def wrapped():
            return func

        COMMANDS[words, states if isinstance(states, tuple) else (states, )] = wrapped
        return wrapped

    return decorator


MAX_WORDS_TO_HINT = 2
MIN_WORD_LENGTH_TO_HINT = 4
WORD_MIN_LENGTH = 8
WORD_MAX_LENGTH = 20


class DialogManager:
    @staticmethod
    def hello(res, user, user_id):
        if not DBHelper.exists(user_id):
            DBHelper.new_player(user_id)

        words, daily_words = DBHelper.get_words(user_id)
        if words == 0:
            res['response']['text'] = get(HELLO)
            DBHelper.new_player(user_id)
        else:
            res['response']['text'] = f'{get(HELLO_AGAIN)}\n' \
                                      f'{get(START_FOUND)} {DBHelper.num_and_word(words)}!\n' \
                                      f'{get(PLAY_MORE)}'
            res['response']['tts'] = res['response']['text'].replace('слов', 'сл+ов')
        res['response']['buttons'] = [UI.button(get(YES_BTN))]
        user['state'] = State.HELLO

    @staticmethod
    @command(HELP, states=(State.HELLO, State.PLAY))
    def help(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        state = user['state']
        if state == State.HELLO:
            res['response']['text'] = get(HELP_HELLO)
        elif state == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)

            res['response']['text'] = f'{get(HELP_PLAY).format(user["word"].upper())}\n'
            if not user['used_hint']:
                user['used_hint'] = True
                unnamed = user['unnamed'][:]
                shuffle(unnamed)
                res['response']['text'] = f'{get(GIVE_HINT)} {", ".join(unnamed[:min(MAX_WORDS_TO_HINT, len(unnamed))])}.'
            else:
                res['response']['text'] = f'{get(HELP_PLAY).format(user["word"].upper())}\n' \
                                          f'{get(NO_HINT)}'

            if ok:
                res['response']['text'] += '\n' + GameManager.what_and_how_much(named, user)

    @staticmethod
    @command(ABILITIES, states=(State.HELLO, State.PLAY))
    def abilities(res, req, session):
        res['response']['text'] = get(WHAT_YOU_CAN)

    @staticmethod
    @command(PLAY, states=(State.HELLO,))
    def play(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        GameManager.start_new_game(res, user, user_id)

    @staticmethod
    @command(STOP, states=(State.HELLO, State.PLAY))
    def stop(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)
            res['response']['text'] = ''
            if ok:
                res['response']['text'] += GameManager.what_and_how_much(named, user) + '\n'

            res['response']['text'] += f'{get(WANNA_EXIT)}'
            res['response']['buttons'] = [UI.button(get(YES_BTN)), UI.button(get(NO_BTN)),
                                          UI.button(get(CHANGE_BTN))]
            user['state'] = State.WANNA_LEAVE

        elif user['state'] == State.HELLO:
            res['response']['text'] = get(LEFT)
            res['response']['end_session'] = True

    @staticmethod
    @command(CHANGE_WORD, states=(State.PLAY, State.WANNA_LEAVE))
    def change_word(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)
            res['response']['text'] = ''
            if ok:
                res['response']['text'] += GameManager.what_and_how_much(named, user) + '\n'

            res['response']['text'] += f'{get(WANNA_CHANGE)}'
            res['response']['buttons'] = [UI.button(get(YES_BTN)), UI.button(get(NO_BTN))]
            user['state'] = State.WANNA_CHANGE

        elif user['state'] == State.WANNA_LEAVE:
            GameManager.start_new_game(res, user, user_id, after_change=True)

    @staticmethod
    @command(NAMED, states=(State.PLAY, State.HELLO))
    def named(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)
            res['response']['text'] = ''
            if ok:
                res['response']['text'] = GameManager.what_and_how_much(named, user) + '\n'
            res['response']['text'] += f'{get(YOUR_WORD)}\n' \
                                       f'{user["word"].upper()}.\n' \
                                       f'{get(YOU_FOUND)} {len(user["named"])}, ' \
                                       f'{get(REMAINED)} {len(user["unnamed"])}'
        elif user['state'] == State.HELLO:
            words, daily = DBHelper.get_words(user_id)
            res['response']['text'] = f'{get(ALL_TIME_FOUND)} {DBHelper.num_and_word(words)}'

        res['response']['tts'] = res['response']['text'].replace('слов', 'сл+ов')

    @staticmethod
    @command(YES, states=State.WANNA_LEAVE)
    def leave(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        res['response']['text'] = get(OK_LEAVE)
        res['response']['buttons'] = [UI.button(get(PLAY_BTN))]
        user['state'] = State.HELLO

    @staticmethod
    @command(NO, states=(State.WANNA_LEAVE, State.WANNA_CHANGE))
    def stay(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        res['response']['text'] = f'{get(OK_STAY)}\n' \
                                  f'{get(YOUR_WORD)}\n' \
                                  f'{user["word"].upper()}.\n' \
                                  f'{choice((get(CAN_NAME_SEVERAL), get(I_CAN_CHANGE)))}'
        res['response']['buttons'] = [UI.button(get(SOURCE_BTN))]
        user['state'] = State.PLAY

    @staticmethod
    @command(YES, states=State.WANNA_CHANGE)
    def yes_change(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        GameManager.start_new_game(res, user, user_id, after_change=True)

    @staticmethod
    def wtf(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            GameManager.init_words(res, req, session)
            return

        res['response']['text'] = get(NOT_UNDERSTAND)
        res['response']['text'] += '\n' + (get(TO_START) if user['state'] == State.HELLO
                                           else get(TO_LEAVE))

        if 'original_utterance' not in req.get('request', {}):
            DBHelper.add_wtf(user['state'], ' '.join(tokens))
        else:
            DBHelper.add_wtf(user['state'], req['request']['original_utterance'])


class GameManager:
    @staticmethod
    def start_new_game(res, user, user_id, after_change=False):
        word = DBHelper.get_random_word(WORD_MIN_LENGTH, WORD_MAX_LENGTH)
        res['response']['text'] = f'{get(YOUR_WORD if after_change else START_WORD)}\n' \
                                  f'{word.upper()}.\n'
        res['response']['buttons'] = [UI.button(get(SOURCE_BTN))]

        user['state'] = State.PLAY
        user['word'] = word
        user['used_hint'] = False
        user['named'] = []
        user['unnamed'] = DBHelper.get_words_from_word(word)

        if DBHelper.get_words(user_id)[0] == 0:
            hint = choice(list(filter(lambda x: len(x) >= MIN_WORD_LENGTH_TO_HINT, user['unnamed'])))
            res['response']['buttons'].insert(0, UI.button(hint.capitalize()))
            res['response']['text'] += f'Подскажу первое - {hint}.\n'

        res['response']['text'] += f'{choice((get(CAN_NAME_SEVERAL), get(I_CAN_CHANGE)))}'

    @staticmethod
    def check_for_unnamed(tokens, user, user_id):
        tmp = []
        for token in tokens:
            if token in user['unnamed']:
                tmp.append(token)
                user['unnamed'].remove(token)

        for x in tmp:
            user['named'].append(x)

        if len(tmp) == 0:
            return False, None

        DBHelper.inc_words(user_id, len(tmp))
        return True, tmp

    @staticmethod
    def check_for_win(user):
        return len(user['unnamed']) == 0

    @staticmethod
    def what_and_how_much(named, user):
        num = len(named)
        return f'{get(CORRECT)}\n' \
               f'{get(COUNTED)} {DBHelper.num_and_word(num)}: {", ".join(named)}.\n' \
               f'{get(TOTAL_FOUND)} {len(user["named"])}'

    @staticmethod
    def init_words(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        ok, named = GameManager.check_for_unnamed(tokens, user, user_id)

        if ok == 0:
            res['response']['text'] = get(INCORRECT)
        else:
            res['response']['text'] = GameManager.what_and_how_much(named, user)
            res['response']['tts'] = res['response']['text'].replace('слов', 'сл+ов')

        res['response']['buttons'] = [UI.button(get(SOURCE_BTN))]

        if GameManager.check_for_win(user):
            res['response']['text'] += f'\n{get(WIN)}'
            user['state'] = State.HELLO
            res['response']['buttons'] = [UI.button(get(YES_BTN))]


def parse_info(req, session):
    user_id = req['session']['user_id']
    user = session[user_id]
    tokens = req['request']['nlu']['tokens']
    return user_id, user, tokens
