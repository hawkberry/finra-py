import io
import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import httpx

from finra import debug
from finra import log_redactor

from .common import no_duplicates


##############################################################################
# LOGGING

class TestLogging(unittest.TestCase):
    
    @no_duplicates
    def test_debug_logging(self):
        logger = debug.get_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'finra.debug')


##############################################################################
# LOG REDACTOR

class TestLogRedactor(unittest.TestCase):
    def setUp(self):
        self.redactor = log_redactor._LogRedactor()
        
    @no_duplicates
    def test_not_registered_no_redactions(self):
        self.assertEqual(
            'test message',
            self.redactor.redact('test message')
            )
        
    @no_duplicates
    def test_single_registration_multiple_redactions(self):
        self.redactor.register('secret', 'SECRET')
        self.assertTrue('SECRET' in self.redactor.label_counts)
        self.assertEqual(
            '<REDACTED SECRET> notsecret [<REDACTED SECRET>] '
            '{<REDACTED SECRET>} <REDACTED SECRET> "<REDACTED SECRET>" '
            ':<REDACTED SECRET> ,<REDACTED SECRET>, <REDACTED SECRET>',
            self.redactor.redact(
                'secret notsecret [secret] '
                '{secret} secret "secret" '
                ':secret ,secret, secret'
                )
            )
        
    @no_duplicates
    def test_multiple_registrations_same_string(self):
        self.redactor.register('secret', 'SECRET')
        self.redactor.register('secret', 'SECRET')
        self.assertTrue('SECRET' in self.redactor.label_counts)
        self.assertEqual(
            '<REDACTED SECRET> notsecret [<REDACTED SECRET>] '
            '{<REDACTED SECRET>} <REDACTED SECRET> "<REDACTED SECRET>" '
            ':<REDACTED SECRET> ,<REDACTED SECRET>, <REDACTED SECRET>',
            self.redactor.redact(
                'secret notsecret [secret] '
                '{secret} secret "secret" '
                ':secret ,secret, secret'
                )
            )
        
    @no_duplicates
    def test_multiple_registrations_same_string_different_label(self):
        self.redactor.register('secret-A', 'SECRET')
        self.redactor.register('secret-B', 'SECRET')
        self.assertTrue('SECRET' in self.redactor.label_counts)
        self.assertEqual(
            '<REDACTED SECRET-1> message <REDACTED SECRET-2>',
            self.redactor.redact('secret-A message secret-B')
            )
        
    @no_duplicates
    def test_non_string_redaction(self):
        self.redactor.register(12345, 'NUMBER')
        self.assertTrue('NUMBER' in self.redactor.label_counts)
        self.assertEqual(
            '<REDACTED NUMBER> 1234567',
            self.redactor.redact('12345 1234567')
            )
        
    @no_duplicates
    def test_none_type_label_not_stored(self):
        self.redactor.register(None, 'LABEL')
        self.assertFalse('LABEL' in self.redactor.label_counts)
        
    @no_duplicates
    def test_empty_string_label_not_stored(self):
        self.redactor.register('', 'LABEL')
        self.assertFalse('LABEL' in self.redactor.label_counts)
        
    @no_duplicates
    def test_spaces_only_string_label_not_stored(self):
        self.redactor.register('  ', 'LABEL')
        self.assertFalse('LABEL' in self.redactor.label_counts)


##############################################################################
# REGISTER REDACTIONS

