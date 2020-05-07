import sqlite3
import os
import re


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
TABLE_NAME = 'ru'

RANDOM_WORD_SQL = 'select word from ' + TABLE_NAME + ' where length(word) between {} and {} order by random() limit 1'
WORDS_SQL = "select word from " + TABLE_NAME + " where word REGEXP '^[{0}]+$' and word <> '{0}'"

db = sqlite3.connect(DB_PATH)
db.create_function('REGEXP', 2, lambda expr, item: re.compile(expr).search(item) is not None)
cursor = db.cursor()


def get_random_word(start, end):
    return cursor.execute(RANDOM_WORD_SQL.format(start, end)).fetchone()[0]


def get_words_from_word(word):
    letters = {x: word.count(x) for x in word.lower()}
    words = filter(lambda x: all(x.count(q) <= letters.get(q, 0) for q in x),
                   map(lambda x: x[0],
                       cursor.execute(WORDS_SQL.format(word)).fetchall()))
    return list(words)


words_ = get_words_from_word('гельминт')
print(len(words_), *words_)