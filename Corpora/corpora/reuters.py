import csv
from glob import glob
import logging
import os

from BeautifulSoup import BeautifulSoup


corpus_path = '/Users/stinky/Work/data/reuters21578'


def corpus_fns(corpus_path):
    return glob(os.path.join(corpus_path, '*.sgm'))


def parse_corpus_fn(fn):
    with open(fn) as f:
        doc = BeautifulSoup(f)

        for tag in doc.findAll('reuters'):
            content = {}

            content['id'] = int(tag['newid'])
            content['oldid'] = int(tag['oldid'])
            content['has_topics'] = tag['topics']
            content['lewissplit'] = tag['lewissplit']
            content['cgisplit'] = tag['cgisplit']

            content['date_str'] = tag.date.text
            content['topics'] = [topic.text for topic in tag.topics.findAll('d')]
            content['places'] = [place.text for place in tag.places.findAll('d')]
            content['people'] = [person.text for person in tag.people.findAll('d')]
            content['orgs'] = [org.text for org in tag.orgs.findAll('d')]
            content['exchanges'] = [exchange.text for exchange in tag.exchanges.findAll('d')]
            content['companies'] = [company.text for company in tag.companies.findAll('d')]

            if tag.unknown:
                content['unknown'] = tag.unknown.text

            text_tag = tag.find('text')

            if not text_tag.body:
                logging.warn("Missing body for id %d in %s" % (content['id'], fn))
                continue

            content['title'] = text_tag.title.text
            content['dateline'] = text_tag.dateline.text
            content['body'] = text_tag.body.text

            yield content


def corpus_articles(corpus_path):
    for fn in corpus_fns(corpus_path):
        for article in parse_corpus_fn(fn):
            yield article


def corpus_to_csv(corpus_path, csv_fn):
    field_names = ['new_id', 'date_str', 'topics', 'places', 'peoples', 'orgs', 'exchanges',
                   'companies', 'title', 'text']

    with open(csv_fn, 'wb') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL,
                            fieldnames=field_names)

        for fn in corpus_fns(corpus_path):
            for article in parse_corpus_fn(fn):
                row = [article['id'], article['date_str'], '|'.join(article['topics']), '|'.join(article['places']),
                       '|'.join(article['people']), '|'.join(article['orgs']), '|'.join(article['exchanges']),
                       '|'.join(article['companies']), article['title'], article['body']]

                writer.writerow(row)