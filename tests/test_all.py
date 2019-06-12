# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""Testing all domain aggregates

Depends on the Python package "coverage"

Usage

::

    $ coverage run  --omit="*tests*,*venv*" -m tests.test_all
    $ coverage report -m
"""

import unittest
from tests.test_logging import TestOculusDLogger, TestGetUtcTimestamp
from tests.test_security import TestInitFunctions, TestEmailValidation, TestStringValidation, TestDataValidator, TestStringDataValidator, TestNumberDataValidator
from tests.test_persistence import TestGenericDataContainer, TestGenericIOProcessor, TestGenericIO, TestTextFileIO, TestValidateFileExistIOProcessor
from tests.test_comms import TestPrepareResponseOnResponse
from tests.test_comms import TestParseParametersAndJoinWithUri
from tests.test_comms import TestGetFunction
from tests.test_comms import TestJsonPostFunction
from tests.test_comms import TestGetOculusdServiceYaml
from tests.test_comms import TestGetServiceUri
from tests.test_models import TestCommsRequest
from tests.test_models import TestCommsRestFulRequest
from tests.test_models import TestCommsResponse
from tests.test_models import TestApiJsonBodyElement


def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestOculusDLogger('test_init'))
    suite.addTest(TestOculusDLogger('test_init_force_debug'))
    suite.addTest(TestOculusDLogger('test_verify_content_no_debug'))
    suite.addTest(TestOculusDLogger('test_verify_content_including_debug'))
    suite.addTest(TestOculusDLogger('test_empty_message_logging'))
    suite.addTest(TestOculusDLogger('test_warning_message_logging'))
    suite.addTest(TestOculusDLogger('test_error_message_logging'))

    suite.addTest(TestGetUtcTimestamp('test_get_utc_timestamp_without_decimal'))
    suite.addTest(TestGetUtcTimestamp('test_get_utc_timestamp_with_decimal'))

    suite.addTest(TestInitFunctions('test_mask_str1_defaults'))
    suite.addTest(TestInitFunctions('test_mask_none_string_defaults'))
    suite.addTest(TestInitFunctions('test_mask_str1_toggle_use_fixed_mask_length'))
    suite.addTest(TestInitFunctions('test_mask_str2_toggle_use_fixed_mask_length'))
    suite.addTest(TestInitFunctions('test_mask_none_str'))
    suite.addTest(TestInitFunctions('test_mask_empty_fixed_length_str'))
    suite.addTest(TestInitFunctions('test_mask_empty_set_length_str'))
    suite.addTest(TestInitFunctions('test_mask_empty_str_no_use_fixed_mask_length'))

    suite.addTest(TestEmailValidation('test_validation_valid_email_address'))
    suite.addTest(TestEmailValidation('test_validation_invalid_email_address_1'))
    suite.addTest(TestEmailValidation('test_validation_invalid_email_address_2'))
    suite.addTest(TestEmailValidation('test_validation_invalid_email_address_3'))

    suite.addTest(TestStringValidation('test_validate_string_short_str_defaults'))
    suite.addTest(TestStringValidation('test_validate_string_can_be_none_and_is_none'))
    suite.addTest(TestStringValidation('test_validate_string_can_not_be_none_and_is_none'))
    suite.addTest(TestStringValidation('test_validate_string_not_a_string_instance'))
    suite.addTest(TestStringValidation('test_validate_string_less_than_minimum_len'))
    suite.addTest(TestStringValidation('test_validate_string_greater_than_maximum_len'))
    suite.addTest(TestStringValidation('test_validate_string_does_not_start_with_alpha_but_with_space'))
    suite.addTest(TestStringValidation('test_validate_string_fail_to_contain_at_least_one_space'))
    suite.addTest(TestStringValidation('test_validate_string_contains_at_least_one_space'))

    suite.addTest(TestDataValidator('test_init_data_validator'))
    suite.addTest(TestDataValidator('test_validation_fails'))

    suite.addTest(TestStringDataValidator('test_init_string_data_validator'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_all_defaults'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_data_container_all_defaults'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_min_and_max_lengths'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_min_and_max_lengths_fail_string_to_short'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_min_and_max_lengths_fail_string_to_long'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_start_with_alpha'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_start_with_alpha_but_start_with_space'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_start_with_alpha_but_start_with_numeric'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_can_be_none_is_true'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_none_value_with_can_be_none_is_true'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_contain_at_least_one_space'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_none_value_with_contain_at_least_one_space_but_doesnt'))
    suite.addTest(TestStringDataValidator('test_string_data_validator_short_string_with_start_with_alpha_and_start_with_space'))

    suite.addTest(TestGenericDataContainer('test_init_generic_data_container'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_list'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_tuple'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_int'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_float'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_decimal'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_dict'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_unsupported_type'))
    suite.addTest(TestGenericDataContainer('test_init_generic_data_container_invalid_validator'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_dict_test01'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_dict_omit_key_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_dict_override_key_with_new_value'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_dict_with_custom_dict_data_validator'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_dict_with_custom_dict_data_validator_force_validation_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_dict_with_dict_validator_not_of_the_expected_type_must_raise_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_string_with_string_validator_and_invalid_string_must_raise_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_string_with_no_validator_and_valid_string'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_string_with_no_validator_and_valid_none_store'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_list_with_string_validator_and_valid_strings'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_list_with_string_validator_and_one_invalid_object_must_raise_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_list_no_validator_list_contains_various_types'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_tuple_with_string_validator_and_valid_strings'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_tuple_with_string_validator_and_null_data_expecting_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_tuple_with_string_validator_and_unsupported_data_expecting_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_tuple_with_string_validator_and_data_validation_fail_expecting_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_tuple_with_no_validator_and_valid_list'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_tuple_with_no_validator_and_valid_list_add_another_item_expecting_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_int_with_no_validator_and_valid_int'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_int_with_validator_and_invalid_int_value'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_int_with_no_validator_and_invalid_input_type'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_int_with_no_validator_and_valid_int_as_str'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_int_with_no_validator_and_valid_int_as_float'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_no_validator_and_valid_float'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_no_validator_and_valid_float_as_str'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_no_validator_and_valid_float_as_int'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_no_validator_and_invalid_input_type'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_validator_and_valid_float'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_validator_and_invalid_float_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_int_with_invalid_validator_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_float_with_invalid_validator_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_no_validator_and_valid_decimal'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_no_validator_and_valid_int'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_no_validator_and_valid_float'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_no_validator_and_valid_str'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_no_validator_and_invalid_input_type_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_validator_and_valid_decimal'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_validator_and_invalid_decimal_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_decimal_with_invalid_validator_and_valid_decimal_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_unsupported_data_type_expect_exception'))
    suite.addTest(TestGenericDataContainer('test_generic_data_container_string_with_string_validator_and_valid_string'))

    suite.addTest(TestGenericIOProcessor('test_init_generic_io_processor'))
    suite.addTest(TestGenericIOProcessor('test_generic_io_processor_process_expect_exception'))

    suite.addTest(TestGenericIO('test_init_generic_io'))
    suite.addTest(TestGenericIO('test_generic_io_read_unimplemented_exception'))
    suite.addTest(TestGenericIO('test_generic_io_write_unimplemented_exception'))

    suite.addTest(TestTextFileIO('test_init_text_file_io'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_read_without_cache'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_read_with_cache'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_read_with_cache_force_refresh'))
    suite.addTest(TestTextFileIO('test_text_file_io_multi_line_text_data_read_without_cache'))
    suite.addTest(TestTextFileIO('test_text_file_io_empty_text_data_read_without_cache'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_read_without_cache_with_read_processor'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_read_without_cache_with_invalid_read_processor_expect_no_changes_in_input_type'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write_dict_as_json'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write_list_as_string'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write_with_cache'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write_without_cache_with_write_processor'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write_without_cache_with_invalid_write_processor'))
    suite.addTest(TestTextFileIO('test_text_file_io_basic_text_data_write_without_cache'))

    suite.addTest(TestNumberDataValidator('test_init_number_data_validator'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_int_input_no_validator_params'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_int_input_with_validator_params_expect_pass'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_float_input_no_validator_params'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_float_input_with_validator_params_expect_pass'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_str_input_no_validator_params'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_str_input_with_validator_params_expect_pass'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_decimal_input_no_validator_params'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_decimal_input_with_validator_params_expect_pass'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_decimal_input_with_invalid_validator_params_expect_fail'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_decimal_input_with_validator_params_expect_fail_input_less_than_min_value'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_decimal_input_with_validator_params_expect_fail_input_greater_than_max_value'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_int_input_with_validator_params_expect_fail_input_less_than_min_value'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_int_input_with_validator_params_expect_fail_input_greater_than_max_value'))
    suite.addTest(TestNumberDataValidator('test_number_data_validator_invalid_number_expect_fail'))

    suite.addTest(TestValidateFileExistIOProcessor('test_init_validate_file_exists_io_processor'))
    suite.addTest(TestValidateFileExistIOProcessor('test_validate_file_exists_io_processor_test_file'))
    suite.addTest(TestValidateFileExistIOProcessor('test_validate_file_exists_io_processor_test_non_existing_file_expect_exception'))
    suite.addTest(TestValidateFileExistIOProcessor('test_validate_file_exists_io_processor_test_invalid_generic_data_container_expect_exception'))
    suite.addTest(TestValidateFileExistIOProcessor('test_validate_file_exists_io_processor_test_invalid_generic_data_container_value_type_expect_exception'))

    suite.addTest(TestPrepareResponseOnResponse('test_init_prepare_response_on_response'))
    suite.addTest(TestPrepareResponseOnResponse('test_success_response_200'))
    suite.addTest(TestPrepareResponseOnResponse('test_success_response_all'))
    suite.addTest(TestPrepareResponseOnResponse('test_http_errors_response_all'))
    suite.addTest(TestPrepareResponseOnResponse('test_unknown__response_700'))

    suite.addTest(TestParseParametersAndJoinWithUri('test_no_parameters_test'))
    suite.addTest(TestParseParametersAndJoinWithUri('test_one_parameters_test'))
    suite.addTest(TestParseParametersAndJoinWithUri('test_two_parameters_test'))
    suite.addTest(TestParseParametersAndJoinWithUri('test_three_parameters_test'))

    suite.addTest(TestGetFunction('test_local_server_basic_get_01'))
    suite.addTest(TestGetFunction('test_local_server_get_with_path_parameters'))
    suite.addTest(TestGetFunction('test_local_server_get_with_bearer_token_01'))

    suite.addTest(TestJsonPostFunction('test_local_server_basic_post_01'))
    suite.addTest(TestJsonPostFunction('test_local_server_post_with_path_parameters'))
    suite.addTest(TestJsonPostFunction('test_local_server_post_with_bearer_token_01'))
    suite.addTest(TestJsonPostFunction('test_local_server_post_with_user_agent_01'))
    suite.addTest(TestJsonPostFunction('test_local_server_post_fail_on_empty_request_body_01'))

    suite.addTest(TestGetOculusdServiceYaml('test_read_local_data'))
    suite.addTest(TestGetOculusdServiceYaml('test_get_oculusd_service_yaml'))

    suite.addTest(TestGetServiceUri('test_get_service_uri_ping_service_01'))
    suite.addTest(TestGetServiceUri('test_service_name_not_found_01'))

    suite.addTest(TestCommsRequest('test_init_comms_request_01'))
    suite.addTest(TestCommsRequest('test_init_comms_request_02'))
    suite.addTest(TestCommsRequest('test_init_fail_on_none_uri_01'))
    suite.addTest(TestCommsRequest('test_validate_valid_uri'))
    suite.addTest(TestCommsRequest('test_validate_fail_on_uri_as_int'))
    suite.addTest(TestCommsRequest('test_validate_fail_on_uri_to_short'))
    suite.addTest(TestCommsRequest('test_validate_warn_on_trace_id_not_string'))
    suite.addTest(TestCommsRequest('test_fail_on_dict_call'))

    suite.addTest(TestCommsRestFulRequest('test_init_comms_rest_ful_request_01'))
    suite.addTest(TestCommsRestFulRequest('test_validate_fail_on_data_is_none'))
    suite.addTest(TestCommsRestFulRequest('test_validate_fail_on_data_is_string'))
    suite.addTest(TestCommsRestFulRequest('test_restful_data_to_dict_from_dict'))
    suite.addTest(TestCommsRestFulRequest('test_restful_data_to_dict_from_list'))
    suite.addTest(TestCommsRestFulRequest('test_restful_data_to_dict_from_tuple'))
    suite.addTest(TestCommsRestFulRequest('test_restful_to_dict_invalid_data_type_produces_warning'))
    suite.addTest(TestCommsRestFulRequest('test_restful_data_to_json_from_dict'))

    suite.addTest(TestCommsResponse('test_init_default_comms_response'))
    suite.addTest(TestCommsResponse('test_fail_on_is_error_is_none'))
    suite.addTest(TestCommsResponse('test_fail_on_is_error_is_not_bool'))
    suite.addTest(TestCommsResponse('test_fail_on_response_code_is_none'))
    suite.addTest(TestCommsResponse('test_fail_on_response_code_is_not_int'))
    suite.addTest(TestCommsResponse('test_fail_on_response_code_description_is_not_str'))
    suite.addTest(TestCommsResponse('test_fail_on_response_data_is_not_str'))
    suite.addTest(TestCommsResponse('test_fail_on_trace_id_is_not_str'))
    suite.addTest(TestCommsResponse('test_init_default_comms_response_to_dict'))
    suite.addTest(TestCommsResponse('test_with_data_comms_response_to_dict'))
    suite.addTest(TestCommsResponse('test_with_data_comms_response_to_dict_data_as_tuple'))
    suite.addTest(TestCommsResponse('test_with_data_comms_response_to_dict_data_as_decimal'))

    suite.addTest(TestApiJsonBodyElement('test_simple_init_01'))
    suite.addTest(TestApiJsonBodyElement('test_simple_to_dict_01'))
    suite.addTest(TestApiJsonBodyElement('test_simple_to_json_01'))
    suite.addTest(TestApiJsonBodyElement('test_compound_init_01'))
    suite.addTest(TestApiJsonBodyElement('test_compound_to_dict_01'))
    suite.addTest(TestApiJsonBodyElement('test_compound_to_json_01'))
    suite.addTest(TestApiJsonBodyElement('test_fail_on_none_value_01'))
    suite.addTest(TestApiJsonBodyElement('test_fail_on_none_value_02'))
    suite.addTest(TestApiJsonBodyElement('test_none_value_to_dict_01'))
    suite.addTest(TestApiJsonBodyElement('test_none_value_to_json_01'))
    suite.addTest(TestApiJsonBodyElement('test_set_value_01'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

# EOF
