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
import json
from odc_pycommons.models import CommsRequest
from odc_pycommons.models import CommsRestFulRequest
from odc_pycommons.models import CommsResponse
from odc_pycommons.models import ThingSensorAxis
from odc_pycommons.models import ThingSensor
from odc_pycommons.models import Thing
from decimal import Decimal


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


class TestCommsResponse(unittest.TestCase):

    def test_init_default_comms_response(self):
        response = CommsResponse()
        self.assertIsNotNone(response)
        self.assertIsInstance(response, CommsResponse)
        self.assertTrue(response.is_error)
        self.assertIsNotNone(response.response_code)
        self.assertIsInstance(response.response_code, int)
        self.assertEqual(response.response_code, -1)
        self.assertIsNotNone(response.response_code_description)
        self.assertIsInstance(response.response_code_description, str)
        self.assertIsNone(response.response_data)

    def test_fail_on_is_error_is_none(self):
        with self.assertRaises(Exception):
            CommsResponse(is_error=None)

    def test_fail_on_is_error_is_not_bool(self):
        with self.assertRaises(Exception):
            CommsResponse(is_error=1)

    def test_fail_on_response_code_is_none(self):
        with self.assertRaises(Exception):
            CommsResponse(response_code=None)

    def test_fail_on_response_code_is_not_int(self):
        with self.assertRaises(Exception):
            CommsResponse(response_code='ok')

    def test_fail_on_response_code_description_is_not_str(self):
        with self.assertRaises(Exception):
            CommsResponse(response_code_description=200)

    def test_fail_on_response_data_is_not_str(self):
        with self.assertRaises(Exception):
            CommsResponse(response_data=200)
        with self.assertRaises(Exception):
            CommsResponse(response_data=True)
        with self.assertRaises(Exception):
            CommsResponse(response_data={'a':1})

    def test_fail_on_trace_id_is_not_str(self):
        with self.assertRaises(Exception):
            CommsResponse(trace_id=200)

    def test_init_default_comms_response_to_dict(self):
        response = CommsResponse()
        response_dict = response.to_dict()
        self.assertIsNotNone(response_dict)
        self.assertIsInstance(response_dict, dict)
        expected = {
            'IsError': True,
            'ResponseCode': -1,
            'ResponseDescription': 'Response code undefined',
            'Data': None,
            'TraceId': None,
            'Warnings': list()
        }
        for expected_key, expected_value in expected.items():
            self.assertTrue(expected_key in response_dict, 'Key "{}" not found'.format(expected_key))
            self.assertEqual(expected[expected_key], response_dict[expected_key], 'Key "{}", value mismatch.'.format(expected_key))

    def test_with_data_comms_response_to_dict(self):
        response = CommsResponse(
            is_error=False,
            response_code=200,
            response_code_description='Ok',
            response_data='{"a": "test", "b": 1, "c": true, "d": null}'
        )
        response_dict = response.to_dict()
        self.assertIsNotNone(response_dict)
        self.assertIsInstance(response_dict, dict)
        expected = {
            'IsError': False,
            'ResponseCode': 200,
            'ResponseDescription': 'Ok',
            'Data': '{"a": "test", "b": 1, "c": true, "d": null}',
            'TraceId': None,
            'Warnings': list()
        }
        for expected_key, expected_value in expected.items():
            self.assertTrue(expected_key in response_dict, 'Key "{}" not found'.format(expected_key))
            self.assertEqual(expected[expected_key], response_dict[expected_key], 'Key "{}", value mismatch.'.format(expected_key))

    def test_with_data_comms_response_to_dict_data_as_tuple(self):
        response = CommsResponse(
            is_error=False,
            response_code=200,
            response_code_description='Ok',
            response_data=None
        )
        response.response_data = (1, 2, 3, )
        response_dict = response.to_dict()
        self.assertIsNotNone(response_dict)
        self.assertIsInstance(response_dict, dict)
        self.assertTrue('Data' in response_dict)
        self.assertIsInstance(response_dict['Data'], list)

    def test_with_data_comms_response_to_dict_data_as_decimal(self):
        response = CommsResponse(
            is_error=False,
            response_code=200,
            response_code_description='Ok',
            response_data=None
        )
        response.response_data = Decimal(22/7)
        response_dict = response.to_dict()
        self.assertIsNotNone(response_dict)
        self.assertIsInstance(response_dict, dict)
        self.assertTrue('Data' in response_dict)
        self.assertIsInstance(response_dict['Data'], str)
        self.assertTrue(response_dict['Data'].startswith('3.14'))