class _TestRegisterRedactions:
    def setUp(self):
        self.logger = logging.getLogger('test')
        
        # New redactor for each test
        log_redactor._LOG_REDACTOR = log_redactor._LogRedactor()
        
    @no_duplicates
    @patch('finra.log_redactor._LOG_REDACTOR', new_callable=Mock)
    def test_none(self, redactor):
        redactor.register = Mock()
        log_redactor.register_redactions(None)
        redactor.register.assert_not_called()
        
    @no_duplicates
    @patch('finra.log_redactor._LOG_REDACTOR', new_callable=Mock)
    def test_empty_string(self, redactor):
        redactor.register = Mock()
        log_redactor.register_redactions('')
        redactor.register.assert_not_called()
        
    @no_duplicates
    @patch('finra.log_redactor._LOG_REDACTOR', new_callable=Mock)
    def test_empty_dict(self, redactor):
        redactor.register = Mock()
        log_redactor.register_redactions({})
        redactor.register.assert_not_called()
        
    @no_duplicates
    @patch('finra.log_redactor._LOG_REDACTOR', new_callable=Mock)
    def test_empty_list(self, redactor):
        redactor.register = Mock()
        log_redactor.register_redactions([])
        redactor.register.assert_not_called()
        
    @no_duplicates
    def test_dict(self):
        log_redactor.register_redactions(
            {'BadValue': '100001'}, bad_patterns=['bAd'] # case-insensitive
            )
        log_redactor.register_redactions(
            {'OtherBadValue': '200002'}, bad_patterns=['bad']
            )
        
        self.logger.info('Bad Value: 100001')
        self.logger.info('Other Bad Value: 200002')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] Bad Value: <REDACTED BadValue>\n"
            r"\[.*\] Other Bad Value: <REDACTED OtherBadValue>\n"
            )
        
    @no_duplicates
    def test_list_of_dict(self):
        log_redactor.register_redactions([
            {'GoodValue': '900009'},
            {'BadValue': '100001'},
            {'OtherBadValue': '200002'},
            ],
            bad_patterns=['bad']
            )
        
        self.logger.info('Good Value: 900009')
        self.logger.info('Bad Value: 100001')
        self.logger.info('Other Bad Value: 200002')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] Good Value: 900009\n"
            r"\[.*\] Bad Value: <REDACTED 1-BadValue>\n"
            r"\[.*\] Other Bad Value: <REDACTED 2-OtherBadValue>\n"
            )
        
    @no_duplicates
    def test_compare(self):
        log_redactor.register_redactions([
            {'fieldName': 'GoodValue', 'fieldValue': '900009'},
            {'fieldName': 'BadValue', 'fieldValue': '100001'},
            {'fieldName': 'OtherBadValue', 'fieldValue': '200002'},
            ],
            bad_patterns=['bad']
            )
        
        self.logger.info('Good Value: 900009')
        self.logger.info('Bad Value: 100001')
        self.logger.info('Other Bad Value: 200002')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] Good Value: 900009\n"
            r"\[.*\] Bad Value: <REDACTED 1-BadValue>\n"
            r"\[.*\] Other Bad Value: <REDACTED 2-OtherBadValue>\n"
            )
        
    @no_duplicates
    def test_whitelist(self):
        log_redactor.register_redactions([
            {'GoodValue': '900009'},
            {'BadValue': '100001'},
            {'OtherBadValue': '200002'},
            ],
            bad_patterns=['bad'],
            whitelist=['OtherBadValue']
            )
        
        self.logger.info('Good Value: 900009')
        self.logger.info('Bad Value: 100001')
        self.logger.info('Other Bad Value: 200002')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] Good Value: 900009\n" +
            r"\[.*\] Bad Value: <REDACTED 1-BadValue>\n" +
            r"\[.*\] Other Bad Value: 200002\n"
            )
        
    @no_duplicates
    def test_whitelist_case_sensitive(self):
        log_redactor.register_redactions([
            {'GoodValue': '900009'},
            {'BadValue': '100001'},
            {'OtherBadValue': '200002'},
            ],
            bad_patterns=['bad'],
            whitelist=['OtHeRbAdVaLuE'] # case-sensitive, fails to whitelist
            )
        
        self.logger.info('Good Value: 900009')
        self.logger.info('Bad Value: 100001')
        self.logger.info('Other Bad Value: 200002')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] Good Value: 900009\n" +
            r"\[.*\] Bad Value: <REDACTED 1-BadValue>\n" +
            r"\[.*\] Other Bad Value: <REDACTED 2-OtherBadValue>\n"
            )
        
    @no_duplicates
    @patch('finra.log_redactor.register_redactions', new_callable=Mock)
    def test_register_from_request_success(self, register_redactions):
        r = httpx.Response(200, content=b'{"success": 1}')
        log_redactor.register_redactions_from_response(r)
        register_redactions.assert_called_with({'success': 1})
        
    @no_duplicates
    @patch('finra.log_redactor.register_redactions', new_callable=Mock)
    def test_register_from_request_not_ok(self, register_redactions):
        r = httpx.Response(403, content=b'{"success": 1}')
        log_redactor.register_redactions_from_response(r)
        register_redactions.assert_not_called()
        
    @no_duplicates
    @patch('finra.log_redactor.register_redactions', new_callable=Mock)
    def test_register_unparseable_json(self, register_redactions):
        class _MockResponse(httpx.Response):
            def json(self):
                raise json.decoder.JSONDecodeError('decode error', '', 0)
        
        r = _MockResponse(200, content=b'{"success": 1}')
        log_redactor.register_redactions_from_response(r)
        register_redactions.assert_not_called()


class TestRegisterRedactionsStream(_TestRegisterRedactions, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.file = io.StringIO()
        debug._enable_bug_report_logging(
            stream=self.file, loggers=[self.logger]
            )


class TestRegisterRedactionsFile(_TestRegisterRedactions, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.TemporaryDirectory()
        path = Path(self.tmpdir.name, 'test_log_file.log')
        
        class ReadFile:
            @staticmethod
            def getvalue():
                return path.read_text()
        
        self.file = ReadFile()
        self.fh, self.sh = debug._enable_bug_report_logging(
            filename=path, stream=None, loggers=[self.logger]
            )
        
    def tearDown(self):
        self.logger.removeHandler(self.fh)
        self.fh.flush()
        self.fh.close()
        self.tmpdir.cleanup()
        super().tearDown()


class TestEmit(unittest.TestCase):
    
    @no_duplicates
    def test_emit_handler_exception(self):
        handler = Mock()
        handler.format.side_effect = Exception()
        
        record = logging.LogRecord(10, 'path', 123, 'msg', None, None, None)
        log_redactor._emit(handler, record)
        
        handler.handleError.assert_called_once_with(record)


##############################################################################
# DEBUG

class TestEnableBugReportLogging(unittest.TestCase):
    
    @patch('logging.Logger.addHandler')
    def test_enable_bug_report_logging_success(self, _):
        debug.enable_bug_report_logging()
        
    def test_enable_no_filename_and_no_stream_value_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "Must set filename or stream to enable bug report logging"
            ):
            debug.enable_bug_report_logging(stream=None)

