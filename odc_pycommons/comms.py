# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

from odc_pycommons.models import CommsRequest, CommsRestFulRequest, CommsResponse
from odc_pycommons import DEBUG
from odc_pycommons import OculusDLogger
import yaml
import json
import urllib.request
import urllib.parse
#import http.client
import traceback
import os


CURRENT_API_DEF_URI = os.getenv('API_DEF_URI', 'https://raw.githubusercontent.com/oculusd/openapi-definitions/master/oculusd-api.yml')
L = OculusDLogger()
api_def_yaml_as_dict = None


def _prepare_comms_response_on_http_response(
    response_code: int=0,
    response: CommsResponse=None
)->CommsResponse:
    if response is None:
        response = CommsResponse(
        is_error=True,
        response_code=-2,
        response_code_description='Unknown error',
        response_data=None,
        trace_id=None
    )   
    if response_code > 199 and response_code < 300:
        response.is_error = False
        response.response_code = response_code
        response.response_code_description = 'Ok'
    elif response_code < 1:
        return response
    elif (response_code < 200 or response_code > 299) and response_code < 600:
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
    except:                                                                                             # pragma: no cover
        traceback.print_exc()                                                                           # pragma: no cover
    return final_uri


def get(
    request: CommsRequest,
    user_agent: str=None,
    uri_parameters: dict=dict(),
    path_parameters: dict=dict(),
    bearer_token: str=None
)->CommsResponse:
    response = CommsResponse(
        is_error=True,
        response_code=-2,
        response_code_description='Unknown error',
        response_data=None,
        trace_id=request.trace_id
    )
    try:
        L.debug(message='debugging GET request')
        L.debug(message='request={}'.format(vars(request)))
        request_uri = request.uri
        debug_level = 0
        if DEBUG:                                                                                       # pragma: no cover
            debug_level = 9                                                                             # pragma: no cover
        if len(path_parameters) > 0:
            for path_parameter_name, path_parameter_value in path_parameters.items():
                if path_parameter_name in request_uri:
                    request_uri = request_uri.replace(path_parameter_name, path_parameter_value)
        req = urllib.request.Request(
            url=_parse_parameters_and_join_with_uri(
                uri=request_uri,
                uri_parameters=uri_parameters
            ),
            method='GET'
        )
        if bearer_token is not None:
            req.add_header(key='Authorization', val='Bearer {}'.format(bearer_token))
        L.debug(message='Final URI: {}'.format(request_uri))
        if user_agent is not None:
            req.add_header(key='User-Agent', val=user_agent)
            response.warnings.append('Using custom User-Agent: "{}"'.format(user_agent))
        handler = urllib.request.HTTPHandler(debuglevel=debug_level)
        if request.uri.lower().startswith('https:'):
            handler = urllib.request.HTTPSHandler(debuglevel=debug_level)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)
        L.debug(message='Entering urlopen call')
        with urllib.request.urlopen(req) as f:
            L.debug(message='Reading response')
            response_code = f.getcode()
            L.debug(message='response_code={}'.format(response_code))
            response = _prepare_comms_response_on_http_response(response_code=response_code, response=response)
            if response_code > 199 or response_code < 300:
                response.response_data = f.read()
                try:
                    response.response_data = response.response_data.decode('utf-8')
                except:                                                                                 # pragma: no cover
                    response.warnings.append('UTF-8 decoding failed. Response data is in BINARY')       # pragma: no cover
    except:                                                                                             # pragma: no cover
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))                                 # pragma: no cover
        response.is_error = True                                                                        # pragma: no cover
        response.response_code = -3                                                                     # pragma: no cover
        response.response_code_description = 'EXCEPTION: {}'.format(traceback.format_exc())             # pragma: no cover
    L.debug(message='response={}'.format(vars(response)))
    return response


