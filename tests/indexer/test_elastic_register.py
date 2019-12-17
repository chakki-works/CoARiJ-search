import os
import time
import shutil
import unittest
import docker
import requests
from indexer.downloader import Downloader
from indexer.report_reader import ReportReader
from indexer.elastic_register import ElasticRegister


class TestElasticsearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        root = os.path.join(os.path.dirname(__file__), "../data")
        d = Downloader(root)
        cls.taxonomy_path = d.download_taxonomy()

        cls.docker = docker.from_env()
        cls._container = cls.docker.containers.run(
                    "docker.elastic.co/elasticsearch/elasticsearch:7.5.0",
                    ports={
                        "9200/tcp": "9200",
                        "9300/tcp": "9300"
                    },
                    environment={
                        "discovery.type": "single-node"
                    }, remove=True, detach=True)
        time.sleep(20)

    @classmethod
    def tearDownClass(cls):
        cls._container.stop()
        if cls.taxonomy_path:
            shutil.rmtree(cls.taxonomy_path)

    @property
    def xblr_test_file(self):
        return os.path.join(os.path.dirname(__file__), "../data/example.xbrl")

    @property
    def index_test_file(self):
        return os.path.join(os.path.dirname(__file__), "../data/index.json")

    def test_create_index(self):
        elr = ElasticRegister("localhost:9200")
        elr.create_index("example", self.index_test_file, drop=True)
        elr.drop_index("example")

    def test_register_document(self):
        elr = ElasticRegister("localhost:9200")
        elr.create_index("example2", self.index_test_file, drop=True)
        r = ReportReader(self.xblr_test_file, self.taxonomy_path)
        result = elr.register_xbrl("example2", r)
        print(result)
        count = elr.client.count(index="example2")
        print(count)
        self.assertGreater(count["count"], 0)
        elr.drop_index("example2")
