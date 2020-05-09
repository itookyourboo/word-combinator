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

        COMMANDS[words, states] = wrapped
        return wrapped

    return decorator


class DialogManager:
    @staticmethod
    def hello(res, user, user_id):
        if not DBHelper.exists(user_id):
            DBHelper.new_player(user_id)

        words, daily_words = DBHelper.get_words(user_id)
        if words == 0:
            res['response']['text'] = HELLO
            DBHelper.new_player(user_id)
        else:
            res['response']['text'] = f'{choice(HELLO_AGAIN)}\n' \
                                      f'Вы отгадали уже целых {words} {DBHelper.morph_words(words)}!\n' \
                                      f'Сыграем ещё?'
        res['response']['buttons'] = [UI.button('Да')]
        user['state'] = State.HELLO

    @staticmethod
    @command(HELP, states=(State.HELLO, State.PLAY))
    def help(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        state = user['state']
        if state == State.HELLO:
            res['response']['text'] = HELP_HELLO
        elif state == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)
            if not user['used_hint']:
                user['used_hint'] = True
                unnamed = user['unnamed'][:]
                shuffle(unnamed)
                res['response']['text'] = f'{HELP_PLAY.format(user["word"])}\n' \
                                          f'Подскажу парочку: {", ".join(unnamed[:min(2, len(unnamed))])}.\n' \
                                          f'Дальше сами.'
            else:
                res['response']['text'] = f'{HELP_PLAY.format(user["word"])}\n' \
                                          f'Больше не подскажу)'

            if ok:
                res['response']['text'] += '\n' + GameManager.what_and_how_much(named, user)

    @staticmethod
    @command(ABILITIES, states=(State.HELLO, State.PLAY))
    def abilities(res, req, session):
        res['response']['text'] = 'Я помогаю вам провести время с пользой. С помощью этой игры вы развиваете память, ' \
                                  'а также узнаёте новые слова.'

    @staticmethod
    @command(PLAY, states=(State.HELLO,))
    def play(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        word = DBHelper.get_random_word(8, 20)
        res['response']['text'] = f'{choice(YOUR_WORD)}{word}.\n' \
                                  f'{choice(CONSTRUCT)}\n' \
                                  f'Можете называть сразу несколько.'
        res['response']['buttons'] = [UI.button(choice(SOURCE_BTN))]
        user['state'] = State.PLAY
        user['word'] = word
        user['used_hint'] = False
        user['named'] = []
        user['unnamed'] = DBHelper.get_words_from_word(word)

        if DBHelper.get_words(user_id)[0] == 0:
            word = choice(list(filter(lambda x: len(x) > 3, user['unnamed'])))
            res['response']['buttons'].insert(0, UI.button(word.capitalize()))

    @staticmethod
    @command(STOP, states=(State.HELLO, State.PLAY))
    def stop(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)
            if ok:
                res['response']['text'] = GameManager.what_and_how_much(named, user)
            else:
                res['response']['text'] = f'{choice(INCORRECT)}.\nВы хотите выйти?'
                res['response']['buttons'] = [UI.button('Да'), UI.button('Нет')]
                user['state'] = State.WANNA_LEAVE
        elif user['state'] == State.HELLO:
            res['response']['text'] = 'Хорошо, будет скучно - обращайтесь!'
            res['response']['end_session'] = True

    @staticmethod
    @command(NAMED, states=(State.PLAY, State.HELLO))
    def named(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            ok, named = GameManager.check_for_unnamed(tokens, user, user_id)
            if ok:
                res['response']['text'] = GameManager.what_and_how_much(named, user)
            else:
                res['response']['text'] = f'{choice(YOUR_WORD)}{user["word"]}.\nВы отгадали {len(user["named"])}, ' \
                                          f'осталось ещё {len(user["unnamed"])}'
        elif user['state'] == State.HELLO:
            words, daily = DBHelper.get_words(user_id)
            res['response']['text'] = f'За всё время вы отгадали {words} '

    @staticmethod
    @command(YES, states=(State.WANNA_LEAVE, ))
    def leave(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        res['response']['text'] = 'Хорошо, закончили.\nЕсли захотите играть, так и скажите.'
        res['response']['buttons'] = [UI.button('Играть')]
        user['state'] = State.HELLO

    @staticmethod
    @command(NO, states=(State.WANNA_LEAVE, ))
    def stay(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        res['response']['text'] = f'Хорошо, продолжаем.\n' \
                                  f'{choice(YOUR_WORD)}{user["word"]}.\n' \
                                  f'Называйте одно или несколько слов сразу.'
        res['response']['buttons'] = [UI.button(choice(SOURCE_BTN))]
        user['state'] = State.PLAY

    @staticmethod
    def wtf(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        if user['state'] == State.PLAY:
            GameManager.init_words(res, req, session)
            return

        res['response']['text'] = choice(NOT_UNDERSTAND)
        DBHelper.add_wtf(user['state'], ' '.join(tokens))


class GameManager:
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
        return f'Засчитала {num} {DBHelper.morph_words(num)}: {", ".join(named)}.\nВсего найдено: {len(user["named"])}'

    @staticmethod
    def init_words(res, req, session):
        user_id, user, tokens = parse_info(req, session)
        ok, named = GameManager.check_for_unnamed(tokens, user, user_id)

        if ok == 0:
            res['response']['text'] = choice(INCORRECT)
        else:
            res['response']['text'] = GameManager.what_and_how_much(named, user)
        res['response']['buttons'] = [UI.button(choice(SOURCE_BTN))]

        if GameManager.check_for_win(user):
            res['response']['text'] += '\nБраво! Вы отгадали все слова!\nСыграем ещё?'
            user['state'] = State.HELLO
            res['response']['buttons'] = [UI.button('Да')]


def parse_info(req, session):
    user_id = req['session']['user_id']
    user = session[user_id]
    tokens = req['request']['nlu']['tokens']
    return user_id, user, tokens
