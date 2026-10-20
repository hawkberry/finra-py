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
        
    @no_duplicates
    def test_redact_string_not_in_repl(self):
        msg = self.redactor.redact('not registered')
        self.assertEqual(msg, 'not registered')


##############################################################################
# REGISTER REDACTIONS

class _TestRegisterRedactions:
    def setUp(self):
        self.logger = logging.getLogger('test')
        
        # New redactor for each test, requires patch for module singleton
        self.redactor = log_redactor._LogRedactor()
        patchers = [
            patch("finra.debug._LOG_REDACTOR", new=self.redactor),
            patch("finra.log_redactor._LOG_REDACTOR", new=self.redactor),
            ]
        for p in patchers:
            obj = p.start()
            self.assertIs(obj, self.redactor)
            self.addCleanup(p.stop)
        
    @no_duplicates
    @patch('finra.log_redactor._register_redactions', new_callable=Mock)
    @patch('finra.log_redactor._LOG_REDACTOR', new_callable=Mock)
    def test_disabled(self, redactor, register_redactions):
        redactor.enabled = False
        log_redactor.register_redactions("redaction")
        register_redactions.assert_not_called()
        
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
        log_redactor.register_redactions("")
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
            {'BadValue': '100001'},
            bad_patterns=['bAd'] # case-insensitive
            )
        log_redactor.register_redactions(
            {'OtherBadValue': '200002'},
            bad_patterns=['bad']
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
        log_redactor.register_redactions(
            [
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
        log_redactor.register_redactions(
            [
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
        log_redactor.register_redactions(
            [
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
        log_redactor.register_redactions(
            [
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
    def test_warn_on(self):
        log_redactor._register_redactions(
            [
                {'warnOnField': 'SSN #123-45-6789 and DOB 7/20/68.'},
                {'whiteListed': 'Another social security number: 234-56-7890'},
                ],
            key_path=None,
            bad_patterns=[],
            whitelist=['whiteListed'],
            warn_on=['warnonfield', 'whitelisted'] # must be lowercase
            ) # test inner function: _register_redactions
        
        self.logger.info('123-45-6789 DOB 7/20/68')
        self.logger.info('Another SSN: 123-45-6789.')
        self.logger.info('White Listed SSN: 234-56-7890.')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] <REDACTED 0-warnOnField-1> <REDACTED 0-warnOnField-2>\n" +
            r"\[.*\] Another SSN: <REDACTED 0-warnOnField-1>.\n" +
            r"\[.*\] White Listed SSN: 234-56-7890.\n"
            )
        
    @no_duplicates
    def test_warn_on_health_info_avoid_redacted(self):
        log_redactor._register_redactions(
            [
                {'warnOnField': 'An exact statement about some Disease.'},
                {'whiteListed': 'A whitelisted field about a Disease.'},
                ],
            key_path=None,
            bad_patterns=[],
            whitelist=['whiteListed'],
            warn_on=['warnonfield', 'whitelisted'] # must be lowercase
            ) # test inner function: _register_redactions
        
        self.logger.info('An exact statement about some Disease.')
        self.logger.info('A whitelisted field about a Disease.')
        self.logger.info('A completely different Disease statement.')
        
        self.assertRegex(
            self.file.getvalue(),
            r"\[.*\] <REDACTED 0-warnOnField>\n" +
            r"\[.*\] A whitelisted field about a Disease.\n" +
            r"\[.*\] A completely different Disease statement.\n"
            )
        
    @no_duplicates
    @patch('finra.log_redactor._register_redactions', new_callable=Mock)
    def test_register_response_success(self, register_redactions):
        r = httpx.Response(200, content=b'{"success": 1}')
        log_redactor.register_redactions_from_response(r)
        register_redactions.assert_called_with(
            {'success': 1}, None, log_redactor._BAD_PATTERNS,
            log_redactor._WHITELIST, log_redactor._WARN_ON
            )
        
    @no_duplicates
    @patch('finra.log_redactor._register_redactions', new_callable=Mock)
    def test_register_response_redactor_disabled(self, register_redactions):
        r = Mock()
        r.status_code = 200
        r.json = Mock()
        
        self.redactor.enabled = False
        log_redactor.register_redactions_from_response(r)
        
        register_redactions.assert_not_called()
        r.json.assert_not_called()
        
    @no_duplicates
    @patch('finra.log_redactor._register_redactions', new_callable=Mock)
    def test_register_response_not_ok(self, register_redactions):
        r = httpx.Response(403, content=b'{"success": 1}')
        log_redactor.register_redactions_from_response(r)
        
        register_redactions.assert_not_called()
        
    @no_duplicates
    @patch('finra.log_redactor.logging.getLogger', new_callable=Mock)
    @patch('finra.log_redactor._register_redactions', new_callable=Mock)
    def test_register_unparseable_json(self, register_redactions, getLogger):
        logger = Mock()
        getLogger.return_value = logger
        
        class _MockResponse(httpx.Response):
            def json(self):
                raise json.decoder.JSONDecodeError('decode error', '', 0)
        
        r = _MockResponse(200, content=b'unparsable')
        log_redactor.register_redactions_from_response(r)
        
        register_redactions.assert_not_called()
        getLogger.assert_called_once_with("finra.debug")
        logger.warning.assert_called_once_with(
            "Response.json() could not decode the content as JSON, so the "
            "response could not be registered for redaction. Review the "
            "log before sharing."
            )


class TestRegisterRedactionsStream(_TestRegisterRedactions, unittest.TestCase):
    def setUp(self):
        _TestRegisterRedactions.setUp(self)
        unittest.TestCase.setUp(self)
        
        self.file = io.StringIO()
        
        self.assertFalse(log_redactor._LOG_REDACTOR.enabled)
        debug._enable_bug_report_logging(
            stream=self.file, loggers=[self.logger]
            )
        self.assertTrue(log_redactor._LOG_REDACTOR.enabled)


class TestRegisterRedactionsFile(_TestRegisterRedactions, unittest.TestCase):
    def setUp(self):
        _TestRegisterRedactions.setUp(self)
        unittest.TestCase.setUp(self)
        
        self.tmpdir = tempfile.TemporaryDirectory()
        path = Path(self.tmpdir.name, 'test_log_file.log')
        
        class ReadFile:
            @staticmethod
            def getvalue():
                return path.read_text()
        
        self.file = ReadFile()
        
        self.assertFalse(log_redactor._LOG_REDACTOR.enabled)
        debug._enable_bug_report_logging(
            filename=path, stream=None, loggers=[self.logger]
            )
        self.assertTrue(log_redactor._LOG_REDACTOR.enabled)
        
    def tearDown(self):
        for h in self.logger.handlers:
            self.logger.removeHandler(h)
            h.flush()
            h.close()
        self.tmpdir.cleanup()
        super().tearDown()


class TestEmit(unittest.TestCase):
    
    @no_duplicates
    def test_emit_handler_exception(self):
        handler = Mock()
        handler.format.side_effect = ValueError()
        
        record = logging.LogRecord(10, 'path', 123, 'msg', None, None, None)
        log_redactor._emit(handler, record)
        
        handler.handleError.assert_called_once_with(record)


##############################################################################
# DEBUG

class TestEnableBugReportLogging(unittest.TestCase):
    
    @no_duplicates
    @patch('logging.Logger.addHandler')
    def test_enable_bug_report_logging_success(self, _):
        debug.enable_bug_report_logging()
        
    @no_duplicates
    def test_enable_no_filename_and_no_stream_value_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "Must set filename or stream to enable bug report logging"
            ):
            debug.enable_bug_report_logging(stream=None)


if __name__ == "__main__": # pragma: no cover
    unittest.main()
