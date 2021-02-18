# -*- coding: utf-8 -*-

import copy

import pytest

from fiqs import fields
from fiqs.exceptions import FieldError
from fiqs.models import Model
from fiqs.testing.models import (
    Sale,
    SaleWithoutProducts,
    SaleWithParts,
    SaleWithProducts,
    SaleWithSubParts,
)

EXPECTED_MAPPING = {
    'dynamic': 'strict',
    'properties': {
        'id': {'type': 'integer'},
        'shop_id': {'type': 'integer'},
        'client_id': {'type': 'keyword'},
        'timestamp': {'type': 'date'},
        'price': {'type': 'integer'},
        'payment_type': {'type': 'keyword'},
        'products': {
            'properties': {
                'product_id': {'type': 'keyword'},
                'product_price': {'type': 'integer'},
                'product_type': {'type': 'keyword'},
                'parts': {
                    'properties': {
                        'part_id': {'type': 'keyword'},
                        'warehouse_id': {'type': 'keyword'},
                        'part_price': {'type': 'integer'},
                    },
                    'type': 'nested',
                },
            },
            'type': 'nested',
        },
    },
}


def test_mapping_from_model():
    assert Sale.get_mapping().to_dict() == EXPECTED_MAPPING


def test_mapping_from_model_nested_three_levels():
    mapping_with_subparts = copy.deepcopy(EXPECTED_MAPPING)

    subparts_properties = {
        'properties': {
            'subpart_id': {'type': 'keyword'},
        },
        'type': 'nested',
    }
    mapping_with_subparts['properties']['products']['properties'][
        'parts']['properties']['subparts'] = subparts_properties

    assert SaleWithSubParts.get_mapping().to_dict() == mapping_with_subparts


def test_mapping_from_model_child_class():
    mapping_without_parts = copy.deepcopy(EXPECTED_MAPPING)
    mapping_without_parts['properties']['products']['properties'].pop('parts')
    assert SaleWithProducts.get_mapping().to_dict() == mapping_without_parts

    mapping_with_parts = copy.deepcopy(EXPECTED_MAPPING)
    assert SaleWithParts.get_mapping().to_dict() == mapping_with_parts


def test_child_class_redefines_parents_field():
    with pytest.raises(FieldError):
        class Parent(Model):
            field = fields.IntegerField()

        class Child(Parent):
            field = fields.IntegerField()


def test_field_model_access_child():
    assert SaleWithoutProducts.price.model == SaleWithoutProducts
    assert SaleWithProducts.price.model == SaleWithProducts
    assert SaleWithParts.price.model == SaleWithParts
