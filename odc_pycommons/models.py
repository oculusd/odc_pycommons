# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. Please refer to the LICENSE.txt file for full license information. Licensed in terms of the GPLv3 License.

from warnings import warn
import json
from email_validator import validate_email
import hashlib
from datetime import datetime
import traceback
from decimal import Decimal


class CommsRequest:

    def __init__(self, uri: str, trace_id: str=None):
        self.trace_id = None
        self._validate(uri=uri, trace_id=trace_id)        

    def _validate(self, uri: str, trace_id: str=None):
        if uri is None:
            raise Exception('the URI cannot be None. It is used for connecting to a remote host or some destination.')
        if not isinstance(uri, str):
            raise Exception('The URI must be a string')
        if len(uri) < 1:
            raise Exception('The URI must be a string containing a valid destination')
        self.uri = uri
        if trace_id is not None:
            if isinstance(trace_id, str):
                self.trace_id = trace_id
            else:
                warn('The Trace ID, when supplied, must be a string')

    def to_dict(self)->dict:
        raise Exception('Not implemented')


class CommsRestFulRequest(CommsRequest):

    def __init__(self, uri: str, data: dict=None, trace_id: str=None):
        self._validate_data(data=data)
        super().__init__(uri=uri, trace_id=trace_id)

    def _validate_data(self, data: dict):
        if data is None:
            raise Exception('Data must be supplied')
        if not type(data) in (dict, list, tuple):
            raise Exception('Unsupported data type: expected a dict or a list or a tuple')
        self.data = data

    def to_dict(self):
        data_value = dict()
        if self.data is not None:
            if type(self.data) in (dict, list):
                data_value = self.data
            elif isinstance(self.data, tuple):
                data_value = list(self.data)
            else:
                warn('Unsupported data type. The dictionary will be empty')
        return data_value

    def to_json(self):
        return json.dumps(self.to_dict())


class CommsResponse:

    def __init__(
        self,
        is_error: bool=True,
        response_code: int=-1,
        response_code_description: str='Response code undefined',
        response_data: str=None,
        trace_id: str=None
    ):
        self._validate(
            is_error=is_error,
            response_code=response_code,
            response_code_description=response_code_description,
            response_data=response_data,
            trace_id=trace_id
        )
        self.warnings = list()

    def _validate(
        self,
        is_error: bool,
        response_code: int,
        response_code_description: str,
        response_data: str,
        trace_id: str
    ):
        if is_error is None:
            raise Exception('Error flag must be a bool type [1]')
        if not isinstance(is_error, bool):
            raise Exception('Error flag must be a bool type [2]')
        self.is_error = is_error
        if response_code is None:
            raise Exception('A response code must be provided as an integer [1]')
        if not isinstance(response_code, int):
            raise Exception('A response code must be provided as an integer [2]')
        self.response_code = response_code
        if response_code_description is not None:
            if not isinstance(response_code_description, str):
                raise Exception('When supplying a response code description, the description must be a string')
        self.response_code_description = response_code_description
        if response_data is not None:
            if not isinstance(response_data, str):
                raise Exception('When supplying response data, the value must be a string')
        self.response_data = response_data
        if trace_id is not None:
            if not isinstance(trace_id, str):
                raise Exception('When supplying a trace ID, the value must be a string')
        self.trace_id = trace_id

    def to_dict(self):
        response_data_value = None
        if self.response_data is not None:
            response_data_type = type(self.response_data)
            if response_data_type in (str, int, dict, list):
                response_data_value = self.response_data
            elif isinstance(self.response_data, tuple):
                response_data_value = list(self.response_data)
            else:
                response_data_value = str(self.response_data)
        return {
            'IsError': self.is_error,
            'ResponseCode': self.response_code,
            'ResponseDescription': self.response_code_description,
            'Data': response_data_value,
            'TraceId': self.trace_id,
            'Warnings': self.warnings
        }


