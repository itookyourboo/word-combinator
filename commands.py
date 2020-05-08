from ui import UI
from dbhelper import get_random_word, get_words_from_word


class State:
    HELLO = 0
    PLAY = 1
    WANNA_LEAVE = 2


HELP = (
    'помощь', 'помоги', 'подсказка'
)
ABILITIES = (
    'умеешь', 'можешь'
)
PLAY = (
    'да', 'играть', 'давай', 'сыграем', 'поехали', 'ок',
    'го', 'сыграть', 'поиграем', 'поиграть', 'играем'
)
NAMED = (
    'какие', 'слова', 'отгадал', 'сказал', 'разгадал', 'назвал',
    'названы', 'названо', 'отгадано', 'сколько', 'исходное', 'главное',
    'повтори', 'какое', 'слово'
)
STOP = (
    'нет', 'выход', 'хватит', 'пока', 'свидания', 'стоп', 'выйти',
    'выключи', 'останови', 'остановить', 'отмена', 'закончить',
    'закончи', 'отстань', 'назад', 'обратно', 'верни', 'вернись'
)


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
        res['response']['text'] = 'Привет! В этой игре вам нужно составлять слова из букв заданного слова.\n' \
                                  'Например, из слова "Комбинатор" можно составить слово "кот". Начнём?'
        res['response']['buttons'] = [UI.button('Да')]
        user['state'] = State.HELLO

    @staticmethod
    @command(HELP)
    def help(res, tokens, user):
        state = user['state']
        if state in (State.HELLO, State.WANNA_LEAVE):
            res['response']['text'] = 'Правила просты: я даю вам слово, а вы составляяете из его букв другие слова.\n' \
                                      'Но следите за количеством букв - из слова "Санки" нельзя составить "Ананас".\n' \
                                      'Приступим?'
        elif state == State.PLAY:
            ok, named = DialogManager.check_for_unnamed(tokens, user)
            res['response']['text'] = 'Составьте из букв данного слова другие слова. ' \
                                      'Можно называть одно или сразу несколько.'
            if ok:
                res['response']['text'] += '\n' + DialogManager.what_and_how_much(named, user)
        else:
            res['response']['text'] = 'Добавь тут обработку)'

    @staticmethod
    @command(ABILITIES)
    def abilities(res, tokens, user):
        res['response']['text'] = 'Я помогаю вам провести время с пользой. С помощью этой игры вы развиваете память, ' \
                                  'а также узнаёте новые слова.'

    @staticmethod
    @command(PLAY)
    def play(res, tokens, user):
        if user['state'] == State.HELLO:
            word = get_random_word(8, 20)
            res['response']['text'] = f'Итак, исходное слово: {word}.\nНазывайте одно или несколько новых слов.'
            res['response']['buttons'] = [UI.button('Назад')]
            user['state'] = State.PLAY

            user['word'] = word
            user['named'] = []
            user['unnamed'] = get_words_from_word(word)

        elif user['state'] == State.WANNA_LEAVE:
            res['response']['text'] = f'Хорошо, продолжаем. Исходное слово: {user["word"]}.\n' \
                                      f'Называйте слова'
            res['response']['buttons'] = [UI.button('Закончить')]
            user['state'] = State.PLAY

    @staticmethod
    @command(STOP)
    def stop(res, tokens, user):
        if user['state'] == State.PLAY:
            ok, named = DialogManager.check_for_unnamed(tokens, user)
            if ok:
                res['response']['text'] = DialogManager.what_and_how_much(named, user)
            else:
                res['response']['text'] = 'Такие слова не подходят. Продолжим игру?'
                res['response']['buttons'] = [UI.button('Да'), UI.button('Выйти')]
                user['state'] = State.WANNA_LEAVE
        elif user['state'] == State.WANNA_LEAVE:
            res['response']['text'] = 'Хорошо, закончили'
            res['response']['buttons'] = [UI.button('Играть')]
            user['state'] = State.HELLO
        elif user['state'] == State.HELLO:
            res['response']['text'] = 'Хорошо, будет скучно - обращайтесь!'

    @staticmethod
    @command(NAMED)
    def named(res, tokens, user):
        if user['state'] == State.PLAY:
            ok, named = DialogManager.check_for_unnamed(tokens, user)
            if ok:
                res['response']['text'] = DialogManager.what_and_how_much(named, user)
            else:
                res['response']['text'] = f'Слово: {user["word"]}.\nВы отгадали {len(user["named"])}, осталось ещё {len(user["unnamed"])}'

    @staticmethod
    def wtf(res, tokens, user):
        if user['state'] == State.PLAY:
            DialogManager.init_words(res, tokens, user)
            return

        res['response']['text'] = 'Извините, я вас не понимаю'
        # TODO: Write command and state to txt file

    @staticmethod
    def check_for_unnamed(tokens, user):
        tmp = []
        for token in tokens:
            if token in user['unnamed']:
                tmp.append(token)
                user['unnamed'].remove(token)

        for x in tmp:
            user['named'].append(x)

        if len(tmp) == 0:
            return False, None

        return True, tmp

    @staticmethod
    def check_for_win(user):
        return len(user['unnamed']) == 0

    @staticmethod
    def what_and_how_much(named, user):
        return f'Засчитала: {", ".join(named)}.\nВсего найдено: {len(user["named"])}'

    @staticmethod
    def init_words(res, tokens, user):
        ok, named = DialogManager.check_for_unnamed(tokens, user)

        if ok == 0:
            res['response']['text'] = 'Подумайте ещё'
        else:
            res['response']['text'] = DialogManager.what_and_how_much(named, user)

        if DialogManager.check_for_win(user):
            res['response']['text'] += '\nБраво! Вы отгадали все слова!\nСыграем ещё?'
            user['state'] = State.HELLO
            res['response']['buttons'] = [UI.button('Да')]
