from ui import UI
from dbhelper import get_random_word, get_words_from_word


class State:
    HELLO = 0
    PLAY = 1


HELP = ('помощь', 'помоги', 'как', 'подсказка')
ABILITIES = ('умеешь', 'можешь')
PLAY = ('да', 'играть', 'давай', 'сыграем', 'поехали', 'ок')
STOP = ('хватит', 'выход', 'закончить')


COMMANDS = {}


def command(words):
    def decorator(func):
        def wrapped():
            return func

        COMMANDS[words] = wrapped
        return wrapped

    return decorator


class DialogManager:
    @staticmethod
    def hello(res, user):
        res['response']['text'] = 'Привет! Это игра Комбинатор'
        res['response']['buttons'] = [UI.button('Играть')]
        user['state'] = State.HELLO

    @staticmethod
    @command(HELP)
    def help(res, user):
        state = user['state']
        if state == State.HELLO:
            res['response']['text'] = 'Я тебе очень помог'
        elif state == State.PLAY:
            res['response']['text'] = 'Играть надо так'
        else:
            res['response']['text'] = 'Добавь тут обработку)0'

    @staticmethod
    @command(ABILITIES)
    def abilities(res, user):
        res['response']['text'] = 'Я могу всё'

    @staticmethod
    @command(PLAY)
    def play(res, user):
        word = get_random_word(8, 20)
        res['response']['text'] = f'Вот твоё первое слово:\n{word}'
        res['response']['buttons'] = [UI.button('Закончить')]
        user['state'] = State.PLAY

        user['word'] = word
        user['named'] = []
        user['unnamed'] = get_words_from_word(word)

    @staticmethod
    @command(STOP)
    def stop(res, user):
        res['response']['text'] = 'Ты в главном меню'
        res['response']['buttons'] = [UI.button('Играть')]
        user['state'] = State.HELLO

    @staticmethod
    def wtf(res, tokens, user):
        if user['state'] == State.PLAY:
            DialogManager.init_words(res, tokens, user)
            return

        res['response']['text'] = 'Непонятно'
        # TODO: Write command and state to txt file

    @staticmethod
    def init_words(res, tokens, user):
        tmp = []
        for token in tokens:
            if token in user['unnamed']:
                tmp.append(token)
                user['unnamed'].remove(token)

        for x in tmp:
            user['named'].append(x)

        if len(tmp) == 0:
            res['response']['text'] = 'Хм, таких слов я не знаю'
        else:
            res['response']['text'] = f"Отгаданы следующие слова: {', '.join(tmp)}\n" \
                                      f"Всего вы нашли {len(user['named'])}"

        if len(user['unnamed']) == 0:
            res['response']['text'] += '\nБраво! Вы отгадали все слова!\nСыграем ещё?'
            user['state'] = State.HELLO
            res['response']['buttons'] = [UI.button('Да')]
