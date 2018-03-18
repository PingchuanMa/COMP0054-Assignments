# -*- coding: UTF-8 -*-

from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh.qparser import EveryPlugin
from whoosh.query import *
from urllib.parse import urlparse
from whoosh.index import open_dir
from build_index import Indexer
from whoosh import scoring
import numpy as np
import datetime

class TFIDF_PR(scoring.WeightingModel):
    use_final = True
    def scorer(self, searcher, fieldname, text, qf=1):
        # IDF is a global statistic, so get it from the top-level searcher
        parent = searcher.get_parent()  # Returns self if no parent
        idf = parent.idf(fieldname, text)
        maxweight = searcher.term_info(fieldname, text).max_weight()
        return TF_IDFScorer(maxweight, idf)
    def final(self, searcher, docnum, score):
        try:
            return score * searcher.stored_fields(docnum)['page_rank']
        except KeyError:
            return score


class TF_IDFScorer(scoring.BaseScorer):
    def __init__(self, maxweight, idf):
        self._maxquality = maxweight * idf
        self.idf = idf

    def supports_block_quality(self):
        return True

    def score(self, matcher):
        return matcher.weight() * self.idf

    def max_quality(self):
        return self._maxquality

    def block_quality(self, matcher):
        return matcher.block_max_weight() * self.idf

class Query(object):

    def __init__(self, index_name):
        self.index_name = index_name
        self.ix = open_dir(index_name)
        self.indexer = Indexer("./template/cache/")
        self.multiParser = MultifieldParser(["anchor", "content"], schema=self.indexer.schema)
        self.singleParser = QueryParser("content", schema=self.indexer.schema)
        self.site_re = re.compile(r'site:')
        self.filetype_re = re.compile(r'filetype:')
        self.type2fn = {
            "website": self.query_website,
            "image": self.query_image,
            "file": self.query_file,
            "document": self.query_document,
            "all": self.query_all,
        }
        self.searcher = self.ix.searcher(weighting=TFIDF_PR)
        self.singleParser.add_plugin(EveryPlugin)
        self.multiParser.add_plugin(EveryPlugin)


    def query_website(self, sentence, page, filetype=None, site=None):
        query = And([self.multiParser.parse(sentence), Term("type", "website")])
        if filetype:
            query = And([query, Term("extension", filetype)])
        if site:
            query = And([query, Prefix("url", site)])
        results = self.searcher.search_page(query, page, terms=True)
        return results

    def query_image(self, sentence, page, filetype=None, site=None):
        query = And([self.singleParser.parse(sentence), Term("type", "image")])
        if filetype:
            query = And([query, Term("extension", filetype)])
        if site:
            query = And([query, Prefix("url", site)])
        results = self.searcher.search_page(query, page, terms=True)
        return results

    def query_file(self, sentence, page, filetype=None, site=None):
        query = And([self.singleParser.parse(sentence), Term("type", "file")])
        if filetype:
            query = And([query, Term("extension", filetype)])
        if site:
            query = And([query, Prefix("url", site)])
        results = self.searcher.search_page(query, page, terms=True)
        return results

    def query_document(self, sentence, page, filetype=None, site=None):
        query = And([self.singleParser.parse(sentence), Term("type", "document")])
        if filetype:
            query = And([query, Term("extension", filetype)])
        if site:
            query = And([query, Prefix("url", site)])
        results = self.searcher.search_page(query, page, terms=True)
        return results

    def query_all(self, sentence, page, filetype=None, site=None):
        query = self.multiParser.parse(sentence)
        if filetype:
            query = And([query, Term("extension", filetype)])
        if site:
            query = And([query, Prefix("url", site)])
        results = self.searcher.search_page(query, page, terms=True)
        return results

    def query(self, sentence, target, page):
        site = None
        filetype = None
        self.log(sentence)
        if self.site_re.match(sentence):
            sentence = sentence[5:].strip()
            site = sentence.split(' ')[0]
            sentence = sentence[len(site):].strip()
            if len(urlparse(site)[0]) == 0:
                site = "%s%s" % ("http://", site)
        elif self.filetype_re.match(sentence):
            sentence = sentence[9:].strip()
            filetype = sentence.split(' ')[0]
            sentence = sentence[len(filetype):].strip()

        return self.type2fn[target](sentence, page, filetype, site)

    def log(self, sentence):
        with open('logging.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime("%y%m%d%H%M%S") + " " + sentence)

if __name__ == '__main__':
    q = Query('index')
    for r in q.query("化学 AND 生物", "website", 1):
        for field, keyword in r.matched_terms():
            if field == 'content':
                print(keyword.decode('utf-8'))
