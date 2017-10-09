# -*- coding: utf-8 -*-
import os
from pandas import DataFrame
import pandas as pd
from nltk.tokenize import RegexpTokenizer
import dill


class Articles(object):

    def __init__(self, path):
        self.path = os.path.join(os.getcwd(), path)
        self.raw_contents = []
        self.contents = []
        self.titles = []
        self.dictionary = {}
        self.indexer = {}
        self.articles_num = 0
        self.dict_num = 0
        self.universe = {}
        self.read_articles()

    def read_articles(self):
        file_names = os.listdir(self.path)
        for name in file_names:
            assert not os.path.isdir(name)
            with open(os.path.join(self.path, name), 'r') as f:
                iter_ = iter(f)
                self.titles.append(f.readline().replace("\n", "").strip())
                content = ""
                raw_content = []
                for line in iter_:
                    content += line
                    raw_content.append(line)
                self.contents.append(content)
                self.raw_contents.append(raw_content)
        self.articles_num = len(self.titles)
        self.universe = set(range(self.articles_num))
        for raw_content in self.raw_contents:
            for idx, line in enumerate(raw_content):
                if len(line) == 0 or line.isspace():
                    del raw_content[idx]
                else:
                    break

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
        content = self.contents[doc_id]

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
                self.indexer[word] = {doc_id}
            else:
                self.indexer[word].add(doc_id)
            self.dictionary[word] += 1
        self.dict_num = len(self.dictionary)

    def save(self, file_name):
        path = os.path.join(os.getcwd(), file_name)
        with open(path, 'wb') as f:
            dill.dump(self, f)

    def print_articles(self):
        # print(self.articles_num)
        # print(self.tokenize(self.titles[0]))
        print(type(self.dictionary))
        print(self.indexer['shoot'])
        print(self.universe)
        # print(self.titles)
        # print(self.dict[0:3])
        pass


if __name__ == "__main__":
    folder_name = "The Complete Works of William Shakespeare"
    a = Articles(folder_name)
    a.init_indexer()
    a.save("articles.pkl")
    # a.load("articles.pkl")
    a.print_articles()
