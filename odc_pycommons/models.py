# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from warnings import warn
import json
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


AXIS_DATA_TYPES = {
    'STRING': str,
    'NUMBER': Decimal,
    'BOOLEAN': bool
}


def _element_transform(
    input_field_name: str,
    input_field_value: object=None,
    can_be_none: bool=True,
    output_as_json: bool=True
):
    """Convert a input_field_name and input_field_value to a dict (default) or as JSON
    
    """
    return_value = {}
    if input_field_value is not None:
        if isinstance(input_field_value, ApiJsonBodyElement):
            return_value = {input_field_name: input_field_value.to_dict()}
        else:
            return_value = {input_field_name: input_field_value}
    elif can_be_none is False and input_field_value is None:
        raise Exception('value cannot be none for field named "{}"'.format(input_field_name))
    else: 
        return_value = {input_field_name: None}
    if output_as_json is True:
        return json.dumps(return_value)
    return return_value


class ApiJsonBodyElement:

    def __init__(
        self,
        field_name: str,
        can_be_none: bool=True,
        default_value: object=None,
        start_value: object=None,
        to_json_function: object=_element_transform,
        to_dict_function: object=_element_transform,
        is_required: bool=False
    ):
        self.field_name = field_name
        self.can_be_none = can_be_none
        self.default_value = default_value
        self.value = start_value
        if to_json_function is not None:
            if callable(to_json_function):
                self.to_json_function = to_json_function
        if to_dict_function is not None:
            if callable(to_dict_function):
                self.to_dict_function = to_dict_function
        self.is_required = is_required

    def set_value(self, value: object=None):
        self.value = value

    def to_json(self)->str:
        return self.to_json_function(
            input_field_name=self.field_name,
            input_field_value=self.value,
            can_be_none=self.can_be_none,
            output_as_json=True
        )

    def to_dict(self)->dict:
        return self.to_dict_function(
            input_field_name=self.field_name,
            input_field_value=self.value,
            can_be_none=self.can_be_none,
            output_as_json=False
        )


class ApiJsonBody:

    def __init__(self, root_elements: list=list()):
        self.root_elements = list()
        if len(root_elements) > 0:
            for e in root_elements:
                if isinstance(e, ApiJsonBodyElement):
                    self.root_elements.append(e)
                else:
                    raise Exception('Element is not an ApiJsonBodyElement object')

    def to_dict(self)->dict:
        result = dict()
        if len(self.root_elements) > 0:
            for e in self.root_elements:
                d = e.to_dict()
                key0 = list(d.keys())[0]
                result[key0] = d[key0]
        return result

    def to_json(self)->str:
        return json.dumps(self.to_dict())

    def replace_value(self, path: str, value: object=None):
        """
            Given the following example:

                >>> from odc_pycommons.models import *
                >>> e2 = ApiJsonBodyElement(field_name='b', start_value='2')
                >>> e1 = ApiJsonBodyElement(field_name='a', start_value=e2)
                >>> e3 = ApiJsonBodyElement(field_name='c', start_value='3')
                >>> b = ApiJsonBody(root_elements=[e1, e3])
                >>> b.to_dict()
                {'a': {'b': '2'}, 'c': '3'}
        
            To replace the value of e3:

                >>> b.replace_value(path='c', value='new value 1')

            To replace the value of e2:

                >>> b.replace_value(path='a.b', value='new value 2')

            Now, you should get:

                >>> b.to_dict()
                {'a': {'b': 'new value 2'}, 'c': 'new value 1'}

        """
        pass

    def find_path_for_value(self, value: object)->list:
        """
            Find all paths that contain a certain value

            Example:

                >>> from odc_pycommons.models import *
                >>> e2 = ApiJsonBodyElement(field_name='b', start_value='2')
                >>> e1 = ApiJsonBodyElement(field_name='a', start_value=e2)
                >>> e3 = ApiJsonBodyElement(field_name='c', start_value='3')
                >>> e4 = ApiJsonBodyElement(field_name='d', start_value='x')
                >>> e5 = ApiJsonBodyElement(field_name='e', start_value='x')
                >>> b = ApiJsonBody(root_elements=[e1, e3])
                >>> b.find_path_for_value(value='3')
                ['c']
                >>> b.find_path_for_value(value='2')
                ['a.b']
                >>> b.find_path_for_value(value='x')
                ['d', 'e']
        """
        pass


# EOF
