import numpy as np
from elasticsearch import Elasticsearch
import requests
from elasticsearch.helpers import bulk
from indexer.report_reader import ReportReader


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

    def register_xbrl(self, index, reader,
                      embedding_host="", aggregation="mean"):
        items = reader.read_report()
        actions = []
        for r in items:
            j = r.json
            if embedding_host and r.text_value:
                payload = {
                    "q": j["value"],
                    "lang": "ja"
                }
                proxies = None
                if "localhost" in embedding_host:
                    proxies = {"http": None, "https": None}

                resp = requests.post(embedding_host + "/vectorize",
                                     data=payload, proxies=proxies)
                resp = resp.json()
                if "embedding" in resp:
                    embedding = np.array(resp["embedding"])
                    print(embedding.shape)
                    if aggregation == "mean":
                        embedding = np.mean(embedding, axis=0)
                    elif aggregation == "max":
                        embedding = np.max(embedding, axis=0)
                    elif aggregation == "sum":
                        embedding = np.sum(embedding, axis=0)

                    j["vector"] = embedding.tolist()

            action = {
                "_op_type": "index",
                "_index": index,
                "_source": r.json
            }
            actions.append(action)

        result = bulk(self.client, actions)
        return result