class RootAccount:

    def __init__(
        self,
        email_address: str,
        passphrase: str,
        account_name: str,
        root_account_ref: str=None,
        passphrase_is_insecure: bool=True,
        secure_passphrase: bool=True
    ):
        self.email_address = None
        self.passphrase = None
        self.account_name = None
        self.root_account_ref = None
        self.root_account_session_token = None
        self.root_account_session_create_timestamp = None
        self._validate_init(
            email_address=email_address,
            passphrase=passphrase,
            account_name=account_name,
            passphrase_is_insecure=passphrase_is_insecure,
            secure_passphrase=secure_passphrase
        )
        self._validate_root_account_ref(root_account_ref=root_account_ref)

    def _validate_init(
        self,
        email_address: str,
        passphrase: str,
        account_name: str,
        passphrase_is_insecure: bool=True,
        secure_passphrase: bool=True
    ):
        if email_address is None:
            raise Exception('email_address parameter must be supplied')
        if not isinstance(email_address, str):
            raise Exception('email_address parameter must both be of type str')
        v = validate_email(email_address)
        self.email_address = v["email"] 
        if passphrase is not None:
            if not isinstance(passphrase, str):
                raise Exception('If passphrase parameter is supplied, it must be a string')
            if len(passphrase) < 20:
                raise Exception('passhrase parameter must be at least 20 characters.')
            if passphrase_is_insecure is True and secure_passphrase is True:
                self.passphrase = hashlib.sha224(passphrase.encode('utf-8')).hexdigest()
            else:
                self.passphrase = passphrase
        else:
            self.passphrase = None
        if account_name is None:
            raise Exception('account_name parameter must be supplied')
        if not isinstance(account_name, str):
            raise Exception('account_name parameter must be of type str')
        if len(account_name) < 1 or len(account_name) > 31:
            raise Exception('account_name parameter must be between 1 and 31 characters in length')
        self.account_name = account_name

    def _validate_root_account_ref(self, root_account_ref: str=None):
        if root_account_ref is not None:
            if not isinstance(root_account_ref, str):
                raise Exception('root_account_ref parameter must be a string')
            if len(root_account_ref) < 4 or len(root_account_ref) > 32:
                raise Exception('root_account_ref appears invalid')
            self.root_account_ref = root_account_ref
        else:
            self.root_account_ref = None

    def _validate_root_account_session_token(self, root_account_session_token: str=None):
        if root_account_session_token is not None:
            if not isinstance(root_account_session_token, str):
                raise Exception('root_account_session_token parameter must be a string')
            if len(root_account_session_token) < 16 or len(root_account_session_token) > 1024:
                raise Exception('root_account_session_token appears invalid')
            if self.root_account_ref is None:
                raise Exception('Cannot set the root_account_session_token parameter if root_account_ref parameter is not supplied/set')
            self.root_account_session_token = root_account_session_token
            self.root_account_session_create_timestamp = int(datetime.utcnow().timestamp())
        else:
            self.root_account_session_token = None
            self.root_account_session_create_timestamp = None

    def set_root_account_ref(self, root_account_ref: str):
        self._validate_root_account_ref(root_account_ref=root_account_ref)

    def set_root_account_session_token(self, root_account_session_token: str):
        self._validate_root_account_session_token(root_account_session_token=root_account_session_token)


AXIS_DATA_TYPES = {
    'STRING': str,
    'NUMBER': Decimal,
    'BOOLEAN': bool
}


class SensorAxisReading:
    def __init__(
        self,
        reading_value: str,
    ):
        # TODO: Add SensorAxisReading validation
        self.reading_value = reading_value

    def to_csv(self):
        return '"{}"'.format(self.reading_value)


class SensorAxis:
    def __init__(
        self,
        axis_name: str,
        axis_user_defined_type: str='unknown-type',
        axis_data_type: str='NUMBER'
    ):
        # TODO: Add SensorAxis validation
        self.axis_name = axis_name
        if axis_data_type in AXIS_DATA_TYPES:
            self.axis_data_type = axis_data_type
        else:
            raise Exception('Unsupported Axis Data Type. Use one of {}'.format(list(AXIS_DATA_TYPES.keys())))
        self.readings = list()
        self.axis_user_defined_type = axis_user_defined_type

    def add_reading(self, reading: SensorAxisReading):
        if reading:
            if isinstance(reading, SensorAxisReading):
                self.readings.append(reading)

    def to_dict(self):
        return {
            'AxisName': self.axis_name,
            'UserDefinedType': self.axis_user_defined_type,
            'DataType': self.axis_data_type
        }


class Sensor:
    def __init__(
        self,
        sensor_name: str,
        sensor_description: str=None
    ):
        # TODO: Add Sensor validation
        self.sensor_name = sensor_name
        self.sensor_description = sensor_description
        self.sensor_axes = dict()
    
    def add_sensor_axis(self, sensor_axis: SensorAxis, trace_id: str=None):
        if sensor_axis:
            if isinstance(sensor_axis, SensorAxis):
                self.sensor_axes[sensor_axis.axis_name] = sensor_axis
    
    def get_sensor_axis_names(self)->list:
        names = list()
        if len(self.sensor_axes) > 0:
            names = list(self.sensor_axes.keys())
        return names

    def to_dict(self):
        result = dict()
        result['SensorName'] = self.sensor_name
        result['SensorDescription'] = self.sensor_description
        result['SensorAxis'] = list()
        for axis_name, axis in self.sensor_axes.items():
            result['SensorAxis'].append(axis.to_dict())
        return result


class Thing:
    def __init__(self, thing_name: str, thing_description: str=None, thing_meta_data: dict=dict(), thing_id: str=None, thing_token: str=None):
        # TODO: Add Thing validation
        self.thing_id = thing_id
        self.thing_name = thing_name
        self.thing_description = thing_description
        self.thing_meta_data = thing_meta_data
        self.thing_sensors = dict()
        self.thing_token = thing_token

    def add_sensor(self, sensor: Sensor):
        if sensor:
            if isinstance(sensor, Sensor):
                self.thing_sensors[sensor.sensor_name] = sensor

    def get_sensor_names(self)->list:
        if self.thing_sensors:
            if isinstance(self.thing_sensors, dict):
                if len(self.thing_sensors) > 0:
                    return list(self.thing_sensors.keys())
        return list()

    def to_dict(self, include_thing_id: bool=False):
        result = dict()
        result['ThingName'] = self.thing_name
        result['ThingDescription'] = self.thing_description
        result['ThingMetaData'] = self.thing_meta_data
        if include_thing_id is True:
            result['ThingId'] = self.thing_id
        result['Sensors'] = list()
        for sensor_name, sensor in self.thing_sensors.items():
            result['Sensors'].append(sensor.to_dict())
        return result


# EOF
