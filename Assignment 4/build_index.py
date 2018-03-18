# -*- coding: UTF-8 -*-

import os
from whoosh.index import create_in
from whoosh.fields import *
import time
import xlrd


class Indexer(object):

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.schema = Schema(
            word=ID(stored=True),
            translation=ID(stored=True),
            level=ID(stored=True),
        )
        self.ix = None
        self.writer = None
        self.time = None
        self.word_cnt = 0

    def init_indexer(self):
        if not os.path.exists("index"):
            os.mkdir("index")
        self.ix = create_in("index", self.schema)
        self.writer = self.ix.writer()

    def get_delta_time(self):
        delta = time.time() - self.time
        self.time = time.time()
        return delta

    def _make_indexer(self, filename):
        data = xlrd.open_workbook(os.path.join(self.root_dir, filename))
        table = data.sheets()[0]
        if filename.startswith("gre"):
            level = "gre"
        elif filename.startswith("toefl"):
            level = "toefl"
        else:
            level = "unknown"
        for i in range(table.nrows):
            translation = table.row_values(i)[1]
            translation = translation.split('\n')
            translation = " ".join(translation)
            self.writer.add_document(
                word=table.row_values(i)[0].lower(),
                translation=translation,
                level=level,
            )
            self.word_cnt += 1

    def make_indexer(self):
        self.init_indexer()
        self.time = time.time()
        self._make_indexer("gre.xls")
        self._make_indexer("toefl.xls")
        print("total words: %d" % self.word_cnt)
        self.writer.commit()
        print("Index Done In:", self.get_delta_time())

# def test():
#     g = os.walk("./resource/cc.nankai.edu.cn/")
#     for path, d, filelist in g:
#         for filename in filelist:
#             dir = os.path.join(path, filename)
#             with open(dir, 'rb') as f:
#                 url = dir[len("./resource/"):]
#                 url = "%s%s" % ('http://', url)
#                 soup = BeautifulSoup(f.read(), "lxml")
#                 for p in soup.find_all('a', href=re.compile(r'(/|\./|http|www).*')):
#                     if p.attrs['href'] is not None:
#                         anchor_text = p.get_text(strip=True)
#                         if anchor_text and len(anchor_text) > 0:
#                             print(urlsplit(urljoin(url, p.attrs['href'])).geturl())
#                             print(anchor_text)
        # for p in soup.find_all(['p', 'a', 'title']):
        #     text = p.get_text(' ', strip=True)
        #     if len(text) != 0:
        #         print(text)


if __name__ == '__main__':
    idx = Indexer("./dicts")
    idx.make_indexer()
    # idx.link_analyzer.load_state()
    # print(np.max(idx.link_analyzer.pr_vector))
    # idx.make_anchor()
    # test()
    # la = LinkAnalyzer()
    # la.href_cnt = 7
    # la.row = [
    #     0, 0, 0, 0, 0,
    #     1,
    #     2, 2,
    #     3, 3, 3,
    #     4, 4, 4, 4,
    #     5, 5,
    #     6]
    #
    # la.col = [
    #     1, 2, 3, 4, 6,
    #     0,
    #     0, 1,
    #     1, 2, 4,
    #     0, 2, 3, 5,
    #     0, 4,
    #     4]
    #
    # la.data = [
    #     1 / 5, 1 / 5, 1 / 5, 1 / 5, 1 / 5,
    #     1,
    #     1 / 2, 1 / 2,
    #     1 / 3, 1 / 3, 1 / 3,
    #     1 / 4, 1 / 4, 1 / 4, 1 / 4,
    #     1 / 2, 1 / 2,
    #     1]
    #
    # la.make_pg_matrix()
    # la.compute_pr()
    # print(la.pr_vector)
    # la.save_state()
    # la.load_state()
    # print(la.pr_vector)
