# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run --omit="*tests*,*venv*,odc_pycommons/__init__.py,odc_pycommons\models.py"  -m tests.test_comms
    $ coverage report -m
"""

import unittest
from odc_pycommons.comms import _prepare_comms_response_on_http_response
from odc_pycommons.models import CommsRequest, CommsRestFulRequest, CommsResponse


class TestPrepareResponseOnResponse(unittest.TestCase):

    def test_init_prepare_response_on_response(self):
        result = _prepare_comms_response_on_http_response()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CommsResponse)
        self.assertEqual(-2, result.response_code)
        self.assertTrue(result.is_error)
        self.assertEqual('Unknown error', result.response_code_description)
        self.assertIsNone(result.response_data)

    def test_success_response_200(self):
        result = _prepare_comms_response_on_http_response(response_code=200)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CommsResponse)
        self.assertEqual(200, result.response_code)
        self.assertFalse(result.is_error)
        self.assertEqual('Ok', result.response_code_description)
        self.assertIsNone(result.response_data)

    def test_success_response_all(self):
        for response_code in range(200, 300):
            result = _prepare_comms_response_on_http_response(response_code=response_code)
            self.assertIsNotNone(result, 'failed on response code "{}"'.format(response_code))
            self.assertIsInstance(result, CommsResponse, 'failed on response code "{}"'.format(response_code))
            self.assertEqual(response_code, result.response_code, 'failed on response code "{}"'.format(response_code))
            self.assertFalse(result.is_error, 'failed on response code "{}"'.format(response_code))
            self.assertEqual('Ok', result.response_code_description, 'failed on response code "{}"'.format(response_code))
            self.assertIsNone(result.response_data, 'failed on response code "{}"'.format(response_code))

    def test_http_errors_response_all(self):
        http_errors = list(range(1,200)) + list(range(300,600))
        for response_code in http_errors:
            result = _prepare_comms_response_on_http_response(response_code=response_code)
            self.assertIsNotNone(result, 'failed on response code "{}"'.format(response_code))
            self.assertIsInstance(result, CommsResponse, 'failed on response code "{}"'.format(response_code))
            self.assertEqual(response_code, result.response_code, 'failed on response code "{}"'.format(response_code))
            self.assertTrue(result.is_error, 'failed on response code "{}"'.format(response_code))
            self.assertEqual('Refer to the appropriate HTTP error code: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes', result.response_code_description, 'failed on response code "{}"'.format(response_code))
            self.assertIsNone(result.response_data, 'failed on response code "{}"'.format(response_code))

    def test_unknown__response_700(self):
        result = _prepare_comms_response_on_http_response(response_code=700)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, CommsResponse)
        self.assertEqual(-4, result.response_code)
        self.assertTrue(result.is_error)
        self.assertEqual('The command completed, but an unknown error occurred', result.response_code_description)
        self.assertIsNone(result.response_data)


if __name__ == '__main__':
    unittest.main()

# EOF
