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
from odc_pycommons import OculusDLogger
from odc_pycommons import get_utc_timestamp


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


class SensorAxisState:
    """
        An Axis state is matched when a particular measured value matches a predertermined configured value.

        A severity is attached to each state and is used in the final logging of any events to assist further downstream processing of the severity.

        The eval_function must handle at least the following parameters:

            * state_config -> AwsSensorAxisState
            * input_value  -> Any value the measurement produced
            * event_logger -> OculusDLogger

        The eval_function must return a boolean True (the input value matched the state definition), or False (typically the default)

        Example scenario 1:
        ------------------
        
            You have a temperature sensor. You want to define three states: too_cold (temperatures below 50), desired (between 50 and below 75) and too_hot (75 and above)

            It is critical for you that the temperature is between 50 and 75. So, the desired state will have a severity of 0 while the other states will be set at anything >0, like 9

            A typical implementation could look like this:

                def temp_state_eval(state_config: AwsSensorAxisState, input_value: object, event_logger:OculusDLogger=OculusDLogger()):
                    if state_config.state_name == 'too_cold':
                        if input_value < 50:
                            event_logger.info(message='Stated "too_cold" matched condition')
                            return True
                    elif state_config.state_name == 'desired':
                        if input_value >= 50 and input_value < 75:
                            event_logger.info(message='Stated "desired" matched condition')
                            return True
                    elif state_config.state_name == 'too_hot':
                        if input_value >= 75:
                            event_logger.info(message='Stated "too_hot" matched condition')
                            return True
                    else:
                        event_logger.error(message='No states matched')
                    return False

                too_cold_state = AwsSensorAxisState(
                    state_name='too_cold',
                    state_type=int,
                    severity: int=9,
                    eval_function=temp_state_eval
                )
                too_hot_state = AwsSensorAxisState(
                    state_name='too_hot',
                    state_type=int,
                    severity: int=9,
                    eval_function=temp_state_eval
                )
                desired_state = AwsSensorAxisState(
                    state_name='desired',
                    state_type=int,
                    severity: int=0,
                    eval_function=temp_state_eval
                )

                # ... later, i=within this library, after a reading has been received, the reading will be matched against all defined states. 
                # Something like this might be an equivalent process:
                states = [too_cold_state, too_hot_state, desired_state]
                while True:
                    temp_reading = get_temp()   # dummy function... real world will work a little different. For now, pretend that an integer is returned
                    for state in states:
                        if state.evaluate_value(input_value=temp_reading) is True:
                            if state.severity > 0:
                                raise_the_alarm(state_definition=state, input_value=temp_reading) # Another dummy function used to demonstrate how you could raise an alarm..
                    time,sleep(60)
    """

    def __init__(
        self,
        state_name: str,
        state_type: object,
        state_value: object=None,
        severity: int=0,
        eval_function: object=None,
        event_logger: OculusDLogger=OculusDLogger()
    ):
        self.state_name = state_name
        self.state_type = state_type
        self.state_value = state_value
        self.severity = severity
        self.eval_function = None
        if callable(eval_function) is True:
            self.eval_function = eval_function
        self.event_logger = event_logger

    def evaluate_value(self, input_value: object)->bool:
        result = False
        try:
            # Attempt to run the supplied matcher function
            if self.eval_function is not None:
                result = self.eval_function(state_config=self, input_value=input_value, event_logger=self.event_logger)
                if isinstance(result, bool):
                    self.event_logger.info(message='eval_function returned "{}"'.format(result))
                else:
                    result = False  # reset
                    self.event_logger.error(message='eval_function returned a non-boolean value. Falling back to basic matching')
            # Fall back to basic match: if the input value matches the type and value, return True
            if input_value is None and self.state_type is None and self.state_value is None:
                result = True
                self.event_logger.info(message='State value "None" triggered by default state check')
            elif input_value is not None and self.state_type is not None and self.state_value is not None:
                if isinstance(input_value, self.state_type):
                    if input_value == self.state_value:
                        result = True
                        self.event_logger.info(message='State value "Match" triggered by default state check')
        except:
            self.event_logger.error(message='EXCEPTION: {}'.format(traceback.format_exc()))
        self.event_logger.info(message='Final State Check Result: {}'.format(result))
        return result


