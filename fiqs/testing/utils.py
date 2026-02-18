import os

from elasticsearch import Elasticsearch
from elasticsearch.dsl import Search

FIQS_ES_URL = os.environ.get("FIQS_ES_URL", "http://localhost:9201")


def get_client():
    return Elasticsearch([FIQS_ES_URL], request_timeout=60)


def get_search(client=None, indices=None):
    indices = indices or "*"
    client = client or get_client()
    return Search(using=client, index=indices)
