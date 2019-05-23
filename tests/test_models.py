# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run --omit="*tests*,*venv*,odc_pycommons/__init__.py" -m tests.test_models
    $ coverage report -m

"""

import unittest
from odc_pycommons.models import CommsRequest
from odc_pycommons.models import CommsRestFulRequest


class TestCommsRequest(unittest.TestCase):

    def test_init_comms_request_01(self):
        instance = CommsRequest(uri='test')
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, CommsRequest)
        self.assertEqual('test', instance.uri)
        self.assertIsNone(instance.trace_id)

    def test_init_comms_request_02(self):
        instance = CommsRequest(uri='test', trace_id='trace1')
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, CommsRequest)
        self.assertEqual('test', instance.uri)
        self.assertIsNotNone(instance.trace_id)
        self.assertEqual('trace1', instance.trace_id)

    def test_init_fail_on_none_uri_01(self):
        with self.assertRaises(Exception):
            CommsRequest(uri=None)

    def test_validate_valid_uri(self):
        instance = CommsRequest(uri='test')
        instance._validate(uri='final')
        self.assertEqual('final', instance.uri)

    def test_validate_fail_on_uri_as_int(self):
        instance = CommsRequest(uri='test')
        with self.assertRaises(Exception):
            instance._validate(uri=123)

    def test_validate_fail_on_uri_to_short(self):
        instance = CommsRequest(uri='test')
        with self.assertRaises(Exception):
            instance._validate(uri='')

    def test_validate_warn_on_trace_id_not_string(self):
        instance = CommsRequest(uri='test')
        instance._validate(uri='test', trace_id=123)
        self.assertIsNone(instance.trace_id)

    def test_fail_on_dict_call(self):
        instance = CommsRequest(uri='test')
        with self.assertRaises(Exception):
            instance.to_dict()


class TestCommsRestFulRequest(unittest.TestCase):

    def test_init_comms_rest_ful_request_01(self):
        instance = CommsRestFulRequest(uri='test', data={'a': 1, 'b': True, 'c': 123})
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, CommsRequest)
        self.assertEqual('test', instance.uri)
        self.assertIsNone(instance.trace_id)
        self.assertIsNotNone(instance.data)
        self.assertIsInstance(instance.data, dict)
        self.assertTrue(3, len(instance.data))

    def test_validate_fail_on_data_is_none(self):
        instance = CommsRestFulRequest(uri='test', data={'a': 1, 'b': True, 'c': 123})
        with self.assertRaises(Exception):
            instance._validate_data(data=None)

    def test_validate_fail_on_data_is_string(self):
        instance = CommsRestFulRequest(uri='test', data={'a': 1, 'b': True, 'c': 123})
        with self.assertRaises(Exception):
            instance._validate_data(data='123')

    def test_restful_data_to_dict_from_dict(self):
        instance = CommsRestFulRequest(uri='test', data={'a': 1, 'b': True, 'c': 123})
        d = instance.to_dict()
        for key in list(d.keys()):
            self.assertTrue(key in instance.data, 'Key "{}" not found'.format(key))

    def test_restful_data_to_dict_from_list(self):
        instance = CommsRestFulRequest(uri='test', data=[1, 2, 3])
        d = instance.to_dict()
        self.assertEqual(3, len(d))
        for item in d:
            self.assertTrue(item in instance.data, 'Item "{}" not found'.format(item))

    def test_restful_data_to_dict_from_tuple(self):
        instance = CommsRestFulRequest(uri='test', data=(1, 2, 3))
        d = instance.to_dict()
        self.assertIsInstance(d, list)
        self.assertEqual(3, len(d))
        for item in d:
            self.assertTrue(item in instance.data, 'Item "{}" not found'.format(item))

    def test_restful_to_dict_invalid_data_type_produces_warning(self):
        instance = CommsRestFulRequest(uri='test', data=(1, 2, 3))
        instance.data = 'abc'
        d = instance.to_dict()
        self.assertEqual(0, len(d))

    def test_restful_data_to_json_from_dict(self):
        instance = CommsRestFulRequest(uri='test', data={'a': 1, 'b': True, 'c': 123})
        j = instance.to_json()
        self.assertIsInstance(j, str)
        for key in list(instance.data.keys()):
            self.assertTrue('"{}"'.format(key) in j, 'Key "{}" not found'.format(key))


# EOF
