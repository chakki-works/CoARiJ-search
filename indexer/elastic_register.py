from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticRegister():

    def __init__(self, host_and_port=""):
        if not host_and_port:
            self.client = Elasticsearch()
        else:
            self.client = Elasticsearch([host_and_port])

    def create_index(self, index, index_file, drop=False):
        if drop:
            self.drop_index(index)

        with open(index_file, encoding="utf-8") as f:
            source = f.read().strip()
            self.client.indices.create(index=index, body=source)

    def drop_index(self, index):
        return self.client.indices.delete(index=index, ignore=[404])

    def register_xbrl(self, index, reader):
        items = reader.read_report()
        docs = []
        for r in items:
            doc = {}
            doc["_op_type"] = "index"
            doc["_index"] = index
            for k in r.json:
                doc[k] = r.json[k]

        result = bulk(self.client, docs)
        return result
