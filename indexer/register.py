import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from indexer.downloader import Downloader
from indexer.report_reader import ReportReader
from indexer.elastic_register import ElasticRegister


def register_docs(elastic_host, embedding_host,
                  data_root, index_file,
                  max_docs=-1):

    if not os.path.exists(data_root):
        os.mkdir(data_root)
    index_name = "reports"

    d = Downloader(data_root)
    data_path = d.download_data()
    taxonomy_path = d.download_taxonomy()

    elr = ElasticRegister(elastic_host)
    elr.create_index(index_name, index_file, drop=True)

    count = 0
    for i, f in enumerate(os.listdir(data_path)):
        if not f.endswith(".xbrl"):
            continue
        if max_docs > 0 and i > max_docs:
            break

        p = os.path.join(data_path, f)
        r = ReportReader(p, taxonomy_path)

        success, error = elr.register_xbrl(index_name, r, embedding_host)
        print(f"Register {f}.")
        count += 1

    print(f"Register {count} documents")


if __name__ == "__main__":
    default_index_file = os.path.join(
                            os.path.dirname(__file__), "./index.json")
    default_data_root = os.path.join(
                            os.path.dirname(__file__), "../data")

    register_docs(elastic_host="localhost:9200",
                  embedding_host="localhost:8080",
                  data_root=default_data_root,
                  index_file=default_index_file,
                  max_docs=10)
