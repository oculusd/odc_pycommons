# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. Please refer to the LICENSE.txt file for full license information. Licensed in terms of the GPLv3 License.

from odc_pycommons.models import CommsRequest, CommsRestFulRequest, CommsResponse
import json
import urllib.request
import urllib.parse
import traceback
import os


SERVICE_URIS = {
    'Regions': [
        'us1',
    ],
    'DefaultRegion': 'us1',
    'Services': {
        'RegisterRootAccount': {
            'us1': 'https://data-us1.oculusd.com/register/root-account',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_RRA',
        },
        'Ping': {
            'us1': 'https://data-us1.oculusd.com/api/ping',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_P',
        },
        'RootAccountActivation': {
            'us1': 'https://data-us1.oculusd.com/account/<<root_account_id>>/activate',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_RAA',
        },
        'RootAccountAuthentication': {
            'us1': 'https://data-us1.oculusd.com/account/<<root_account_id>>/authenticate',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_RAUTH',
        },
        'RegisterThing': {
            'us1': 'https://data-us1.oculusd.com/register/thing/<<token>>',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_RT',
        },
        'GetThingToken': {
            'us1': 'https://data-us1.oculusd.com/thing/<<thing_id>>/<<user_token>>/create-thing-token',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_GTT',
        },
        'LogSingleThing': {
            'us1': 'https://data-us1.oculusd.com/data/log/thing-data/<<user_token>>/<<thing_token>>',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_LST',
        },
        'RootAccountReset': {
            'us1': 'https://data-us1.oculusd.com/account/<<root_account_id>>/reset',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_RAR',
        },
        'RootAccountThingSensorQuery': {
            'us1': '/data/query/thing-sensor-data/<<user_token>>/<<thing_token>>/<sensor_name>>',
            'ENV_OVERRIDE': 'OCULUSD_APIURI_RATSQ',
        },
    }
}


def get_service_uri(service_name: str, region: str=None)->str:
    selected_region = SERVICE_URIS['DefaultRegion']
    if service_name not in SERVICE_URIS['Services']:
        raise Exception('service_name not found')
    if 'ENV_OVERRIDE' in SERVICE_URIS['Services'][service_name]:
        temp = os.getenv(SERVICE_URIS['Services'][service_name]['ENV_OVERRIDE'], None)
        if temp is not None:
            return temp
    if region is not None:
        if isinstance(region, str):
            if region in SERVICE_URIS['Regions']:
                selected_region = region
    if selected_region in SERVICE_URIS['Services'][service_name]:
        return SERVICE_URIS['Services'][service_name][selected_region]
    raise Exception('Service URI failure')


def _prepare_response_on_response(
    response_code: int=0,
    response: CommsResponse=CommsResponse(
        is_error=True,
        response_code=-2,
        response_code_description='Unknown error',
        response_data=None,
        trace_id=None
    )
)->CommsResponse:
    if response_code > 199 or response_code < 300:
        response.is_error = False
        response.response_code = response_code
        response.response_code_description = 'Ok'
    elif response_code < 200 or response_code > 299:
        response.is_error = True
        response.response_code = response_code
        response.response_code_description = 'Refer to the appropriate HTTP error code: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes'
    else:
        response.is_error = True
        response.response_code = -4
        response.response_code_description = 'The command completed, but an unknown error occurred'
    return response


def _parse_parameters_and_join_with_uri(uri: str, uri_parameters: dict)->str:
    final_uri = uri
    try:
        if uri_parameters:
            if isinstance(uri_parameters, dict):
                if len(uri_parameters) > 0:
                    final_uri = '{}?{}'.format(
                        uri,
                        urllib.parse.urlencode(uri_parameters)
                    )
    except:
        traceback.print_exc()
    return final_uri


def get(
    request: CommsRequest,
    user_agent: str=None,
    uri_parameters: dict=dict()
)->CommsResponse:
    response = CommsResponse(
        is_error=True,
        response_code=-2,
        response_code_description='Unknown error',
        response_data=None,
        trace_id=request.trace_id
    )
    try:
        req = urllib.request.Request(
            url=_parse_parameters_and_join_with_uri(
                uri=request.uri,
                uri_parameters=uri_parameters
            ),
            method='GET'
        )
        if user_agent is not None:
            req.add_header(key='User-Agent', val=user_agent)
            response.warnings.append('Using custom User-Agent: "{}"'.format(user_agent))
        with urllib.request.urlopen(req) as f:
            response_code = f.getcode()
            response = _prepare_response_on_response(response_code=response_code, response=response)
            if response_code > 199 or response_code < 300:
                response.response_data = f.read()
                try:
                    response.response_data = response.response_data.decode('utf-8')
                except:
                    response.warnings.append('UTF-8 decoding failed. Response data is in BINARY')
    except:
        response.is_error = True
        response.response_code = -3
        response.response_code_description = 'EXCEPTION: {}'.format(traceback.format_exc())
    return response


def json_post(request: CommsRestFulRequest, user_agent: str=None)->CommsResponse:
    response = CommsResponse(
        is_error=True,
        response_code=-2,
        response_code_description='Unknown error',
        response_data=None,
        trace_id=request.trace_id
    )
    try:
        if request.data is not None:
            if isinstance(request.data, dict):
                data_json = json.dumps(request.data)
                encoded_json = data_json.encode('utf-8')
                req = urllib.request.Request(url=request.uri, data=encoded_json, method='POST')
                req.add_header(key='Content-type', val='application/json')
                if user_agent is not None:
                    req.add_header(key='User-Agent', val=user_agent)
                    response.warnings.append('Using custom User-Agent: "{}"'.format(user_agent))
                with urllib.request.urlopen(req) as f:
                    response_code = f.getcode()
                    response = _prepare_response_on_response(response_code=response_code, response=response)
                    if response_code > 199 or response_code < 300:
                        response.response_data = f.read()
                        try:
                            response.response_data = response.response_data.decode('utf-8')
                        except:
                            response.warnings.append('UTF-8 decoding failed. Response data is in BINARY')
            else:
                response.response_code = -5
                response.response_code_description = 'Expected a dictionary, but found "{}"'.format(type(request.data))
        else:
            response.response_code = -6
            response.response_code_description = 'No data to post.'
    except:
        response.is_error = True
        response.response_code = -3
        response.response_code_description = 'EXCEPTION: {}'.format(traceback.format_exc())
    return response

# EOF