class StateAlert:

    def evaluate_state(
        self, 
        state: SensorAxisState,
        input_value: object=None,
        event_logger: OculusDLogger=OculusDLogger()
    ):
        try:
            if state.evaluate_value(input_value=input_value) is True:
                if state.severity > 0:
                    event_logger.error(message='STATE_ALERT: State "{}" alert with Severity "{}"'.format(state.state_name, sate.severity))
                else:
                    event_logger.info(message='STATE_ALERT: State "{}" alert with Severity "{}"'.format(state.state_name, sate.severity))
        except:
            event_logger.error(message='EXCEPTION: {}'.format(traceback.format_exc()))


class AwsSnsStateAlert(StateAlert):

    def __init__(self, sns_topic_arn, aws_sns_client: object):
        self.sns_topic_arn = sns_topic_arn
        self.aws_sns_client = aws_sns_client
        super().__init__()

    def evaluate_state(
        self, 
        state: SensorAxisState,
        input_value: object=None,
        event_logger: OculusDLogger=OculusDLogger()
    ):
        try:
            if state.evaluate_value(input_value=input_value) is True:
                if state.severity > 0:
                    event_logger.error(message='STATE_ALERT: State "{}" alert with Severity "{}"'.format(state.state_name, sate.severity))
                    input_value_abbreviated = '{}'.format(input_value)
                    if len(input_value_abbreviated) > 10:
                        input_value_abbreviated = '{}... (shortened)'.format(input_value_abbreviated[0:10])
                    response = self.aws_sns_client.publish(
                        TopicArn=self.sns_topic_arn,
                        Message='string',
                        Subject='[STATE_ALERT] {} - severity "{}"'.format(state.state_name, state.severity),
                        MessageStructure='OculusD State Alert: Input value "{}" triggered state with configured severity of "{}"'.format(input_value_abbreviated, state.severity)
                    )
                    event_logger.debug(message='response={}'.format(response))
                else:
                    event_logger.info(message='STATE_ALERT: State "{}" alert with Severity "{}"'.format(state.state_name, sate.severity))
        except:
            event_logger.error(message='EXCEPTION: {}'.format(traceback.format_exc()))


class ThingSensorAxis:

    def __init__(
        self,
        axis_name: str,
        axis_data_type: str='STRING',
        axis_states: list=list(),
        axis_state_alert_processor: StateAlert=StateAlert()
    ):
        self.axis_name = axis_name
        if axis_data_type not in AXIS_DATA_TYPES:
            raise Exception('Wrong data type. Must be one of {}'.format(list(AXIS_DATA_TYPES.keys())))
        self.axis_data_type = axis_data_type
        self.axis_states = list()
        if axis_states is not None:
            if isinstance(axis_states, list):
                if len(axis_states) > 0:
                    for axis_state in axis_states:
                        if axis_state is not None:
                            if isinstance(axis_state, SensorAxisState):
                                self.axis_states.append(axis_state)
                            else:
                                raise Exception('Expected an AwsSensorAxisState but got "{}"'.format(type(axis_state)))
                        else:
                            raise Exception('When supplied, axis state objects cannot be None')
        self.axis_state_alert_processor = axis_state_alert_processor
        self.last_reading_value = None
        self.last_reading_timestamp_utc = 0

    def record_axis_reading(self, reading_value: object, reading_timestamp: int=get_utc_timestamp()):
        self.last_reading_value = reading_value
        self.last_reading_timestamp_utc = reading_timestamp

    def to_dict(self, include_axis_state_definitions: bool=False, include_last_values: bool=False):
        return {
            'AxisName': self.axis_name,
            'AxisDataType': self.axis_data_type,
        }

    def to_json(self, include_axis_state_definitions: bool=False, include_last_values: bool=False):
        return json.dumps(self.to_dict(include_axis_state_definitions=include_axis_state_definitions, include_last_values=include_last_values))