class TestAwsThingSensorAxis(unittest.TestCase):

    def test_aws_thing_sensor_axis_init_01(self):
        axis = ThingSensorAxis(axis_name='axis1')
        self.assertIsNotNone(axis)
        self.assertIsInstance(axis, ThingSensorAxis)
        self.assertEqual(axis.axis_name, 'axis1')
        self.assertEqual(axis.axis_data_type, 'STRING')

    def test_aws_thing_sensor_axis_init_with_valid_type(self):
        axis = ThingSensorAxis(axis_name='axis1', axis_data_type='NUMBER')
        self.assertIsNotNone(axis)
        self.assertIsInstance(axis, ThingSensorAxis)
        self.assertEqual(axis.axis_name, 'axis1')
        self.assertEqual(axis.axis_data_type, 'NUMBER')

    def test_aws_thing_sensor_axis_init_with_invalid_type(self):
        with self.assertRaises(Exception):
            ThingSensorAxis(axis_name='axis1', axis_data_type='some-funny-type')

    def test_aws_thing_sensor_axis_to_dict(self):
        axis = ThingSensorAxis(axis_name='axis1')
        d = axis.to_dict()
        self.assertIsNotNone(d)
        self.assertIsInstance(d, dict)
        self.assertTrue(len(d) == 2)
        self.assertTrue('AxisName' in d)
        self.assertTrue('AxisDataType' in d)
        self.assertEqual(d['AxisName'], 'axis1')
        self.assertEqual(d['AxisDataType'], 'STRING')

    def test_aws_thing_sensor_axis_to_json(self):
        axis = ThingSensorAxis(axis_name='axis1')
        j = axis.to_json()
        self.assertIsNotNone(j)
        self.assertIsInstance(j, str)
        self.assertTrue(len(j) > 0)
        d = json.loads(j)
        self.assertTrue(len(d) == 2)
        self.assertTrue('AxisName' in d)
        self.assertTrue('AxisDataType' in d)
        self.assertEqual(d['AxisName'], 'axis1')
        self.assertEqual(d['AxisDataType'], 'STRING')


class TestAwsThingSensor(unittest.TestCase):

    def test_aws_thing_sensor_init_01(self):
        sensor = ThingSensor(sensor_name='sensor1')
        self.assertIsNotNone(sensor)
        self.assertIsInstance(sensor, ThingSensor)
        self.assertEqual(sensor.sensor_name, 'sensor1')
        self.assertIsInstance(sensor.axis_collection, list)
        self.assertTrue(len(sensor.axis_collection) == 0) 

    def test_aws_thing_sensor_init_02(self):
        sensor_axis_collection = [
            ThingSensorAxis(axis_name='axis1'),
            ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
        ]
        sensor = ThingSensor(sensor_name='sensor1', axis_collection=sensor_axis_collection)
        self.assertIsInstance(sensor.axis_collection, list)
        self.assertTrue(len(sensor.axis_collection) == 2)
        for axis in sensor.axis_collection:
            self.assertIsInstance(axis, ThingSensorAxis)

    def test_aws_thing_sensor_to_dict_01(self):
        sensor = ThingSensor(sensor_name='sensor1')
        d = sensor.to_dict()
        self.assertIsNotNone(d)
        self.assertIsInstance(d, dict)
        self.assertEqual(len(d), 2)
        self.assertTrue('SensorName' in d)
        self.assertTrue('SensorAxisCollection' in d)
        self.assertIsNotNone(d['SensorName'])
        self.assertIsNotNone(d['SensorAxisCollection'])
        self.assertEqual(d['SensorName'], 'sensor1')
        self.assertIsInstance(d['SensorAxisCollection'], list)
        self.assertEqual(len(d['SensorAxisCollection']), 0)

    def test_aws_thing_sensor_to_dict_02(self):
        sensor_axis_collection = [
            ThingSensorAxis(axis_name='axis1'),
            ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
        ]
        sensor = ThingSensor(sensor_name='sensor1', axis_collection=sensor_axis_collection)
        d = sensor.to_dict()
        self.assertIsNotNone(d)
        self.assertIsInstance(d, dict)
        self.assertEqual(len(d), 2)
        self.assertTrue('SensorName' in d)
        self.assertTrue('SensorAxisCollection' in d)
        self.assertIsNotNone(d['SensorName'])
        self.assertIsNotNone(d['SensorAxisCollection'])
        self.assertEqual(d['SensorName'], 'sensor1')
        self.assertIsInstance(d['SensorAxisCollection'], list)
        self.assertEqual(len(d['SensorAxisCollection']), 2)
        for axis in d['SensorAxisCollection']:
            self.assertIsNotNone(axis)
            self.assertIsInstance(axis, dict)
            self.assertEqual(len(axis), 2)
            self.assertTrue('AxisName' in axis)
            self.assertTrue('AxisDataType' in axis)

    def test_aws_thing_sensor_to_json_01(self):
        sensor = ThingSensor(sensor_name='sensor1')
        j = sensor.to_json()
        self.assertIsNotNone(j)
        self.assertIsInstance(j, str)
        self.assertTrue(len(j) > 0)
        d = json.loads(j)
        self.assertTrue('SensorName' in d)
        self.assertTrue('SensorAxisCollection' in d)
        self.assertIsNotNone(d['SensorName'])
        self.assertIsNotNone(d['SensorAxisCollection'])
        self.assertEqual(d['SensorName'], 'sensor1')
        self.assertIsInstance(d['SensorAxisCollection'], list)
        self.assertEqual(len(d['SensorAxisCollection']), 0)

    def test_aws_thing_sensor_to_json_02(self):
        sensor_axis_collection = [
            ThingSensorAxis(axis_name='axis1'),
            ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
        ]
        sensor = ThingSensor(sensor_name='sensor1', axis_collection=sensor_axis_collection)
        j = sensor.to_json()
        self.assertIsNotNone(j)
        self.assertIsInstance(j, str)
        self.assertTrue(len(j) > 0)
        d = json.loads(j)
        self.assertIsNotNone(d)
        self.assertIsInstance(d, dict)
        self.assertEqual(len(d), 2)
        self.assertTrue('SensorName' in d)
        self.assertTrue('SensorAxisCollection' in d)
        self.assertIsNotNone(d['SensorName'])
        self.assertIsNotNone(d['SensorAxisCollection'])
        self.assertEqual(d['SensorName'], 'sensor1')
        self.assertIsInstance(d['SensorAxisCollection'], list)
        self.assertEqual(len(d['SensorAxisCollection']), 2)
        for axis in d['SensorAxisCollection']:
            self.assertIsNotNone(axis)
            self.assertIsInstance(axis, dict)
            self.assertEqual(len(axis), 2)
            self.assertTrue('AxisName' in axis)
            self.assertTrue('AxisDataType' in axis)

    def test_aws_thing_sensor_init_with_invalid_axis_collection(self):
        sensor_axis_collection = [
            ThingSensorAxis(axis_name='axis1'),
            123
        ]
        with self.assertRaises(Exception):
            ThingSensor(sensor_name='sensor1', axis_collection=sensor_axis_collection)


