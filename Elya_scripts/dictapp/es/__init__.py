from elasticsearch import Elasticsearch, exceptions
from vd.settings import ELASTIC_PORT, MAPPING_FILE
import json
import requests


with open(MAPPING_FILE, 'r', encoding='utf-8') as m:
    MAPPING = m.read()


class ESClient(object):
    def __init__(self):
        self.es = Elasticsearch(port=ELASTIC_PORT)
        self.es.indices.create(index='vd', ignore=400, body=MAPPING)
        total = self.get_all()['total']
        self.indices = {"vd": total}

    def create(self, doc):
        self.indices["vd"] += 1
        res = self.es.index(index="vd", doc_type='entry', id=self.indices["vd"], body=doc)
        self.es.indices.refresh(index="vd")
        return res['created']

    def get_by_id(self, id):
        try:
            doc = self.es.get(index="vd", doc_type='entry', id=id)
            return doc
        except exceptions.NotFoundError:
            return []

    def get_all(self):
        res = self.es.search(index="vd", body={"query": {"match_all": {}}})
        return res['hits']

    def get_by_query(self, query):
        res = self.es.search(index="vd", doc_type="entry", body={"query": query})
        return res['hits']

    def search_query(self, query):
        data = requests.get('http://127.0.0.1:5000/vd/_search?q='+query)
        data = json.loads(data.text)
        return data['hits']

    def delete_by_id(self, id):
        try:
            self.es.delete(index="vd", doc_type='entry', id=id)
        except exceptions.NotFoundError:
            return []


if __name__ == "__main__":
    es = ESClient()
    es.create(json.dumps(1))
