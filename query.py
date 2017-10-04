# -*- coding: utf-8 -*-

import os

from nltk import WordPunctTokenizer
from pandas import DataFrame
import pandas as pd
import dill
from articles import Articles


class Query(object):

    def __init__(self, path):
        self.articles = Articles(path)
        self.OPERATORS = {
            'and': '&',
            '&': '&',
            '*': '&',
            'or': '|',
            '|': '|',
            '+': '|',
            'not': '~',
            '~': '~',
            '!': '~',
            '(': '(',
            ')': ')',
        }
        self.PRIORITY = {
            '(': 0,
            ')': 0,
            '|': 1,
            '&': 2,
            '~': 3,
        }

    def load_articles(self, file_name):
        path = os.path.join(os.getcwd(), file_name)
        with open(path, 'rb') as f:
            self.articles = dill.load(f)

    @staticmethod
    def plus(p1, p2):
        assert isinstance(p1, set)
        assert isinstance(p2, set)
        return p1 | p2

    @staticmethod
    def mult(p1, p2):
        assert isinstance(p1, set)
        assert isinstance(p2, set)
        return p1 & p2

    def excl(self, p1):
        assert isinstance(p1, set)
        return self.articles.universe - p1

    def get_set(self, p1):
        assert isinstance(p1, str)
        return self.articles.indexer.get(p1, set([]))

    def to_post(self, elements):
        stack = []
        post = []
        num_parentheses = 0
        for element in elements:
            element_ = self.OPERATORS.get(element, None)
            if element_ is None:
                post.append(element)
            else:
                if element_ == '(':
                    num_parentheses += 1
                    stack.append(element_)
                elif len(stack) == 0:
                    stack.append(element_)
                elif element_ == ')':
                    assert len(stack) > 1
                    assert num_parentheses > 0
                    num_parentheses -= 1
                    while stack[-1] != '(':
                        post.append(stack.pop())
                        assert len(stack) > 0
                    stack.pop()
                elif self.PRIORITY[element_] > self.PRIORITY[stack[-1]]:
                    stack.append(element_)
                else:
                    while len(stack) > 0 and self.PRIORITY[element_] <= self.PRIORITY[stack[-1]]:
                        post.append(stack.pop())
                    stack.append(element_)
        assert num_parentheses == 0
        while len(stack) > 0:
            post.append(stack.pop())
        return post

    def to_keywords(self, elements):
        keywords = []
        for element in elements:
            if self.OPERATORS.get(element, None) is None:
                keywords.append(element)
        return keywords

    def calculate_post(self, post):
        stack = []
        for element in post:
            if self.OPERATORS.get(element, None) is None:
                stack.append(self.get_set(element))
            else:
                assert len(stack) > 0
                if element == '~':
                    p1 = stack.pop()
                    stack.append(self.excl(p1))
                elif element == '&':
                    p1 = stack.pop()
                    p2 = stack.pop()
                    stack.append(Query.mult(p1, p2))
                else:
                    p1 = stack.pop()
                    p2 = stack.pop()
                    stack.append(Query.plus(p1, p2))
        assert len(stack) == 1
        return stack.pop()

    @staticmethod
    def decorate_sent(sent):
        sent = sent.lower()
        sent = sent.replace('&', ' & ')
        sent = sent.replace('*', ' * ')
        sent = sent.replace('|', ' | ')
        sent = sent.replace('+', ' + ')
        sent = sent.replace('~', ' ~ ')
        sent = sent.replace('(', ' ( ')
        sent = sent.replace(')', ' ) ')
        return sent

    def query(self, sent):

        sent = Query.decorate_sent(sent)
        elements = WordPunctTokenizer().tokenize(sent)
        post = self.to_post(elements)
        result = self.calculate_post(post)
        return result

    def query_keywords(self, sent):

        sent = Query.decorate_sent(sent)
        elements = WordPunctTokenizer().tokenize(sent)
        keywords = self.to_keywords(elements)
        return keywords

if __name__ == '__main__':
    folder_name = "The Complete Works of William Shakespeare"
    q = Query(folder_name)
    q.load_articles('articles.pkl')
    q.query_keywords('a and the and not spit')