class TestAwsThing(unittest.TestCase):

    def test_aws_thing_init_01(self):
        thing = Thing(thing_name='thing1')
        self.assertIsNotNone(thing)
        self.assertIsInstance(thing, Thing)
        self.assertEqual(thing.thing_name, 'thing1')
        self.assertIsNone(thing.thing_arn)
        self.assertIsNotNone(thing.sensors)
        self.assertIsInstance(thing.sensors, list)
        self.assertEqual(len(thing.sensors), 0)

    def test_aws_thing_init_02(self):
        thing = Thing(thing_name='thing1', thing_arn='arn1')
        self.assertIsNotNone(thing)
        self.assertIsInstance(thing, Thing)
        self.assertEqual(thing.thing_name, 'thing1')
        self.assertIsNotNone(thing.thing_arn)
        self.assertIsInstance(thing.thing_arn, str)
        self.assertEqual(thing.thing_arn, 'arn1')
        self.assertIsNotNone(thing.sensors)
        self.assertIsInstance(thing.sensors, list)
        self.assertEqual(len(thing.sensors), 0)

    def test_aws_thing_init_03(self):
        sensor1 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
                ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
            ]
        )
        sensor2 = ThingSensor(
            sensor_name='sensor2',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
            ]
        )
        thing = Thing(thing_name='thing1', thing_arn='arn1', sensors=[sensor1, sensor2])
        self.assertIsNotNone(thing)
        self.assertIsInstance(thing, Thing)
        self.assertEqual(thing.thing_name, 'thing1')
        self.assertIsNotNone(thing.thing_arn)
        self.assertIsInstance(thing.thing_arn, str)
        self.assertEqual(thing.thing_arn, 'arn1')
        self.assertIsNotNone(thing.sensors)
        self.assertIsInstance(thing.sensors, list)
        self.assertEqual(len(thing.sensors), 2)
        for sensor in thing.sensors:
            self.assertIsInstance(sensor, ThingSensor)

    def test_aws_thing_init_fail_with_invalid_sensor(self):
        sensor1 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
                ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
            ]
        )
        sensor2 = 123
        with self.assertRaises(Exception):
            Thing(thing_name='thing1', thing_arn='arn1', sensors=[sensor1, sensor2])

    def test_aws_thing_init_fail_with_valid_sensor_and_missing_axis(self):
        sensor1 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
                ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
            ]
        )
        sensor2 = ThingSensor(
            sensor_name='sensor2'
        )
        with self.assertRaises(Exception):
            Thing(thing_name='thing1', thing_arn='arn1', sensors=[sensor1, sensor2])

    def test_aws_thing_init_fail_with_duplicate_sensor_names(self):
        sensor1 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
                ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
            ]
        )
        sensor2 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1')
            ]
        )
        with self.assertRaises(Exception):
            Thing(thing_name='thing1', thing_arn='arn1', sensors=[sensor1, sensor2])

    def test_aws_thing_init_fail_with_invalid_sensor_collection(self):
        with self.assertRaises(Exception):
            Thing(thing_name='thing1', thing_arn='arn1', sensors=123)

    def test_aws_thing_to_dict(self):
        sensor1 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
                ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
            ]
        )
        sensor2 = ThingSensor(
            sensor_name='sensor2',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
            ]
        )
        thing = Thing(thing_name='thing1', thing_arn='arn1', sensors=[sensor1, sensor2])
        d = thing.to_dict()
        self.assertIsNotNone(d)
        self.assertIsInstance(d, dict)
        self.assertEqual(len(d), 3)
        self.assertTrue('ThingName' in d)
        self.assertTrue('ThingArn' in d)
        self.assertTrue('ThingSensors' in d)
        self.assertIsInstance(d['ThingName'], str)
        self.assertIsInstance(d['ThingArn'], str)
        self.assertIsInstance(d['ThingSensors'], list)
        self.assertEqual(d['ThingName'], 'thing1')
        self.assertEqual(d['ThingArn'], 'arn1')
        for sensor in d['ThingSensors']:
            self.assertIsNotNone(sensor)
            self.assertIsInstance(sensor, dict)
            self.assertEqual(len(sensor), 2)
            self.assertTrue('SensorName' in sensor)
            self.assertTrue('SensorAxisCollection' in sensor)
            self.assertIsNotNone(sensor['SensorName'])
            self.assertIsNotNone(sensor['SensorAxisCollection'])
            self.assertIsInstance(sensor['SensorAxisCollection'], list)
            self.assertTrue(len(sensor['SensorAxisCollection']) > 0)
            for axis in sensor['SensorAxisCollection']:
                self.assertIsNotNone(axis)
                self.assertIsInstance(axis, dict)
                self.assertEqual(len(axis), 2)
                self.assertTrue('AxisName' in axis)
                self.assertTrue('AxisDataType' in axis)

    def test_aws_thing_to_json(self):
        sensor1 = ThingSensor(
            sensor_name='sensor1',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
                ThingSensorAxis(axis_name='axis2', axis_data_type='NUMBER')
            ]
        )
        sensor2 = ThingSensor(
            sensor_name='sensor2',
            axis_collection=[
                ThingSensorAxis(axis_name='axis1'),
            ]
        )
        thing = Thing(thing_name='thing1', thing_arn='arn1', sensors=[sensor1, sensor2])
        j = thing.to_json()
        self.assertIsNotNone(j)
        self.assertIsInstance(j, str)
        self.assertTrue(len(j) > 0)
        d = json.loads(j)
        self.assertIsNotNone(d)
        self.assertIsInstance(d, dict)
        self.assertEqual(len(d), 3)
        self.assertTrue('ThingName' in d)
        self.assertTrue('ThingArn' in d)
        self.assertTrue('ThingSensors' in d)
        self.assertIsInstance(d['ThingName'], str)
        self.assertIsInstance(d['ThingArn'], str)
        self.assertIsInstance(d['ThingSensors'], list)
        self.assertEqual(d['ThingName'], 'thing1')
        self.assertEqual(d['ThingArn'], 'arn1')
        for sensor in d['ThingSensors']:
            self.assertIsNotNone(sensor)
            self.assertIsInstance(sensor, dict)
            self.assertEqual(len(sensor), 2)
            self.assertTrue('SensorName' in sensor)
            self.assertTrue('SensorAxisCollection' in sensor)
            self.assertIsNotNone(sensor['SensorName'])
            self.assertIsNotNone(sensor['SensorAxisCollection'])
            self.assertIsInstance(sensor['SensorAxisCollection'], list)
            self.assertTrue(len(sensor['SensorAxisCollection']) > 0)
            for axis in sensor['SensorAxisCollection']:
                self.assertIsNotNone(axis)
                self.assertIsInstance(axis, dict)
                self.assertEqual(len(axis), 2)
                self.assertTrue('AxisName' in axis)
                self.assertTrue('AxisDataType' in axis)


if __name__ == '__main__':
    unittest.main()

# EOF