class SensorStateReader:

    """
        This is the part a user must implement that reads actual data from a sensor...
    """

    def __init__(self, state_reader_name: str, event_logger: OculusDLogger=OculusDLogger()):
        self.state_reader_name = state_reader_name
        self.event_logger = event_logger

    def _check_all_states(self, axis_name: str, sensor_axis: list=list(), input_value: object=None, reading_timestamp: int=get_utc_timestamp()):
        for axis in sensor_axis:
            if axis_name == axis.axis_name:
                axis.record_axis_reading(reading_value=input_value, reading_timestamp=reading_timestamp)
                try:
                    for axis_state in axis.axis_states:
                        if axis_state.evaluate_value(input_value=input_value) is True:
                            axis.axis_state_alert_processor.evaluate_state(
                                state=axis_state,
                                input_value=input_value,
                                event_logger=self.event_logger
                            )
                except:
                    self.event_logger('EXCEPTION: {}'.format(traceback.format_exc()))

    def read_state(self, sensor_axis: list=list()):
        """
            Implementation guidelines
            =========================

            You need to add your code here that will retrieve a set of values for your defined axis.

            Then, when all is done, call _check_all_states() as such (assuming your Thing was defined as thing):

                class MyTemperatureSensorReader(SensorStateReader):

                    def __init__(self):
                        super().__init__(state_reader_name='MyTemperatureSensorReader')

                    def read_state(self, sensor_axis: list=list()):
                        # ... your implementation... safe each axis reading result in read_value
                        reading_timestamp = get_utc_timestamp()
                        for axis in sensor_axis:
                            read_value = my_sensor_axis_data_capture_function() # ..... read a value from your sensor axis
                            self._check_all_states(
                                axis_name=axis.axis_name,
                                sensor_axis=sensor_axis,
                                input_value=read_value,
                                reading_timestamp=reading_timestamp
                            )

        """
        self.event_logger.info('READ STATE TRIGGERED for "{}"'.format(self.state_reader_name))
        reading_timestamp = get_utc_timestamp()
        for axis in sensor_axis:
            read_value = None
            self._check_all_states(
                axis_name=axis.axis_name,
                sensor_axis=sensor_axis,
                input_value=read_value,
                reading_timestamp=reading_timestamp
            )


