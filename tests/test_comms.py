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


Special thanks to:

    * Miel Donkers for https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7 that helped a lot in setting up the web server test framework
    * Hasan Sajedi for https://dev.to/hasansajedi/running-a-method-as-a-background-process-in-python-21li that helped me figure out how to run the test web server in the background 

"""

import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
from odc_pycommons.comms import _prepare_comms_response_on_http_response
from odc_pycommons.comms import _parse_parameters_and_join_with_uri
from odc_pycommons.comms import get
from odc_pycommons.comms import json_post
from odc_pycommons.models import CommsRequest, CommsRestFulRequest, CommsResponse


class HttpHandlerForLocalTesting(BaseHTTPRequestHandler):

    def _set_200_json_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _set_201_json_response(self):
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_200_json_response()
        result = {
            'GET': 'Ok',
            'Path': str(self.path),
            'Headers': str(self.headers),
        }
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])    # <--- Gets the size of data
        post_data = self.rfile.read(content_length)             # <--- Gets the data itself
        self._set_201_json_response()
        result = {
            'POST': 'Ok',
            'Path': str(self.path),
            'Headers': str(self.headers),
            'Body': post_data.decode('utf-8'),
        }
        self.wfile.write(json.dumps(result).encode('utf-8'))


class HttpTestServerThreading(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        print('Starting Web Server')
        HTTPServer(('127.0.0.1', 8083), HttpHandlerForLocalTesting).serve_forever()


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


class TestParseParametersAndJoinWithUri(unittest.TestCase):

    def test_no_parameters_test(self):
        final_uri = _parse_parameters_and_join_with_uri(uri='test', uri_parameters={})
        self.assertIsNotNone(final_uri)
        self.assertIsInstance(final_uri, str)
        self.assertEqual('test', final_uri)

    def test_one_parameters_test(self):
        final_uri = _parse_parameters_and_join_with_uri(uri='test', uri_parameters={'a': 'test_a'})
        self.assertIsNotNone(final_uri)
        self.assertIsInstance(final_uri, str)
        self.assertEqual('test?a=test_a', final_uri)

    def test_two_parameters_test(self):
        final_uri = _parse_parameters_and_join_with_uri(uri='test', uri_parameters={'a': 'test_a', 'b': 2})
        self.assertIsNotNone(final_uri)
        self.assertIsInstance(final_uri, str)
        self.assertTrue('test?' in final_uri)
        self.assertTrue('a=test_a' in final_uri)
        self.assertTrue('b=2' in final_uri)
        self.assertTrue('&' in final_uri)
        self.assertEqual(1, final_uri.count('?'))
        self.assertEqual(1, final_uri.count('&'))
        self.assertEqual(2, final_uri.count('='))

    def test_three_parameters_test(self):
        final_uri = _parse_parameters_and_join_with_uri(uri='test', uri_parameters={'a': 'test_a', 'b': 2, 'c': 'o k'})
        self.assertIsNotNone(final_uri, 'final_uri={}'.format(final_uri))
        self.assertIsInstance(final_uri, str, 'final_uri={}'.format(final_uri))
        self.assertTrue('test?' in final_uri, 'final_uri={}'.format(final_uri))
        self.assertTrue('a=test_a' in final_uri, 'final_uri={}'.format(final_uri))
        self.assertTrue('b=2' in final_uri, 'final_uri={}'.format(final_uri))
        self.assertTrue('c=o+k' in final_uri, 'final_uri={}'.format(final_uri))
        self.assertTrue('&' in final_uri, 'final_uri={}'.format(final_uri))
        self.assertEqual(1, final_uri.count('?'), 'final_uri={}'.format(final_uri))
        self.assertEqual(2, final_uri.count('&'), 'final_uri={}'.format(final_uri))
        self.assertEqual(3, final_uri.count('='), 'final_uri={}'.format(final_uri))


class TestGetFunction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._connection = HttpTestServerThreading()
        print('Web Server Running')

    @classmethod
    def tearDownClass(cls):
        cls._connection = None
        print('Web Server Stopped')

    def test_local_server_basic_get_01(self):
        get_comms_request = CommsRequest(uri='http://127.0.0.1:8083/dummy')
        request_result = get(request=get_comms_request)
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(200, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(request_result.response_data, str)
        self.assertTrue('GET' in request_result.response_data)
        self.assertFalse('authorization' in request_result.response_data.lower())

    def test_local_server_get_with_path_parameters(self):
        get_comms_request = CommsRequest(uri='http://127.0.0.1:8083/dummy/__VAR__')
        request_result = get(request=get_comms_request, path_parameters={'__VAR__': 'testvar'})
        response_dict = json.loads(request_result.response_data)
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(200, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(response_dict, dict)
        self.assertTrue('Path' in response_dict)
        self.assertEqual('/dummy/testvar', response_dict['Path'])
        self.assertFalse('authorization' in request_result.response_data.lower())

    def test_local_server_get_with_bearer_token_01(self):
        get_comms_request = CommsRequest(uri='http://127.0.0.1:8083/dummy')
        request_result = get(request=get_comms_request, bearer_token='aaa.bbb.ccc')
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(200, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(request_result.response_data, str)
        self.assertTrue('GET' in request_result.response_data)
        self.assertTrue('authorization' in request_result.response_data.lower())
        self.assertTrue('aaa.bbb.ccc' in request_result.response_data.lower())


class TestJsonPostFunction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._connection = HttpTestServerThreading()
        print('Web Server Running')

    @classmethod
    def tearDownClass(cls):
        cls._connection = None
        print('Web Server Stopped')

    def test_local_server_basic_post_01(self):
        post_comms_request = CommsRestFulRequest(uri='http://127.0.0.1:8083/dummy', data={})
        request_result = json_post(request=post_comms_request)
        data_dict = json.loads(request_result.response_data)
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(201, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(request_result.response_data, str)
        self.assertTrue('POST' in data_dict)
        self.assertTrue('Body' in data_dict)
        body = json.loads(data_dict['Body'])
        self.assertFalse('authorization' in request_result.response_data.lower())
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body), 0)

    def test_local_server_post_with_path_parameters(self):
        post_comms_request = CommsRestFulRequest(uri='http://127.0.0.1:8083/dummy/__VAR__', data={'a': 1, 'b': 'test'})
        request_result = json_post(request=post_comms_request, path_parameters={'__VAR__': 'testvar'})
        response_dict = json.loads(request_result.response_data)
        body = json.loads(response_dict['Body'])
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(201, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(response_dict, dict)
        self.assertTrue('Path' in response_dict)
        self.assertEqual('/dummy/testvar', response_dict['Path'])
        self.assertFalse('authorization' in request_result.response_data.lower())
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body), 2)
        self.assertTrue('a' in body)
        self.assertTrue('b' in body)
        self.assertEqual(body['a'], 1)
        self.assertEqual(body['b'], 'test')

    def test_local_server_post_with_bearer_token_01(self):
        post_comms_request = CommsRestFulRequest(uri='http://127.0.0.1:8083/dummy', data={})
        request_result = json_post(request=post_comms_request, bearer_token='aaa.bbb.ccc')
        data_dict = json.loads(request_result.response_data)
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(201, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(request_result.response_data, str)
        self.assertTrue('POST' in data_dict)
        self.assertTrue('Body' in data_dict)
        body = json.loads(data_dict['Body'])
        self.assertTrue('authorization' in request_result.response_data.lower())
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body), 0)

    def test_local_server_post_with_user_agent_01(self):
        post_comms_request = CommsRestFulRequest(uri='http://127.0.0.1:8083/dummy', data={})
        request_result = json_post(request=post_comms_request, user_agent='test-agent v1')
        data_dict = json.loads(request_result.response_data)
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(201, request_result.response_code)
        self.assertFalse(request_result.is_error)
        self.assertIsInstance(request_result.response_data, str)
        self.assertTrue('POST' in data_dict)
        self.assertTrue('Body' in data_dict)
        body = json.loads(data_dict['Body'])
        self.assertFalse('authorization' in request_result.response_data.lower())
        self.assertTrue('user-agent: test-agent v1' in request_result.response_data.lower())
        self.assertIsInstance(body, dict)
        self.assertEqual(len(body), 0)

    def test_local_server_post_fail_on_empty_request_body_01(self):
        """The model CommsRestFulRequest forces a check that the data cannot be None, so we have to manually set it so after initializing the model
        """
        post_comms_request = CommsRestFulRequest(uri='http://127.0.0.1:8083/dummy', data={})
        post_comms_request.data = None
        request_result = json_post(request=post_comms_request)
        self.assertIsNotNone(request_result)
        self.assertIsInstance(request_result, CommsResponse)
        self.assertEqual(-6, request_result.response_code)


if __name__ == '__main__':
    unittest.main()

# EOF