def json_post(
    request: CommsRestFulRequest,
    user_agent: str=None,
    path_parameters: dict=dict(),
    bearer_token: str=None
)->CommsResponse:
    response = CommsResponse(
        is_error=True,
        response_code=-2,
        response_code_description='Unknown error',
        response_data=None,
        trace_id=request.trace_id
    )
    try:
        L.debug(message='debugging POST request')
        L.debug(message='request={}'.format(vars(request)))
        if request.data is not None:
            request_uri = request.uri
            if len(path_parameters) > 0:
                for path_parameter_name, path_parameter_value in path_parameters.items():
                    if path_parameter_name in request_uri:
                        request_uri = request_uri.replace(path_parameter_name, path_parameter_value)
            L.debug(message='Final URI: {}'.format(request_uri))
            if isinstance(request.data, dict):
                data_json = json.dumps(request.data)
                encoded_json = data_json.encode('utf-8')
                req = urllib.request.Request(url=request_uri, data=encoded_json, method='POST')
                req.add_header(key='Content-type', val='application/json')
                if bearer_token is not None:
                    req.add_header(key='Authorization', val='Bearer {}'.format(bearer_token))
                if user_agent is not None:
                    req.add_header(key='User-Agent', val=user_agent)
                    response.warnings.append('Using custom User-Agent: "{}"'.format(user_agent))
                L.debug(message='Entering urlopen call')
                with urllib.request.urlopen(req) as f:
                    response_code = f.getcode()
                    L.debug(message='response_code={}'.format(response_code))
                    response = _prepare_comms_response_on_http_response(response_code=response_code, response=response)
                    if response_code > 199 or response_code < 300:
                        response.response_data = f.read()
                        try:
                            response.response_data = response.response_data.decode('utf-8')
                        except:                                                                                         # pragma: no cover
                            response.warnings.append('UTF-8 decoding failed. Response data is in BINARY')               # pragma: no cover
            else:                                                                                                       # pragma: no cover
                response.response_code = -5                                                                             # pragma: no cover
                response.response_code_description = 'Expected a dictionary, but found "{}"'.format(type(request.data)) # pragma: no cover
        else:
            response.response_code = -6
            response.response_code_description = 'No data to post.'
            L.debug(message='No data to post')
    except:                                                                                                             # pragma: no cover
        L.error(message='EXCEPTION: {}'.format(traceback.format_exc()))                                                 # pragma: no cover
        response.is_error = True                                                                                        # pragma: no cover
        response.response_code = -3                                                                                     # pragma: no cover
        response.response_code_description = 'EXCEPTION: {}'.format(traceback.format_exc())                             # pragma: no cover
    L.debug(message='response={}'.format(vars(response)))                                                               # pragma: no cover
    return response


def get_oculusd_service_yaml(
    service_uri: str=CURRENT_API_DEF_URI,
    http_get_service_impl: object=get
)->dict:
    global api_def_yaml_as_dict
    try:
        if api_def_yaml_as_dict is not None:
            return api_def_yaml_as_dict
        api_def_comms_request = CommsRequest(uri=CURRENT_API_DEF_URI)
        api_def_request_responce = http_get_service_impl(request=api_def_comms_request, user_agent='Custom')
        api_def_yaml_as_dict = yaml.safe_load(api_def_request_responce.response_data)
        return api_def_yaml_as_dict
    except:                                                                                                             # pragma: no cover
        pass                                                                                                            # pragma: no cover
    raise Exception('Failed to retrieve OculusD Service Definition')                                                    # pragma: no cover


def get_service_uri(service_name: str, region: str=None, service_yaml_definition: dict=get_oculusd_service_yaml())->str:
    final_url = None
    base_url = api_def_yaml_as_dict['servers'][0]['url']
    selected_region = api_def_yaml_as_dict['servers'][0]['variables']['region']['default']
    if region is not None:
        if isinstance(region, str):
            if region in api_def_yaml_as_dict['servers'][0]['variables']['region']['enum']:
                selected_region = region
    if '{region}' in base_url:
        base_url = base_url.replace('{region}', selected_region)

    service_name_found = False
    for path, path_data in api_def_yaml_as_dict['paths'].items():
        if 'x-descriptive-name' in path_data:
            if path_data['x-descriptive-name'] == service_name:
                service_name_found = True
                service_path = path
                if 'x-env-override' in path_data:
                    service_path = os.getenv(path_data['x-env-override'], path)
                final_url = '{}{}'.format(base_url, service_path)
    if service_name_found is False:
        raise Exception('service_name not found')
    if final_url is not None:
        return final_url
    raise Exception('Service URI failure')


# EOF
