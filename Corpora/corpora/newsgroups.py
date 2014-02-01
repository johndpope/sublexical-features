from abc import ABCMeta
from collections import Sequence
from glob import glob
import os

from numpy import ndarray

from experiments.preprocessing import mahoney_clean


data_path = '/Users/stinky/Work/data'
newsgroups_corpus_path = os.path.join(data_path, '20_newsgroups')

article_count = 19997
topic_count = {
    'rec.motorcycles': 1000,
    'comp.sys.mac.hardware': 1000,
    'talk.politics.misc': 1000,
    'soc.religion.christian': 997,
    'comp.graphics': 1000,
    'sci.med': 1000,
    'talk.religion.misc': 1000,
    'comp.windows.x': 1000,
    'comp.sys.ibm.pc.hardware': 1000,
    'talk.politics.guns': 1000,
    'alt.atheism': 1000,
    'comp.os.ms-windows.misc': 1000,
    'sci.crypt': 1000, 'sci.space': 1000,
    'misc.forsale': 1000,
    'rec.sport.hockey': 1000,
    'rec.sport.baseball': 1000,
    'sci.electronics': 1000,
    'rec.autos': 1000,
    'talk.politics.mideast': 1000
}

num_topics = 20
topics = ['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc', 'comp.sys.ibm.pc.hardware',
          'comp.sys.mac.hardware', 'comp.windows.x', 'misc.forsale', 'rec.autos',
          'rec.motorcycles', 'rec.sport.baseball', 'rec.sport.hockey', 'sci.crypt',
          'sci.electronics', 'sci.med', 'sci.space', 'soc.religion.christian',
          'talk.politics.guns', 'talk.politics.mideast', 'talk.politics.misc', 'talk.religion.misc']


def parse_fn(fn):
    with open(fn) as f:
        data = f.read()
        body = data[data.find('\n\n'):data.find('\n-- \n')]

    return body


def parse_articles(corpus_path, include_body=True):
    for path in glob(os.path.join(corpus_path, '*')):
        group = os.path.basename(path)

        for fn in glob(os.path.join(path, '*')):
            if include_body:
                body = parse_fn(fn)
            else:
                body = None

            yield {'id': int(os.path.basename(fn)),
                   'group': group,
                   'body': body}


def _build_article_index(corpus_path):
    index = [None] * article_count

    for i, art in enumerate(parse_articles(corpus_path, include_body=False)):
        index[i] = (art['id'], art['group'])

    return index


class NewsgroupsSequence(Sequence):
    __metaclass__ = ABCMeta

    def __init__(self, corpus_path, indices=None):
        self.article_index = _build_article_index(corpus_path)
        self.corpus_path = corpus_path
        self.indices = indices

    def __len__(self):
        if type(self.indices) in [ndarray, list]:
            return len(self.indices)
        else:
            return article_count


def check_index(f):
    def _check_index(self, index):
        if type(self.indices) in [ndarray, list]:
            index = self.indices[index]

        return f(self, index)

    return _check_index


class GroupSequence(NewsgroupsSequence):
    @check_index
    def __getitem__(self, index):
        return self.article_index[index][1]


class ArticleSequence(NewsgroupsSequence):
    @check_index
    def __getitem__(self, index):
        art_id, group = self.article_index[index]
        body = parse_fn(os.path.join(self.corpus_path, group, str(art_id)))

        return unicode(mahoney_clean(body))