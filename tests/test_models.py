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


# EOF
