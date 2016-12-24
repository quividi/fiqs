# -*- coding: utf-8 -*-

from elasticsearch_dsl import Mapping, Nested

from fiqs.fields import Field, NestedField


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        klass = super(ModelMetaClass, cls).__new__(cls, name, bases, attrs)

        fields = []
        for k, v in attrs.iteritems():
            if isinstance(v, Field):
                # We set the field's key
                v._set_key(k)
                # Give the model access to the field
                getattr(klass, k).model = klass
                fields.append(v)

        cls._fields = fields

        return klass


class Model(object):
    __metaclass__ = ModelMetaClass

    index = None
    doc_type = None

    @classmethod
    def get_index(cls, *args, **kwargs):
        if not cls.index:
            raise NotImplementedError('Model class should define an index')

        return cls.index

    @classmethod
    def get_doc_type(cls, *args, **kwargs):
        if not cls.doc_type:
            raise NotImplementedError('Model class should define a doc_type')

        return cls.doc_type

    @classmethod
    def get_mapping(cls):
        m = Mapping(cls.get_doc_type())
        m.meta('dynamic', 'strict')

        nested_mappings = {}
        fields_to_nest = []

        for field in cls._fields:
            if isinstance(field, NestedField):
                nested_mappings[field.key] = (field, Nested())

            if field.parent:
                fields_to_nest.append(field)
            else:
                m.field(field.storage_field, field.type)

        for field in fields_to_nest:
            if field.parent not in nested_mappings:
                raise Exception(
                    'Nested field {} needs to be defined in {}'.format(
                        field.parent, str(cls)))

            _, nested_mapping = nested_mappings[field.parent]
            nested_mapping.field(field.storage_field, field.type)

        for field, nested_mapping in nested_mappings.values():
            if not field.parent:
                m.field(field.key, nested_mapping)
            else:
                _, parent_mapping = nested_mappings[field.parent]
                parent_mapping.field(field.key, nested_mapping)

        return m