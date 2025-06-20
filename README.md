fiqs
====

[![Build Status](https://travis-ci.org/pmourlanne/fiqs.svg?branch=master)](https://travis-ci.org/pmourlanne/fiqs)

fiqs is an opinionated high-level library whose goal is to help you write concise queries
agains Elasticsearch and better consume the results. It is built on top of the awesome [Elasticsearch](<https://github.com/elastic/elasticsearch-py>) library.

fiqs exposes a ``flatten_result`` function which transforms an elasticsearch.dsl ``Result``, or a dictionary, into the list of its nodes.
fiqs also lets you create Model classes, a la Django, which automatically generates an Elasticsearch mapping.
Finally fiqs exposes a ``FQuery`` objects which, leveraging your models, lets you write less verbose queries against Elasticsearch.


Compatibility
-------------

fiqs is compatible with Elasticsearch 9.X and works with Python3


Documentation
-------------

Documentation is available at https://fiqs.readthedocs.io/


Code example
------------

You define a model, matching what is in your Elasticsearch cluster:

```python
    from fiqs import models

    class Sale(models.Model):
        index = 'sale_data'
        doc_type = 'sale'

        id = fields.IntegerField()
        shop_id = fields.IntegerField()
        client_id = fields.KeywordField()

        timestamp = fields.DateField()
        price = fields.IntegerField()
        payment_type = fields.KeywordField(choices=['wire_transfer', 'cash', 'store_credit'])
```


You can then write clean queries:

```python
    from elasticsearch.dsl import Search
    from fiqs.aggregations import Sum
    from fiqs.query import FQuery

    from .models import Sale

    search = Search(...)
    metric = FQuery(search).values(
        total_sales=Sum(Sale.price),
    ).group_by(
        Sale.shop_id,
        Sale.client_id,
    )
    result = metric.eval()
```


And let fiqs organise the results:

```python
    print(result)
    # [
    #     {
    #         "shop_id": 1,
    #         "client_id": 1,
    #         "doc_count": 30,
    #         "total_sales": 12345.0,
    #     },
    #     {
    #         "shop_id": 2,
    #         "client_id": 1,
    #         "doc_count": 20,
    #         "total_sales": 23456.0,
    #     },
    #     {
    #         "shop_id": 3,
    #         "client_id": 1,
    #         "doc_count": 10,
    #         "total_sales": 34567.0,
    #     },
    #     [...]
    # ]
```


Contributing
------------

The fiqs project is hosted on [Github](<https://github.com/pmourlanne/fiqs>)

To run the tests on your machine use this command: ``python setup.py test`` Some tests are used to generate results output from Elasticsearch. To run them you will need to run a docker container on your machine: ``docker run -d -p 8200:9200 -p 8300:9300 docker.elastic.co/elasticsearch/elasticsearch:9.x.x`` and then run ``pytest -k docker``.


License
-------

See attached LICENSE file.
