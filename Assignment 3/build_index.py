# -*- coding: UTF-8 -*-

import os
from bs4 import BeautifulSoup
from jieba.analyse import ChineseAnalyzer
from whoosh.index import create_in
from whoosh.fields import *
from urllib.parse import urljoin
import time
from collections import defaultdict
import numpy as np
from scipy.sparse import csr_matrix
import json


class LinkAnalyzer(object):

    def __init__(self):
        self.row_cnt = 0
        self.col_cnt = 0
        self.row = []
        self.col = []
        self.data = []
        self.href_cnt = 0
        self.anchor = defaultdict(list)
        self.href = dict()
        self.pr_matrix = None
        self.pr_vector = None

    def save_state(self):
        root_dir = "./link/"
        if not os.path.exists(root_dir):
            os.mkdir(root_dir)
        with open(os.path.join(root_dir, "anchor.json"), 'w') as f:
            json.dump(self.anchor, f)
        with open(os.path.join(root_dir, "href.json"), 'w') as f:
            json.dump(self.href, f)
        with open(os.path.join(root_dir, "pr_vector.json"), 'w') as f:
            json.dump(self.pr_vector.tolist(), f)

    def clear_temp(self):
        self.col = None
        self.row = None
        self.data = None

    def load_state(self):
        root_dir = "./link/"
        assert os.path.exists(root_dir)
        with open(os.path.join(root_dir, "anchor.json"), 'r') as f:
            self.anchor = dict(json.load(f))
        with open(os.path.join(root_dir, "href.json"), 'r') as f:
            self.href = dict(json.load(f))
        with open(os.path.join(root_dir, "pr_vector.json"), 'r') as f:
            self.pr_vector = np.array(json.load(f))

    def add_anchor_text(self, full_href, anchor_text):
        self.anchor[self.href[full_href]].append(anchor_text)

    def add_href(self, full_href):
        if full_href not in self.href:
            self.href[full_href] = self.href_cnt
            self.href_cnt += 1

    def set_row(self, full_href):
        self.row_cnt = self.href[full_href]

    def add_col(self, full_href):
        if self.row_cnt != self.href[full_href]:
            self.row.append(self.row_cnt)
            self.col.append(self.href[full_href])
            self.col_cnt += 1

    def add_row(self):
        if self.col_cnt > 0:
            self.data.extend([1 / self.col_cnt] * self.col_cnt)
            self.col_cnt = 0

    def make_pg_matrix(self):
        self.pr_matrix = csr_matrix((self.data, (self.row, self.col)), dtype=np.float32, shape=(self.href_cnt, self.href_cnt))
        self.pr_matrix = self.pr_matrix.transpose()

    def compute_pr(self, p=0.85):
        process = 0
        pr = np.ones((self.href_cnt, 1), dtype=np.float32) * (1 / self.href_cnt)
        pr_ = p * self.pr_matrix.dot(pr) + (1 - p) * (1 / self.href_cnt)
        while not np.isclose(pr, pr_).all():
            pr = pr_
            pr_ = p * self.pr_matrix.dot(pr) + (1 - p) * (1 / self.href_cnt)
            process += 1
        self.pr_vector = pr_
        print("item num: %d" % len(self.data))
        print("dimension: %d" % self.href_cnt)
        print("iteration num: %d" % process)
        self.clear_temp()

    def get_pr(self, full_href):
        return self.pr_vector[self.href[full_href]][0]

    def get_anchor(self, full_href):
        anchor_str = ' '.join(self.anchor[self.href[full_href]])
        return anchor_str


