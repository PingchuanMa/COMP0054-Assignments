import os
from collections import defaultdict
from io import StringIO
import numpy as np
import dill

from nltk.tokenize import RegexpTokenizer
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage


def load_articles(file_name):
    path = os.path.join(os.getcwd(), file_name)
    with open(path, 'rb') as f:
        return dill.load(f)


class PaperParser:
    def __init__(self, path):
        self.path = path
        self.word_dict = defaultdict(lambda: [-1])
        self.idf = np.array([])
        self.word_number = 0
        self.paper_number = 0
        self.title = []
        self.contents = []
        self.abstract = []
        self.paper_vectors = []
        self.file_names = []

    def extract_content(self):
        self.file_names = os.listdir(self.path)
        self.file_names.sort()
        self.paper_number = len(self.file_names)
        for cnt, name in enumerate(self.file_names):
            file_path = os.path.join(self.path, name)
            assert os.path.isfile(file_path)
            with open(file_path, 'rb') as fp:
                rsrcmgr = PDFResourceManager(caching=False)
                retstr = StringIO()
                device = TextConverter(PDFResourceManager(), retstr, codec='utf-8', laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                for page in PDFPage.get_pages(fp, set()):
                    interpreter.process_page(page)
                text = retstr.getvalue()
                lines = text.splitlines(keepends=False)
                self.make_brief(lines)
                text = self.turn_lower(text)
                self.contents.append(self.rm_punc(text))
                print(cnt, "/", self.paper_number)
                print(self.title[cnt])

    def make_dict(self):
        for content in self.contents:
            for word in content:
                word_info = self.word_dict[word]
                if word_info[0] == -1:
                    word_info[0] = self.word_number
                    self.word_number += 1

    @staticmethod
    def rm_punc(content):
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(content)
        return words

    @staticmethod
    def turn_lower(content):
        return content.lower()

    def make_brief(self, lines):
        abstract = []
        for idx, line in enumerate(lines):
            if idx == 0:
                self.title.append(line)
                continue
            line = line.strip()
            if len(line) == 0 or line == "\n":
                continue
            abstract.append(line)
            if len(abstract) > 5:
                break
        self.abstract.append(abstract)

    def make_vectors(self):
        for content in self.contents:
            vector = self.make_vector(content)
            self.paper_vectors.append(vector)

    def make_vector(self, content):
        vector = np.array([0.] * self.word_number)
        for word in content:
            idx = self.word_dict[word][0]
            assert idx >= 0
            vector[idx] += 1
        vector[vector > 0] = np.log2(vector[vector > 0]) + 1
        norm = np.linalg.norm(vector)
        return vector / norm

    def save(self, file_name):
        path = os.path.join(os.getcwd(), file_name)
        with open(path, 'wb') as f:
            dill.dump(self, f)

    def make_idf(self):
        df = np.array([0.] * self.word_number)
        for vector in self.paper_vectors:
            df[np.nonzero(vector)] += 1
        # for idx, val in enumerate(df):
        #     if val == 0:
        #         print(idx)
        # print(self.paper_number)
        idf = np.log2(self.paper_number / df)
        # print(idf)
        norm = np.linalg.norm(idf)
        # print(norm)
        self.idf = idf / norm

    # def make_metadata(self, filename, document):
    #     self.paper_metadata[filename] = document.info

    # def print(self):
    #     parser = PDFParser(self.fp)
    #     document = PDFDocument(parser, password="")
    #
    #     # Get the outlines of the document.
    #     metadata = document.info
    #     print(metadata)

    # def meta_title(file):
    #     """Title from pdf metadata.
    #     """
    #     try:
    #         docinfo = PdfFileReader(file).getDocumentInfo()
    #         return docinfo.title if docinfo.title else ""
    #     except PdfReadError:
    #         return ""


if __name__ == '__main__':
    pp = PaperParser("static/papers")
    pp.extract_content()
    pp.make_dict()
    pp.make_vectors()
    # pp = load_articles("papers.pkl")
    pp.make_idf()
    pp.save("papers.pkl")
