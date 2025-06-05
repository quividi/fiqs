import json
import os
import time

import pytest
from elasticsearch.helpers import bulk
from elasticsearch.dsl import Mapping, Nested

from fiqs.testing.utils import get_client

SALE_INDEX_NAME = "test_sale"
TRAFFIC_INDEX_NAME = "test_traffic"

SALE_FIXTURE_PATH = "fiqs/testing/fixtures/shop_fixture.json"
TRAFFIC_FIXTURE_PATH = "fiqs/testing/fixtures/traffic_fixture.json"


def sale_mapping():
    m = Mapping()

    m.meta("dynamic", "strict")

    m.field("id", "integer")
    m.field("shop_id", "integer")
    m.field("client_id", "keyword")
    m.field("timestamp", "date")
    m.field("price", "integer")
    m.field("payment_type", "keyword")

    products = Nested(
        properties={
            "product_id": "keyword",
            "product_type": "keyword",
            "product_price": "integer",
            "parts": Nested(
                properties={
                    "part_id": "keyword",
                    "warehouse_id": "keyword",
                    "part_price": "integer",
                }
            ),
        }
    )
    m.field("products", products)

    return m


def traffic_mapping():
    m = Mapping()

    m.meta("dynamic", "strict")

    m.field("id", "integer")
    m.field("shop_id", "integer")
    m.field("timestamp", "date")
    m.field("duration", "integer")
    m.field("incoming_traffic", "integer")
    m.field("outgoing_traffic", "integer")

    return m


def create_index(client, index_name, mapping):
    request_body = {"mappings": mapping.to_dict()}
    return client.options(ignore_status=400).indices.create(
        index=index_name, body=request_body
    )


def delete_index(client, index_name):
    return client.indices.delete(index=index_name)


def insert_documents(client, index_name, fixture_path):
    with open(fixture_path) as f:
        lines = f.readlines()

    events = [json.loads(line) for line in lines]

    actions = []
    for event in events:
        actions.append(
            {
                "_index": index_name,
                "_source": event,
                "_id": event["id"],
            }
        )

    return bulk(client, actions)


def insert_sale_documents(client):
    create_sale_index(client)
    insert_documents(client, SALE_INDEX_NAME, SALE_FIXTURE_PATH)


def insert_traffic_documents(client):
    create_traffic_index(client)
    insert_documents(client, TRAFFIC_INDEX_NAME, TRAFFIC_FIXTURE_PATH)


def create_sale_index(client):
    create_index(client, SALE_INDEX_NAME, sale_mapping())


def create_traffic_index(client):
    create_index(client, TRAFFIC_INDEX_NAME, traffic_mapping())


def delete_sale_index(client):
    delete_index(client, SALE_INDEX_NAME)


def delete_traffic_index(client):
    delete_index(client, TRAFFIC_INDEX_NAME)


@pytest.fixture(scope="session")
def elasticsearch_sale(request):
    client = get_client()
    insert_sale_documents(client)

    request.addfinalizer(lambda: delete_sale_index(client))
    time.sleep(1)

    return client


@pytest.fixture(scope="session")
def elasticsearch_traffic(request):
    client = get_client()
    insert_traffic_documents(client)

    request.addfinalizer(lambda: delete_traffic_index(client))
    time.sleep(1)

    return client


BASE_PATH = "fiqs/testing/outputs/"


def write_output(search, name):
    result = search.execute()

    path = os.path.join(BASE_PATH, f"{name}.json")
    with open(path, "w") as f:
        d = result._d_
        d.pop("took", None)  # Not used and may change between calls

        json.dump(
            result._d_,
            f,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )


def write_fquery_output(fquery, name):
    result = fquery.eval(flat=False)

    path = os.path.join(BASE_PATH, f"{name}.json")
    with open(path, "w") as f:
        d = result._d_
        d.pop("took", None)  # Not used and may change between calls

        json.dump(
            result._d_,
            f,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
        )


def load_output(name):
    path = os.path.join(BASE_PATH, f"{name}.json")

    with open(path) as f:
        output = json.load(f)

    return output
