# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. 
# This software is licensed under the LGPL license version 3 of 2007. A copy of
# the license should be included with this software, usually in a file called
# LICENSE.txt. If this is not the case, you can view the license online at
# https://www.gnu.org/licenses/lgpl-3.0.txt

"""
Usage with coverage:

::

    $ coverage run -m tests.test_logging
    $ coverage report -m
"""

import unittest
import logging
from odc_pycommons import OculusDLogger, DEBUG, formatter, get_utc_timestamp
from pathlib import Path
import os
import traceback
import time


class TestLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.lines = list()

    def emit(self, record):
        self.lines.append(self.format(record))

    def flush(self):
        self.lines = list()


class TestOculusDLogger(unittest.TestCase):

    def setUp(self):    
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.ch = TestLogHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)

    def tearDown(self):
        self.ch.flush()

    def test_init(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.info('TEST')
        self.assertEqual(len(self.ch.lines), 1)

    def test_init_force_debug(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.enable_debug()
        test_logger.debug('You should see this...')
        test_logger.info('TEST')
        self.assertEqual(len(self.ch.lines), 2)

    def test_verify_content_no_debug(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.disable_debug()
        test_logger.debug('You should not see this...')
        test_logger.info('TEST')
        self.assertEqual(len(self.ch.lines), 1)
        line1_elements = self.ch.lines[0].split(' ')
        self.assertEqual(len(line1_elements), 6)
        self.assertFalse('test_verify_content_no_debug' in self.ch.lines[0])

    def test_verify_content_including_debug(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.enable_debug()
        test_logger.info('TEST')
        self.assertEqual(len(self.ch.lines), 1)
        line1_elements = self.ch.lines[0].split(' ')
        self.assertEqual(len(line1_elements), 7)
        self.assertTrue('test_verify_content_including_debug' in self.ch.lines[0])

    def test_empty_message_logging(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.info(message=None)
        last_line = ''
        last_line = self.ch.lines[-1]
        self.assertTrue('NO_INPUT_MESSAGE' in last_line)

    def test_warning_message_logging(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.warning(message=None)
        last_line = ''
        last_line = self.ch.lines[-1]
        self.assertTrue('NO_INPUT_MESSAGE' in last_line)
        self.assertTrue('WARN' in last_line)

    def test_error_message_logging(self):
        test_logger = OculusDLogger(logger_impl=self.logger)
        test_logger.error(message=None)
        last_line = ''
        last_line = self.ch.lines[-1]
        self.assertTrue('NO_INPUT_MESSAGE' in last_line)
        self.assertTrue('ERR' in last_line)


class TestGetUtcTimestamp(unittest.TestCase):

    def test_get_utc_timestamp_without_decimal(self):
        ts = get_utc_timestamp()
        self.assertIsNotNone(ts)
        self.assertIsInstance(ts, int)
        self.assertTrue(ts>0)

    def test_get_utc_timestamp_with_decimal(self):
        ts = get_utc_timestamp(with_decimal=True)
        self.assertIsNotNone(ts)
        self.assertIsInstance(ts, float)
        self.assertTrue(ts>0.5)

if __name__ == '__main__':
    unittest.main()


# EOF
