from paper_parser import PaperParser
from nltk.tokenize import RegexpTokenizer
import dill
import os
import numpy as np


class PaperQuery:

    def __init__(self, folder_name):
        self.pp = PaperParser(folder_name)
        self.tokenizer = RegexpTokenizer(r'\w+')

    def load_parser(self, file_name):
        path = os.path.join(os.getcwd(), file_name)
        with open(path, 'rb') as f:
            self.pp = dill.load(f)

    def make_vector(self, tokens):
        q_vector = np.array([.0] * self.pp.word_number)
        for token in tokens:
            assert isinstance(token, str)
            idx = self.pp.word_dict[token][0]
            if idx != -1:
                q_vector[idx] += 1
        q_vector[q_vector > 0] = np.log2(q_vector[q_vector > 0]) + 1
        assert q_vector.shape == self.pp.idf.shape
        q_vector = q_vector * self.pp.idf
        return q_vector

    def query(self, sent):
        tokens = self.tokenizer.tokenize(sent.lower())
        q_vector = self.make_vector(tokens)
        weights = np.array([.0] * self.pp.paper_number)
        for idx in range(self.pp.paper_number):
            weight = -np.dot(q_vector, self.pp.paper_vectors[idx])
            weights[idx] = weight
        return weights.argsort()


if __name__ == '__main__':
    pq = PaperQuery("static/papers")
    pq.load_parser("papers.pkl")
    print(pq.pp.title)
