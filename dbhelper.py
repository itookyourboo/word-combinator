import sqlite3
import os
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
WORDS_TABLE = 'ru'
PLAYERS_TABLE = 'players'

RANDOM_WORD_SQL = 'select word from ' + WORDS_TABLE + ' where length(word) between {} and {} order by random() limit 1'
WORDS_SQL = "select word from " + WORDS_TABLE + " where word REGEXP '^[{0}]+$' and word <> '{0}'"

db = sqlite3.connect(DB_PATH)
db.create_function('REGEXP', 2, lambda expr, item: re.compile(expr).search(item) is not None)
cursor = db.cursor()

cursor.execute(f'create table if not exists {PLAYERS_TABLE} (id string primary key, words integer, daily integer)')


class DBHelper:
    @staticmethod
    def get_random_word(start, end):
        return cursor.execute(RANDOM_WORD_SQL.format(start, end)).fetchone()[0].lower()

    @staticmethod
    def get_words_from_word(word):
        letters = {x: word.count(x) for x in word}
        words = filter(lambda x: all(x.count(q) <= letters.get(q, 0) for q in x),
                       map(lambda x: x[0],
                           cursor.execute(WORDS_SQL.format(word)).fetchall()))
        return list(words)

    @staticmethod
    def add_wtf(state, text):
        with open(os.path.join(BASE_DIR, 'wtf.txt'), 'a', encoding='utf8') as file:
            file.write(f'STATE: {state}, TEXT - {text}\n')

    @staticmethod
    def exists(user_id):
        return len(cursor.execute(f"select * from {PLAYERS_TABLE} where id = '{user_id}'").fetchall()) != 0

    @staticmethod
    def new_player(user_id):
        if DBHelper.exists(user_id):
            return

        cursor.execute(f"insert into {PLAYERS_TABLE} values('{user_id}', {0}, {0})")
        db.commit()

    @staticmethod
    def inc_words(user_id, number, daily=False):
        _, words, words_daily = cursor.execute(f"select * from {PLAYERS_TABLE} where id = '{user_id}'").fetchone()
        cursor.execute(f"update {PLAYERS_TABLE} set words = {words + number}, "
                       f"daily = {words_daily + int(daily) * number} "
                       f"where id = '{user_id}'")
        db.commit()

    @staticmethod
    def get_words(user_id):
        _, words, words_daily = cursor.execute(f"select * from {PLAYERS_TABLE} where id = '{user_id}'").fetchone()
        return words, words_daily

    @staticmethod
    def morph_words(num):
        if 10 <= num % 100 <= 20:
            return 'слов'

        elif (num % 10) in (0, 5, 6, 7, 8, 9):
            return 'слов'

        elif num % 10 == 1:
            return 'слово'
        elif (num % 10) in (2, 3, 4):
            return 'слова'

    @staticmethod
    def num_and_word(num):
        return f'{"одно" if num == 1 else num} {DBHelper.morph_words(num)}'


if __name__ == '__main__':
    while True:
        cursor.execute(input())
        [print(i) for i in cursor.fetchall()]
        db.commit()

#
# for i in range(120):
#     print(i, morph(i))

# words_ = DBHelper.get_words_from_word('вежливый')
# print(len(words_), *words_)
