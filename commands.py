from ui import UI


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
        res['response']['text'] = 'Вот твоё первое слово'
        res['response']['buttons'] = [UI.button('Закончить')]
        user['state'] = State.PLAY

    @staticmethod
    @command(STOP)
    def stop(res, user):
        res['response']['text'] = 'Ты в главном меню'
        res['response']['buttons'] = [UI.button('Играть')]
        user['state'] = State.HELLO

    @staticmethod
    def wtf(res, user):
        res['response']['text'] = 'Непонятно'
        # TODO: Write command and state to txt file