class Indexer(object):

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.prefix_len = len(self.root_dir)
        analyzer = ChineseAnalyzer()
        self.schema = Schema(
            title=ID(stored=True),
            url=ID(stored=True),
            content=TEXT(stored=True, analyzer=analyzer, field_boost=1.0),
            type=ID(stored=True),
            anchor=TEXT(stored=True, analyzer=analyzer, field_boost=3.0, phrase=False),
            page_rank=NUMERIC(stored=True, numtype=float, bits=32),
            extension=ID(stored=True)
        )
        self.img_pattern = re.compile(r'.+\.jpg|.+\.png|.+\.gif|.+\.bmp|.+\.jpeg', re.I)
        self.doc_pattern = re.compile(r'.+\.pdf|.+\.doc|.+\.docx|.+\.xls|.+\.xlsx|.+\.ppt|.+\.pptx|.+\.txt', re.I)
        self.file_pattern = re.compile(r'.+\.rar|.+\.mp4|.+\.mp3|.+\.zip|.+\.tar|.+\.gz|.+\.7z', re.I)
        self.unresolvable_pattern = re.compile(r'.+\.js|.+\.css', re.I)
        self.website_cnt = 0
        self.link_analyzer = LinkAnalyzer()
        self.ix = None
        self.writer = None
        self.time = None

    def init_indexer(self):
        if not os.path.exists("index"):
            os.mkdir("index")
        self.ix = create_in("index", self.schema)
        self.writer = self.ix.writer()

    def get_delta_time(self):
        delta = time.time() - self.time
        self.time = time.time()
        return delta

    def preprocess(self):
        self.init_indexer()
        g = os.walk(self.root_dir)
        for path, d, filelist in g:
            for filename in filelist:
                self._preprocess(path, filename)
        print("Anchor Done:", self.get_delta_time())
        self.link_analyzer.make_pg_matrix()
        self.link_analyzer.compute_pr()
        print("Page Rank Done:", self.get_delta_time())
        self.link_analyzer.save_state()
        self.website_cnt = 0

    def _preprocess(self, path, filename):
        full_path = os.path.join(path, filename)
        url = "%s%s" % ("http://", full_path[self.prefix_len:])
        noext_name, ext = os.path.splitext(filename)
        if len(ext) > 0:
            ext = ext[1:]
        if self.img_pattern.match(filename):
            self.writer.add_document(content=noext_name, url=url, type=u"image", extension=ext)
            os.remove(full_path)
        elif self.doc_pattern.match(filename):
            self.writer.add_document(content=noext_name, url=url, type=u"document", extension=ext)
            os.remove(full_path)
        elif self.file_pattern.match(filename):
            self.writer.add_document(content=noext_name, url=url, type=u"file", extension=ext)
            os.remove(full_path)
        elif self.unresolvable_pattern.match(filename):
            os.remove(full_path)
            pass
        else:
            with open(full_path, 'rb') as f:
                try:
                    soup = BeautifulSoup(f.read(), "lxml")
                    if not soup.title:
                        raise NameError('no title found')

                    # add myself to href counter
                    self.link_analyzer.add_href(url)
                    self.link_analyzer.set_row(url)

                    for href in soup.find_all('a', href=re.compile(r'(/|\./|http|www).*')):
                        if href.attrs['href'] is not None:
                            anchor_text = href.get_text(strip=True)
                            if anchor_text and len(anchor_text) > 0:
                                full_href = urljoin(url, href.attrs['href'])

                                # add it to href counter
                                self.link_analyzer.add_href(full_href)
                                # append text to anchor
                                self.link_analyzer.add_anchor_text(full_href, anchor_text)
                                # build the page rank matrix
                                self.link_analyzer.add_col(full_href)

                    # add a normalized row to matrix
                    self.link_analyzer.add_row()

                    if self.website_cnt % 500 == 0:
                        print(self.website_cnt, path)
                    self.website_cnt += 1

                except NameError as e:
                    print('\x1b[6;30;42m%s:\x1b[0m' % e, url)
                    os.remove(full_path)

                except Exception as e:
                    print('\x1b[6;30;42m%s:\x1b[0m' % type(e), url)
                    os.remove(full_path)

    def make_document(self, path, filename):
        full_path = os.path.join(path, filename)
        url = "%s%s" % ("http://", full_path[self.prefix_len:])
        _, ext = os.path.splitext(filename)
        if len(ext) > 0:
            ext = ext[1:]
        with open(full_path, 'rb') as f:
            try:
                soup = BeautifulSoup(f.read(), "lxml")
                if not soup.title:
                    raise NameError('no title found')

                title = soup.title.get_text(strip=True)
                content_list = [raw_text.get_text(' ', strip=True) for raw_text in soup.find_all(['p', 'a', 'title'])]
                content = ' '.join(content_list)
                self.writer.add_document(
                    title=title,
                    url=url,
                    content=content,
                    type=u"website",
                    anchor=self.link_analyzer.get_anchor(url),
                    page_rank=self.link_analyzer.get_pr(url),
                    extension=ext
                )
                if self.website_cnt % 500 == 0:
                    print(self.website_cnt, path)
                self.website_cnt += 1
            except Exception as e:
                print('\x1b[6;30;42m%s:\x1b[0m' % type(e), url)
                os.remove(full_path)

    def make_indexer(self):
        self.time = time.time()
        self.preprocess()
        g = os.walk(self.root_dir)
        for path, d, filelist in g:
            for filename in filelist:
                self.make_document(path, filename)
        print("total websites: %d" % self.website_cnt)
        self.writer.commit()
        print("Index Done:", self.get_delta_time())

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
    idx = Indexer(u"./template/cache/")
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
