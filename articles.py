# -*- coding: utf-8 -*-
import os
from pandas import DataFrame
import pandas as pd
from nltk.tokenize import RegexpTokenizer
import dill


class Articles(object):

    def __init__(self, path):
        self.path = path
        self.articles = []
        self.titles = []
        self.dictionary = {}
        self.indexer = {}
        self.articles_num = 0
        self.read_articles()

    def read_articles(self):
        file_names = os.listdir(self.path)
        for name in file_names:
            assert not os.path.isdir(name)
            with open(os.path.join(self.path, name), 'r') as f:
                iter_ = iter(f)
                self.titles.append(f.readline().replace("\n", ""))
                content = ""
                for line in iter_:
                    content += line
                self.articles.append(content)
        self.articles_num = len(self.titles)

    @staticmethod
    def rm_punc(content):
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(content)
        return words

    @staticmethod
    def turn_lower(content):
        return content.lower()

    @staticmethod
    def deduplicate(words):
        return list(set(words))

    def tokenize(self, doc_id):

        # get content from collection of articles
        content = self.articles[doc_id]

        # turn all words in articles into lowercase
        content = Articles.turn_lower(content)

        # remove punctuations
        words = Articles.rm_punc(content)

        # remove duplications
        words = Articles.deduplicate(words)

        return words

    def init_segments(self):

        segments = []

        for doc_id in range(self.articles_num):
            tokens = self.tokenize(doc_id)
            segments.append(tokens)

        return segments

    def init_indexer(self):

        segments = self.init_segments()
        full_dict = DataFrame(columns=[
            'word',
            'doc_id',
        ])
        for doc_id in range(self.articles_num):
            tokens = segments[doc_id]
            tiny_dict = DataFrame({
                'word': tokens,
                'doc_id': doc_id,
            })
            full_dict = pd.concat([full_dict, tiny_dict])
        full_dict = full_dict.sort_values(["word"], ascending=True, kind='mergesort')
        for _, row in full_dict.iterrows():
            word = row.word
            doc_id = row.doc_id
            if self.dictionary.setdefault(word, 0) == 0:
                self.indexer[word] = [doc_id]
            else:
                self.indexer[word].append(doc_id)
            self.dictionary[word] += 1

    def print_articles(self):
        # print(self.articles_num)
        # print(self.tokenize(self.titles[0]))
        print(type(self.dictionary))
        print(type(self.indexer))
        # print(self.titles)
        # print(self.dict[0:3])
        pass


if __name__ == "__main__":
    folder_name = "The Complete Works of William Shakespeare"
    a = Articles(folder_name)
    a.init_indexer()
    a.print_articles()