class ThingSensor:
    
    def __init__(
        self,
        sensor_name: str,
        axis_collection: list=list(),
        sensor_value_reader_implementation: SensorStateReader=SensorStateReader(state_reader_name='DefaultSensorStateReader'),
        sensor_reader_trigger_interval: int=300,
    ):
        self.sensor_name = sensor_name
        self.axis_collection = list()
        if len(axis_collection) > 0:
            for axis in axis_collection:
                if isinstance(axis, ThingSensorAxis):
                    self.axis_collection.append(axis)
                else:
                    raise Exception('Found an axis configuration that is not a AwsThingSensorAxis object!')
        if sensor_value_reader_implementation is None:
            raise Exception('sensor_value_reader_implementation must be defined')
        if not isinstance(sensor_value_reader_implementation, SensorStateReader):
            raise Exception('sensor_value_reader_implementation must be an instance of SensorStateReader')
        self.sensor_value_reader_implementation = sensor_value_reader_implementation
        self.sensor_reader_trigger_interval = sensor_reader_trigger_interval
        self.last_trigger_processed = 0

    def trigger_sensor_reading(self):
        now = get_utc_timestamp()
        if (now - self.last_trigger_processed) > self.sensor_reader_trigger_interval:
            self.last_trigger_processed = now
            self.sensor_value_reader_implementation.read_state(sensor_axis=self.axis_collection)

    def to_dict(self):
        axis_list = list()
        if len(self.axis_collection) > 0:
            for axis in self.axis_collection:
                axis_list.append(axis.to_dict())
        return {
            'SensorName': self.sensor_name,
            'SensorAxisCollection': axis_list,
            'SensorReader': {
                'SensorReaderTriggerInterval': self.sensor_reader_trigger_interval,
                'SensorReaderClassName': self.sensor_value_reader_implementation.__class__.__name__,
            },
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class Thing:

    def __init__(self, thing_name: str, sensors: list=list()):
        self.thing_name = thing_name
        self.sensors = list()
        self.sensor_names = list()
        if len(sensors) > 0:
            for sensor in sensors:
                if isinstance(sensor, ThingSensor):
                    if sensor.sensor_name in self.sensor_names:
                        raise Exception('Sensor named "{}" already defined'.format(sensor.sensor_name))
                    if len(sensor.axis_collection) > 0:
                        self.sensors.append(sensor)
                        self.sensor_names.append(sensor.sensor_name)
                    else:
                        raise Exception('Every sensor must have at least 1 axis define. Sensor "{}" appears to have none.'.format(sensor.sensor_name))
                else:
                    raise Exception('Found a sensor that is not a AwsThingSensor object!')

    def activate_sensor_triggers(self):
        if len(self.sensors) > 0:
            for sensor in self.sensors:
                sensor.trigger_sensor_reading()

    def to_dict(self):
        sensor_list = list()
        if len(self.sensors) > 0:
            for sensor in self.sensors:
                sensor_list.append(sensor.to_dict())
        return {
            'ThingName': self.thing_name,
            'ThingSensors': sensor_list,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class ThingGroup:

    def __init__(self, thing_group_name: str, things: list=list()):
        self.thing_group_name = thing_group_name
        self.things = list()
        if things is not None:
            if isinstance(things, list):
                if len(things) > 0:
                    for thing in things:
                        if isinstance(thing, Thing):
                            self.things.append(thing)

    def find_thing_by_name(self, thing_name: str)->Thing:
        if len(self.things) > 0:
            for thing in self.things:
                if thing.thing_name == thing_name:
                    return thing
        raise Exception('Thing named "{}" not found in group named "{}"'.format(thing_name, self.thing_group_name))

    def thing_exists(self, thing_name)->bool:
        if len(self.things) > 0:
            for thing in self.things:
                if thing.thing_name == thing_name:
                    return True
        return False

    def add_thing_to_group(self, thing: Thing):
        if self.thing_exists(thing_name=thing.thing_name) is False:
            self.things.append(thing)

    def to_dict(self)->dict:
        things_list = list()
        for thing in self.things:
            things_list.append(thing.to_dict())
        return {
            'ThingGroupName': self.thing_group_name,
            'Things': things_list,
        }

    def to_json(self)->str:
        return json.dumps(self.to_dict()) 



class AwsThing(Thing):

    def __init__(self, thing_name: str, thing_arn: str=None, sensors: list=list()):
        self.thing_arn = thing_arn
        super().__init__(thing_name=thing_name, sensors=sensors)

    def to_dict(self):
        sensor_list = list()
        if len(self.sensors) > 0:
            for sensor in self.sensors:
                sensor_list.append(sensor.to_dict())
        return {
            'ThingName': self.thing_name,
            'ThingArn': self.thing_arn,
            'ThingSensors': sensor_list,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class AwsThingGroup(ThingGroup):

    def __init__(self, thing_group_name: str, thing_group_arn: str, things: list=list()):
        self.thing_group_arn = thing_group_arn
        super().__init__(thing_group_name=thing_group_name)
        if things is not None:
            if isinstance(things, list):
                if len(things) > 0:
                    for thing in things:
                        if isinstance(thing, AwsThing):
                            self.things.append(thing)
    
    def get_thing_arn(self, thing_name: str)->str:
        if len(self.things) > 0:
            for thing in self.things:
                if thing.thing_name == thing_name:
                    return thing.thing_arn
        raise Exception('Thing named "{}" not found in group named "{}"'.format(thing_name, self.thing_group_name))

# EOF
