# -*- coding: UTF-8 -*-

import datetime

from whoosh.index import open_dir
from whoosh.qparser import EveryPlugin
from whoosh.qparser import QueryParser
from whoosh.query import *

from build_index import Indexer
from nltk.tokenize import word_tokenize
import itertools

import numpy as np


def fmt_row(width, row, header=False):
    out = " | ".join(fmt_item(x, width) for x in row)
    if header:
        out = out + "\n" + "-" * len(out)
    return out


def fmt_item(x, l):
    if isinstance(x, np.ndarray):
        assert x.ndim == 0
        x = x.item()
    if isinstance(x, float):
        rep = "%g" % x
    else:
        rep = str(x)
    return " "*(l - len(rep)) + rep


color2num = dict(
    gray=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
    crimson=38
)


def colorize(string, color, bold=False, highlight=False):
    attr = []
    num = color2num[color]
    if highlight:
        num += 10
    attr.append(str(num))
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)


class Query(object):

    def __init__(self, index_name):
        self.index_name = index_name
        self.ix = open_dir(index_name)
        self.indexer = Indexer("./template/cache/")
        self.singleParser = QueryParser("word", schema=self.indexer.schema)
        self.searcher = self.ix.searcher()
        self.singleParser.add_plugin(EveryPlugin)

    def translate(self, word, level):
        query = self.singleParser.parse(word.lower())
        query = And([query, Term("level", level)])
        results = self.searcher.search(query)
        for result in results:
            self.log(word)
            return "%s [%s]" % (colorize(word, color='magenta'), colorize(result["translation"], color='white', bold=True))
        else:
            return word

    def query(self, sentence, level):
        ll = [[word_tokenize(w), ' '] for w in sentence.split()]
        words = list(itertools.chain(*list(itertools.chain(*ll))))
        str_ = ""
        for word in words:
            str_ += self.translate(word, level)
                
        return str_

    def process(self, filename, level):
        translated = ""
        with open(filename, 'r') as f:
            for line in f.readlines():
                translated += self.query(line, level)
                translated += '\n'
        return translated

    def log(self, sentence):
        with open('logging.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%y%m%d%H%M%S") + " " + sentence)


if __name__ == '__main__':
    q = Query('index')
    print(q.process("reading.txt", "toefl"))
