# -*- coding: utf-8 -*-

import copy


class Field(object):
    def __init__(self, type, key=None, verbose_name=None, storage_field=None,
                 unit=None, choices=None, data=None, parent=None):
        verbose_name = verbose_name or key
        storage_field = storage_field or key
        choices = choices or ()
        data = data or {}

        self.key = key
        self.type = type
        self.verbose_name = verbose_name
        self.storage_field = storage_field
        self.unit = unit
        self.choices = choices
        self.data = data
        self.parent = parent

    def _set_key(self, key):
        self.key = key
        if not self.verbose_name:
            self.verbose_name = key
        if not self.storage_field:
            self.storage_field = key

    def get_storage_field(self):
        if not self.parent:
            return self.storage_field

        parent_field = getattr(self.model, self.parent)
        return '{}.{}'.format(parent_field.get_storage_field(), self.storage_field)

    def bucket_params(self):
        d = {
            'name': self.key,
            'field': self.get_storage_field(),
        }

        if 'script' in self.data:
            # should we remove field?
            d['script'] = self.data['script'].format('_value')

        if 'size' in self.data:
            size = self.data['size']
            if size == 0:
                size = 2 ** 32 - 1
            d['size'] = size

        return d

    def is_range(self):
        return 'ranges' in self.data


class TextField(Field):
    def __init__(self, **kwargs):
        super(TextField, self).__init__('text', **kwargs)


class KeywordField(Field):
    def __init__(self, **kwargs):
        super(KeywordField, self).__init__('keyword', **kwargs)


class DateField(Field):
    def __init__(self, **kwargs):
        super(DateField, self).__init__('date', **kwargs)


class IntegerField(Field):
    def __init__(self, **kwargs):
        super(IntegerField, self).__init__('integer', **kwargs)


class BooleanField(Field):
    def __init__(self, **kwargs):
        super(BooleanField, self).__init__('boolean', **kwargs)


class NestedField(Field):
    def __init__(self, **kwargs):
        super(NestedField, self).__init__('nested', **kwargs)

    def nested_params(self):
        params = {
            'name': self.key,
            'agg_type': 'nested',
            'path': self.get_storage_field(),
        }
        return params


class ReverseNestedField(Field):
    def __init__(self, **kwargs):
        super(ReverseNestedField, self).__init__('reverse_nested', **kwargs)

    def nested_params(self):
        params = {
            'name': self.key,
            'agg_type': 'reverse_nested',
        }
        # /!\ path must not be provided for root reverse_nested aggregation
        if self.key != 'root':
            params['path'] = self.key

        return params


class FieldWithChoices(Field):
    def __init__(self, field, choices=None):
        choices = choices or ()
        data = copy.deepcopy(field.data)
        return super(FieldWithChoices, self).__init__(
            field.type,
            key=field.key,
            verbose_name=field.verbose_name,
            storage_field=field.storage_field,
            unit=field.unit,
            choices=choices,
            data=data,
            parent=field.parent,
        )


class DataExtendedField(Field):
    def __init__(self, field, **kwargs):
        data = copy.deepcopy(field.data)
        data.update(**kwargs)
        return super(DataExtendedField, self).__init__(
            field.type,
            key=field.key,
            verbose_name=field.verbose_name,
            storage_field=field.storage_field,
            unit=field.unit,
            choices=field.choices,
            data=data,
            parent=field.parent,
        )
