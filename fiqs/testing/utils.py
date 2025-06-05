from elasticsearch import Elasticsearch
from elasticsearch.dsl import Search


def get_client():
    return Elasticsearch(["http://localhost:8200"], request_timeout=60)


def get_search(client=None, indices=None):
    indices = indices or "*"
    client = client or get_client()
    return Search(using=client, index=indices)
