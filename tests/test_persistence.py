# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run --omit="odc_pycommons/__init__.py","odc_pycommons/security.py" -m tests.test_persistence
    $ coverage report -m
"""

import unittest
from odc_pycommons.persistence import GenericDataContainer, GenericIOProcessor, GenericIO, TextFileIO, ValidateFileExistIOProcessor
from decimal import Decimal
from odc_pycommons.security import DataValidator, L, StringDataValidator, NumberDataValidator
from datetime import datetime
import os
import json


class DictValueNotNoneDataValidator(DataValidator):
    def __init__(self, logger=L):
        self.logger = logger

    def validate(self, data: object, **kwarg)->bool:
        if data is not None:
            return True
        self.logger.error('Data value must be set')
        return False


class TextMultiplierGenericIOProcessor(GenericIOProcessor):

    def __init__(self):
        super().__init__()

    def process(self, data: GenericDataContainer, **kwarg):
        multiplier = 2
        if 'multiplier' in kwarg:
            multiplier = kwarg['multiplier']
        result_generic_data_container = GenericDataContainer(result_set_name='TEST', data_type=str)
        if 'result_generic_data_container' in kwarg:
            result_generic_data_container = kwarg['result_generic_data_container']
        result_generic_data_container.store(data=data.data*multiplier)


class TestGenericDataContainer(unittest.TestCase):

    def setUp(self):
        pass
        
    def test_init_generic_data_container(self):
        gdc = GenericDataContainer(result_set_name='Test')
        self.assertIsNotNone(gdc)
        self.assertIsInstance(gdc, GenericDataContainer)
        self.assertEqual('Test', gdc.result_set_name)
        self.assertIsInstance(gdc.data_type, type)
        self.assertEqual('str', gdc.data_type.__name__)
        self.assertIsNone(gdc.data_validator)

    def test_init_generic_data_container_list(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=list)
        self.assertEqual('list', gdc.data_type.__name__)

    def test_init_generic_data_container_tuple(self):
        # NOTE: Before a tuple is added (store() called), the data_type must be a list... Just roll with it!
        gdc = GenericDataContainer(result_set_name='Test', data_type=list)
        self.assertEqual('list', gdc.data_type.__name__)

    def test_init_generic_data_container_int(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int)
        self.assertEqual('int', gdc.data_type.__name__)

    def test_init_generic_data_container_float(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float)
        self.assertEqual('float', gdc.data_type.__name__)

    def test_init_generic_data_container_decimal(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal)
        self.assertEqual('Decimal', gdc.data_type.__name__)

    def test_init_generic_data_container_dict(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=dict)
        self.assertEqual('dict', gdc.data_type.__name__)

    def test_init_generic_data_container_unsupported_type(self):
        with self.assertRaises(Exception):
            gdc = GenericDataContainer(result_set_name='Test', data_type=self.__class__)

    def test_init_generic_data_container_invalid_validator(self):
        with self.assertRaises(Exception):
            gdc = GenericDataContainer(result_set_name='Test', data_validator='This must fail!')

    def test_generic_data_container_dict_test01(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=dict)
        self.assertEqual('dict', gdc.data_type.__name__)
        d = {
            'TestKey1': 1001,
            'TestKey2': 'Test Value',
            'TestKey3': Decimal('100'),
        }
        item_nr = 0
        for key, val in d.items():
            item_nr = item_nr + 1
            result = gdc.store(data=val, key=key)
            self.assertEqual(item_nr, result, 'Key "{}" failed to be added'.format(key))
            self.assertTrue(key in gdc.data, 'Key "{}" not found'.format(key))
        self.assertEqual(d['TestKey1'], gdc.data['TestKey1'])
        self.assertEqual(d['TestKey2'], gdc.data['TestKey2'])
        self.assertIsInstance(d['TestKey3'], Decimal)

    def test_generic_data_container_dict_omit_key_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=dict)
        with self.assertRaises(Exception):
            gdc.store(data='Unimportant Data')
    
    def test_generic_data_container_dict_override_key_with_new_value(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=dict)
        self.assertEqual('dict', gdc.data_type.__name__)
        d = {
            'TestKey1': 1001,
            'TestKey2': 'Test Value',
            'TestKey3': Decimal('100'),
        }
        for key, val in d.items():
            result = gdc.store(data=val, key=key)
        result = gdc.store(data='New Value', key='TestKey1')
        self.assertTrue(result == 3)
        self.assertEqual('New Value', gdc.data['TestKey1'])

    def test_generic_data_container_dict_with_custom_dict_data_validator(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=dict, data_validator=DictValueNotNoneDataValidator())
        self.assertEqual('dict', gdc.data_type.__name__)
        d = {
            'TestKey1': 1001,
            'TestKey2': 'Test Value',
            'TestKey3': Decimal('100'),
        }
        item_nr = 0
        for key, val in d.items():
            item_nr = item_nr + 1
            result = gdc.store(data=val, key=key)
            self.assertEqual(item_nr, result, 'Key "{}" failed to be added'.format(key))
            self.assertTrue(key in gdc.data, 'Key "{}" not found'.format(key))
        self.assertEqual(d['TestKey1'], gdc.data['TestKey1'])
        self.assertEqual(d['TestKey2'], gdc.data['TestKey2'])
        self.assertIsInstance(d['TestKey3'], Decimal)
    
    def test_generic_data_container_dict_with_custom_dict_data_validator_force_validation_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=dict, data_validator=DictValueNotNoneDataValidator())
        self.assertEqual('dict', gdc.data_type.__name__)
        d = {
            'TestKey1': 1001,
            'TestKey2': 'Test Value',
            'TestKey3': Decimal('100'),
        }
        item_nr = 0
        for key, val in d.items():
            item_nr = item_nr + 1
            result = gdc.store(data=val, key=key)
        with self.assertRaises(Exception):
            gdc.store(data=None, key='TheInfamousAnyKey')

    def test_generic_data_container_dict_with_dict_validator_not_of_the_expected_type_must_raise_exception(self):
        with self.assertRaises(Exception):
            gdc = GenericDataContainer(result_set_name='Test', data_type=dict, data_validator='Definitely an invalid validator instance!')

    def test_generic_data_container_string_with_string_validator_and_invalid_string_must_raise_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=str, data_validator=StringDataValidator())
        input_str = ' abc'
        with self.assertRaises(Exception):
            gdc.store(data=input_str, start_with_alpha=True)

    def test_generic_data_container_string_with_string_validator_and_valid_string(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=str, data_validator=StringDataValidator())
        input_str = 'abc'
        gdc.store(data=input_str, start_with_alpha=True)
        self.assertEqual(gdc.data, 'abc')

    def test_generic_data_container_string_with_no_validator_and_valid_string(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=str)
        gdc.store(data='abc')
        self.assertIsNotNone(gdc.data)
        self.assertIsInstance(gdc.data, str)
        self.assertEqual('abc', gdc.data)

    def test_generic_data_container_string_with_no_validator_and_valid_none_store(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=str)
        gdc.store(data=None)
        self.assertIsNone(gdc.data)

    def test_generic_data_container_list_with_string_validator_and_valid_strings(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=list, data_validator=StringDataValidator())
        l = ['Item 1', 'Item 2']
        qty = 0
        for item in l:
            qty = qty + 1
            result = gdc.store(data=item, start_with_alpha=False)
            self.assertEqual(qty, result, 'Item "{}" failed to be stored'.format(qty))

    def test_generic_data_container_list_with_string_validator_and_one_invalid_object_must_raise_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=list, data_validator=StringDataValidator())
        l = ['Item 1', 1, 'This item will be ignored']
        result = gdc.store(data=l[0], start_with_alpha=False)
        self.assertEqual(1, result)
        with self.assertRaises(Exception):
            result = gdc.store(data=l[1], start_with_alpha=False)

    def test_generic_data_container_list_no_validator_list_contains_various_types(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=list)
        l = ['Item 1', 1, Decimal('0.0')]
        qty = 0
        for item in l:
            qty = qty + 1
            result = gdc.store(data=item, start_with_alpha=False)
            self.assertEqual(qty, result, 'Item "{}" failed to be stored'.format(qty))

    def test_generic_data_container_tuple_with_string_validator_and_valid_strings(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=tuple, data_validator=StringDataValidator())
        l = ('Item 1', 'Item 2', )
        result = gdc.store(data=l, start_with_alpha=False)
        self.assertEqual(len(l), result, 'Item "{}" failed to be stored'.format(len(l)))

    def test_generic_data_container_tuple_with_string_validator_and_null_data_expecting_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=tuple, data_validator=StringDataValidator())
        with self.assertRaises(Exception):
            gdc.store(data=None, start_with_alpha=False)

    def test_generic_data_container_tuple_with_string_validator_and_unsupported_data_expecting_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=tuple, data_validator=StringDataValidator())
        with self.assertRaises(Exception):
            gdc.store(data='This must fail', start_with_alpha=False)

    def test_generic_data_container_tuple_with_string_validator_and_data_validation_fail_expecting_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=tuple, data_validator=StringDataValidator())
        l = ('Item 1', 'Item 2', 3, )
        with self.assertRaises(Exception):
            gdc.store(data=l, start_with_alpha=False)

    def test_generic_data_container_tuple_with_no_validator_and_valid_list(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=tuple)
        l = ['Item 1', 'Item 2', ]
        result = gdc.store(data=l, start_with_alpha=False)
        self.assertEqual(len(l), result, 'Item "{}" failed to be stored'.format(len(l)))

    def test_generic_data_container_tuple_with_no_validator_and_valid_list_add_another_item_expecting_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=tuple)
        l = ['Item 1', 'Item 2', ]
        l2 = ['Item 3', 'Item 4', ]
        result = gdc.store(data=l, start_with_alpha=False)
        with self.assertRaises(Exception):
            gdc.store(data=l2, start_with_alpha=False)

    def test_generic_data_container_int_with_no_validator_and_valid_int(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int)
        l = 1001
        result = gdc.store(data=l)
        self.assertEqual(1, result)

    def test_generic_data_container_int_with_validator_and_invalid_int_value(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int, data_validator=NumberDataValidator())
        l = 1001
        with self.assertRaises(Exception):
            gdc.store(data=l, min_value=2000, max_value=3000)

    def test_generic_data_container_int_with_no_validator_and_invalid_input_type(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int, data_validator=NumberDataValidator())
        l = 1001
        with self.assertRaises(Exception):
            gdc.store(data=Decimal(l), min_value=2000, max_value=3000)

    def test_generic_data_container_int_with_no_validator_and_valid_int_as_str(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int)
        l = '1001'
        result = gdc.store(data=l)
        self.assertEqual(1, result)

    def test_generic_data_container_int_with_no_validator_and_valid_int_as_float(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int)
        l = 1001.0
        result = gdc.store(data=l)
        self.assertEqual(1, result)

    def test_generic_data_container_float_with_no_validator_and_valid_float(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float)
        l = 1001.01
        result = gdc.store(data=l)
        self.assertEqual(1, result)

    def test_generic_data_container_float_with_no_validator_and_valid_float_as_str(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float)
        l = '1001.01'
        result = gdc.store(data=l)
        self.assertEqual(1, result)

    def test_generic_data_container_float_with_no_validator_and_valid_float_as_int(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float)
        l = 1001
        result = gdc.store(data=l)
        self.assertEqual(1, result)

    def test_generic_data_container_float_with_no_validator_and_invalid_input_type(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float)
        l = Decimal(1001)
        with self.assertRaises(Exception):
            gdc.store(data=l)

    def test_generic_data_container_float_with_validator_and_valid_float(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float, data_validator=NumberDataValidator())
        l = 1001.001
        result = gdc.store(data=l, min_value=0.0, max_value=9999.0)
        self.assertEqual(1, result)

    def test_generic_data_container_float_with_validator_and_invalid_float_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float, data_validator=NumberDataValidator())
        l = 1001.001
        with self.assertRaises(Exception):
            gdc.store(data=l, min_value=5555.0, max_value=9999.0)

    def test_generic_data_container_int_with_invalid_validator_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=int, data_validator=StringDataValidator())
        l = 1001
        with self.assertRaises(Exception):
            gdc.store(data=l, min_value=0, max_value=3000)

    def test_generic_data_container_float_with_invalid_validator_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=float, data_validator=StringDataValidator())
        l = 1001.001
        with self.assertRaises(Exception):
            gdc.store(data=l, min_value=0.0, max_value=3000.0)

    def test_generic_data_container_decimal_with_no_validator_and_valid_decimal(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal)
        l = Decimal(1001.01)
        result = gdc.store(data=l)
        self.assertEqual(1, result)
        self.assertEqual(0, l.compare(gdc.data))

    def test_generic_data_container_decimal_with_no_validator_and_valid_int(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal)
        l = 1001
        result = gdc.store(data=l)
        self.assertEqual(1, result)
        self.assertEqual(0, Decimal(l).compare(gdc.data))

    def test_generic_data_container_decimal_with_no_validator_and_valid_float(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal)
        l = 1001.001
        result = gdc.store(data=l)
        self.assertEqual(1, result)
        self.assertEqual(0, Decimal(l).compare(gdc.data))

    def test_generic_data_container_decimal_with_no_validator_and_valid_str(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal)
        l = '1001.005'
        result = gdc.store(data=l)
        self.assertEqual(1, result)
        self.assertEqual(0, Decimal(l).compare(gdc.data))

    def test_generic_data_container_decimal_with_no_validator_and_invalid_input_type_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal)
        l = datetime.now()
        with self.assertRaises(Exception):
            gdc.store(data=l)

    def test_generic_data_container_decimal_with_validator_and_valid_decimal(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal, data_validator=NumberDataValidator())
        l = Decimal(1001.01)
        result = gdc.store(data=l, min_value=Decimal(0.0), max_value=Decimal(9999.0))
        self.assertEqual(1, result)
        self.assertEqual(0, l.compare(gdc.data))

    def test_generic_data_container_decimal_with_validator_and_invalid_decimal_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal, data_validator=NumberDataValidator())
        l = Decimal(1001.01)
        with self.assertRaises(Exception):
            gdc.store(data=l, min_value=Decimal(8888.0), max_value=Decimal(9999.0))

    def test_generic_data_container_decimal_with_invalid_validator_and_valid_decimal_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal, data_validator=StringDataValidator())
        l = Decimal(1001.01)
        with self.assertRaises(Exception):
            gdc.store(data=l, min_value=Decimal(0.0), max_value=Decimal(9999.0))

    def test_generic_data_container_unsupported_data_type_expect_exception(self):
        with self.assertRaises(Exception):
            gdc = GenericDataContainer(result_set_name='Test', data_type=datetime)


class TestGenericIOProcessor(unittest.TestCase):

    def test_init_generic_io_processor(self):
        giop = GenericIOProcessor()
        self.assertIsNotNone(giop)
        self.assertIsInstance(giop, GenericIOProcessor)
        self.assertIsNotNone(giop.logger)

    def test_generic_io_processor_process_expect_exception(self):
        giop = GenericIOProcessor()
        gdc = GenericDataContainer(result_set_name='Test', data_type=Decimal, data_validator=NumberDataValidator())
        l = Decimal(1001.01)
        result = gdc.store(data=l, min_value=Decimal(0.0), max_value=Decimal(9999.0))
        self.assertEqual(1, result)
        with self.assertRaises(Exception):
            giop.process(data=gdc)


class TestGenericIO(unittest.TestCase):

    def test_init_generic_io(self):
        gio = GenericIO(uri='a_file.txt')
        self.assertIsNotNone(gio)
        self.assertIsInstance(gio, GenericIO)
        self.assertEqual('a_file.txt', gio.uri)

    def test_generic_io_read_unimplemented_exception(self):
        gio = GenericIO(uri='a_file.txt')
        with self.assertRaises(Exception):
            gio.read()

    def test_generic_io_write_unimplemented_exception(self):
        gio = GenericIO(uri='a_file.txt')
        gdc = GenericDataContainer(data_type=str)
        gdc.store(data='Some Data')
        with self.assertRaises(Exception):
            gio.write(data=gdc)


class TestTextFileIO(unittest.TestCase):

    def tearDown(self):
        if os.path.isfile('READ_TEST'):
            os.remove('READ_TEST')
        if os.path.isfile('WRITE_TEST'):
            os.remove('WRITE_TEST')

    def test_init_text_file_io(self):
        tfio = TextFileIO(file_folder_path='.', file_name='TEST')
        self.assertIsNotNone(tfio)
        self.assertIsInstance(tfio, TextFileIO)
        self.assertEqual('.{}TEST'.format(os.sep), tfio.uri)
        self.assertEqual(0, tfio.cached_data_timestamp)
        self.assertIsNone(tfio.cached_data)
        self.assertEqual(900, tfio.cache_max_age)
        self.assertFalse(tfio.enable_cache)

    def test_text_file_io_basic_text_data_read_without_cache(self):
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST')
        text_data = 'TEST'
        with open('READ_TEST', 'w') as f:
            f.write(text_data)
        gdc = tfio.read()
        self.assertIsNotNone(gdc)
        self.assertIsInstance(gdc, GenericDataContainer)
        self.assertIsNotNone(gdc.data)
        self.assertEqual('TEST', gdc.data)

    def test_text_file_io_basic_text_data_write_without_cache(self):
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST')
        gdc = GenericDataContainer(result_set_name=tfio.uri, data_type=str)
        gdc.store(data='Some More Test Data')
        tfio.write(data=gdc)
        with open('WRITE_TEST', 'r') as f:
            text_data = f.readline()
            self.assertIsNotNone(text_data)
            self.assertIsInstance(text_data, str)
            self.assertEqual('Some More Test Data', text_data)

    def test_text_file_io_basic_text_data_read_with_cache(self):
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST', enable_cache=True)
        text_data = 'TEST'
        with open('READ_TEST', 'w') as f:
            f.write(text_data)
        gdc = tfio.read()
        self.assertIsNotNone(gdc)
        self.assertIsInstance(gdc, GenericDataContainer)
        self.assertIsNotNone(gdc.data)
        self.assertEqual('TEST', gdc.data)
        self.assertTrue(os.path.isfile('READ_TEST'))
        if os.path.isfile('READ_TEST'):
            os.remove('READ_TEST')
        self.assertFalse(os.path.isfile('READ_TEST'))
        gdc_cached_value = tfio.read()
        self.assertIsNotNone(gdc_cached_value)
        self.assertIsInstance(gdc_cached_value, GenericDataContainer)
        self.assertIsNotNone(gdc_cached_value.data)
        self.assertEqual('TEST', gdc_cached_value.data)

    def test_text_file_io_basic_text_data_read_with_cache_force_refresh(self):
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST', enable_cache=True)
        text_data = 'TEST'
        with open('READ_TEST', 'w') as f:
            f.write(text_data)
        gdc = tfio.read()
        self.assertIsNotNone(gdc)
        self.assertIsInstance(gdc, GenericDataContainer)
        self.assertIsNotNone(gdc.data)
        self.assertEqual('TEST', gdc.data)
        if os.path.isfile('READ_TEST'):
            os.remove('READ_TEST')
        with open('READ_TEST', 'w') as f:
            f.write('Brand New Data')
        self.assertTrue(os.path.isfile('READ_TEST'))
        gdc_cached_refreshed_value = tfio.read(force=True)
        self.assertIsNotNone(gdc_cached_refreshed_value)
        self.assertIsInstance(gdc_cached_refreshed_value, GenericDataContainer)
        self.assertIsNotNone(gdc_cached_refreshed_value.data)
        self.assertEqual('Brand New Data', gdc_cached_refreshed_value.data)

    def test_text_file_io_multi_line_text_data_read_without_cache(self):
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST')
        text_data = 'TEST\n123\nAgain'
        with open('READ_TEST', 'w') as f:
            f.write(text_data)
        gdc = tfio.read()
        self.assertIsNotNone(gdc)
        self.assertIsInstance(gdc, GenericDataContainer)
        self.assertIsNotNone(gdc.data)
        self.assertEqual('TEST\n123\nAgain', gdc.data)

    def test_text_file_io_empty_text_data_read_without_cache(self):
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST')
        with open('READ_TEST', 'w') as f:
            f.write('')
        gdc = tfio.read()
        self.assertIsNotNone(gdc)
        self.assertIsInstance(gdc, GenericDataContainer)
        self.assertIsNotNone(gdc.data)
        self.assertEqual('', gdc.data)

    def test_text_file_io_basic_text_data_read_without_cache_with_read_processor(self):
        iop = TextMultiplierGenericIOProcessor()
        gdc_result = GenericDataContainer(result_set_name='Result', data_type=str)
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST')
        text_data = '*'
        with open('READ_TEST', 'w') as f:
            f.write(text_data)
        tfio.read(read_processor=iop, multiplier=8, result_generic_data_container=gdc_result)
        self.assertIsNotNone(gdc_result)
        self.assertIsInstance(gdc_result, GenericDataContainer)
        self.assertIsNotNone(gdc_result.data)
        self.assertEqual('********', gdc_result.data)

    def test_text_file_io_basic_text_data_read_without_cache_with_invalid_read_processor_expect_no_changes_in_input_type(self):
        iop = 'Invalid Processor'
        gdc_result = {'Test': 123}
        tfio = TextFileIO(file_folder_path='.', file_name='READ_TEST')
        text_data = '*'
        with open('READ_TEST', 'w') as f:
            f.write(text_data)
        tfio.read(read_processor=iop, multiplier=8, result_generic_data_container=gdc_result)
        self.assertIsNotNone(gdc_result)
        self.assertIsInstance(gdc_result, dict)
        self.assertEqual(1, len(gdc_result))
        self.assertTrue('Test' in gdc_result)
        self.assertEqual(123, gdc_result['Test'])

    def test_text_file_io_basic_text_data_write(self):
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST')
        text_data = 'TEST'
        gdp = GenericDataContainer(data_type=str)
        gdp.store(data=text_data)
        tfio.write(data=gdp)
        result = ''
        lines = list()
        with open('WRITE_TEST', 'r') as f:
            lines = f.readlines()
        result = ''.join(lines)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual('TEST', result)

    def test_text_file_io_basic_text_data_write_dict_as_json(self):
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST')
        gdp = GenericDataContainer(data_type=dict)
        gdp.store(data=True, key='DidItWork')
        tfio.write(data=gdp)
        lines = list()
        with open('WRITE_TEST', 'r') as f:
            lines = f.readlines()
        result = json.loads(''.join(lines))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual(1, len(result))
        self.assertTrue('DidItWork' in result)
        self.assertIsInstance(result['DidItWork'], bool)
        self.assertTrue(result['DidItWork'])

    def test_text_file_io_basic_text_data_write_list_as_string(self):
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST')
        gdp = GenericDataContainer(data_type=list)
        gdp.store(data=1)
        gdp.store(data=2)
        gdp.store(data=3)
        tfio.write(data=gdp)
        lines = list()
        with open('WRITE_TEST', 'r') as f:
            lines = f.readlines()
        result = ''.join(lines)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('[' in result)
        self.assertTrue(']' in result)
        self.assertTrue('1' in result)
        self.assertTrue('2' in result)
        self.assertTrue('3' in result)
        self.assertTrue(',' in result)

    def test_text_file_io_basic_text_data_write_with_cache(self):
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST', enable_cache=True)
        text_data = 'TEST'
        gdp = GenericDataContainer(data_type=str)
        gdp.store(data=text_data)
        tfio.write(data=gdp)
        os.remove('WRITE_TEST')
        result = tfio.read()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, GenericDataContainer)
        self.assertEqual('TEST', result.data)

    def test_text_file_io_basic_text_data_write_without_cache_with_write_processor(self):
        iop = TextMultiplierGenericIOProcessor()
        gdc_result = GenericDataContainer(result_set_name='Result', data_type=str)
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST')
        text_data = '*'
        gdp = GenericDataContainer(data_type=str)
        gdp.store(data=text_data)
        tfio.write(data=gdp, write_processor=iop, multiplier=8, result_generic_data_container=gdc_result)
        result = ''
        lines = list()
        with open('WRITE_TEST', 'r') as f:
            lines = f.readlines()
        result = ''.join(lines)
        self.assertEqual(text_data, result)
        self.assertIsNotNone(gdc_result)
        self.assertIsInstance(gdc_result, GenericDataContainer)
        self.assertIsNotNone(gdc_result.data)
        self.assertEqual('********', gdc_result.data)

    def test_text_file_io_basic_text_data_write_without_cache_with_invalid_write_processor(self):
        iop = 'This is not a real processor'
        gdc_result = GenericDataContainer(result_set_name='Result', data_type=str)
        tfio = TextFileIO(file_folder_path='.', file_name='WRITE_TEST')
        text_data = '*'
        gdp = GenericDataContainer(data_type=str)
        gdp.store(data=text_data)
        tfio.write(data=gdp, write_processor=iop, multiplier=8, result_generic_data_container=gdc_result)
        result = ''
        lines = list()
        with open('WRITE_TEST', 'r') as f:
            lines = f.readlines()
        result = ''.join(lines)
        self.assertEqual(text_data, result)
        self.assertIsNotNone(gdc_result)
        self.assertIsInstance(gdc_result, GenericDataContainer)
        self.assertEqual('', gdc_result.data)


class TestValidateFileExistIOProcessor(unittest.TestCase):

    def setUp(self):
        self.gdc = GenericDataContainer(result_set_name='Test', data_type=str)
        self.gdc.store(data='somefile.txt')
        with open(self.gdc.data, 'w') as f:
            f.write('TEST')

    def tearDown(self):
        os.remove(self.gdc.data)

    def test_init_validate_file_exists_io_processor(self):
        fp = ValidateFileExistIOProcessor()
        self.assertIsNotNone(fp)
        self.assertIsInstance(fp, ValidateFileExistIOProcessor)
        self.assertIsNotNone(fp.logger)

    def test_validate_file_exists_io_processor_test_file(self):
        fp = ValidateFileExistIOProcessor()
        exception_raised = False
        try:
            fp.process(data=self.gdc)
        except:                     # pragma: no cover
            exception_raised = True # pragma: no cover
        self.assertFalse(exception_raised)

    def test_validate_file_exists_io_processor_test_non_existing_file_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=str)
        gdc.store(data='null_file.txt')
        fp = ValidateFileExistIOProcessor()
        with self.assertRaises(Exception):
            fp.process(data=gdc)

    def test_validate_file_exists_io_processor_test_invalid_generic_data_container_expect_exception(self):
        fp = ValidateFileExistIOProcessor()
        with self.assertRaises(Exception):
            fp.process(data='somefile.txt')

    def test_validate_file_exists_io_processor_test_invalid_generic_data_container_value_type_expect_exception(self):
        gdc = GenericDataContainer(result_set_name='Test', data_type=list)
        gdc.store(data=['somefile.txt'])
        fp = ValidateFileExistIOProcessor()
        with self.assertRaises(Exception):
            fp.process(data=gdc)


if __name__ == '__main__':
    unittest.main()

# EOF
