import asyncio
import inspect
import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import ANY, Mock, patch

from finra import auth
from finra.token_manager import TokenManager

from .common import MockAsyncOAuth2Client, MockOAuth2Client, no_duplicates


API_KEY = 'APIKEY'
API_SECRET = '0x6D8723EF'
TOKEN_PATH = 'test_token.json'
TOKEN_CREATED_TIMESTAMP = 1780445000
TOKEN_EXPIRES_AT = TOKEN_CREATED_TIMESTAMP + 10_000
NOW = 1780445421


##############################################################################
# LOGGING

class TestLogging(unittest.TestCase):
    
    @no_duplicates
    def test_auth_logging(self):
        logger = auth.get_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'finra.auth')
    

##############################################################################
# DOCS

class TestDocs(unittest.TestCase):
    
    @no_duplicates
    def test_add_auth_params_docs_bad_param(self):
        with self.assertRaisesRegex(
            ValueError, "Unknown parameters: 'unknown_parameter'"
            ):
            auth._add_auth_params_docs(auth.get_client, "unknown_parameter")


##############################################################################
# TOKEN MANAGER

class TestTokenManager(unittest.TestCase):
    
    @no_duplicates
    @patch('time.time', Mock(return_value=NOW))
    def test_token_age(self):
        token = {'token': '1', 'created_timestamp': TOKEN_CREATED_TIMESTAMP}
        token_manager = TokenManager.from_wrapped_token(token, None)
        self.assertEqual(
            token_manager.token_age,
            NOW - TOKEN_CREATED_TIMESTAMP
            )
        
    @no_duplicates
    def test_expires_at(self):
        token = {
            'token': {'expires_at': TOKEN_EXPIRES_AT},
            'created_timestamp': TOKEN_CREATED_TIMESTAMP
            }
        token_manager = TokenManager.from_wrapped_token(token, None)
        self.assertEqual(token_manager.expires_at, TOKEN_EXPIRES_AT)
        
    @no_duplicates
    @patch('time.time', Mock(return_value=NOW))
    def test_expires_in(self):
        token = {
            'token': {'expires_at': TOKEN_EXPIRES_AT},
            'created_timestamp': TOKEN_CREATED_TIMESTAMP
            }
        token_manager = TokenManager.from_wrapped_token(token, None)
        self.assertEqual(
            token_manager.expires_in,
            TOKEN_EXPIRES_AT - NOW - 1
            )
        
    @no_duplicates
    def test_update_token(self):
        token = {'token': '1', 'created_timestamp': TOKEN_CREATED_TIMESTAMP}
        
        updated = [False]
        def token_write_func(token, *args, **kwds):
            updated[0] = True
        
        token_manager = TokenManager.from_wrapped_token(
            token, token_write_func
            )
        new_token = {'token': '2'}
        token_manager.update_token(new_token)
        self.assertTrue(updated[0])
        self.assertEqual(new_token, token_manager.token)
        
    @no_duplicates
    def test_from_wrapped_token(self):
        token = {'token': '1', 'created_timestamp': TOKEN_CREATED_TIMESTAMP}
        token_manager = TokenManager.from_wrapped_token(token, None)
        self.assertEqual(token_manager.token, token['token'])
        
    @no_duplicates
    def test_reject_tokens_without_created_timestamp(self):
        token = {'token': '1'}
        with self.assertRaisesRegex(
            ValueError,
            "WARNING: The token format has changed since this token "
            "was created. Please delete it and create a new one."
            ):
            TokenManager.from_wrapped_token(token, None)


##############################################################################
# BUILD CLIENT

class TestBuildClient(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.token_path = Path(self.tmpdir.name, TOKEN_PATH)
        self.token = {'token': '1'}
        self.wrapped_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': self.token,
            }
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.TokenManager')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_build(self, session, token_manager, client):
        session.return_value = session
        
        token_manager.token = self.token
        
        client.return_value = client
        
        c = auth.build_client(API_KEY, API_SECRET, token_manager)
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=token_manager,
            mock=False,
            test_environment=False
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._PROD_TOKEN_ENDPOINT,
            update_token=ANY, leeway=ANY
            )
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.TokenManager')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_with_params(self, session, token_manager, client):
        session.return_value = session
        
        token_manager.token = self.token
        
        client.return_value = client
        
        c = auth.build_client(
            API_KEY,
            API_SECRET,
            token_manager,
            leeway=123,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=token_manager,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._TEST_TOKEN_ENDPOINT,
            update_token=ANY, leeway=123
            )
        
    @no_duplicates
    @patch('finra.auth.TokenManager')
    def test_client_constructor(self, token_manager):
        token_manager.token = self.token
        
        client_constructor = Mock()
        client_constructor.return_value = auth.Client(
            API_KEY,
            auth.OAuth2Client(API_KEY, API_SECRET),
            token_manager=token_manager
            )
        
        auth.build_client(
            API_KEY,
            API_SECRET,
            token_manager,
            client_cls=client_constructor
            )
        
        client_constructor.assert_called_once_with(
            API_KEY, ANY, token_manager=token_manager,
            mock=False, test_environment=False
            )
        
    @no_duplicates
    @patch('finra.auth.TokenManager')
    def test_client_constructor_wrong_client_type(self, token_manager):
        token_manager.token = self.token
        
        client_constructor = Mock()
        client_constructor.return_value = auth.AsyncClient(
            API_KEY,
            auth.AsyncOAuth2Client(API_KEY, API_SECRET),
            token_manager=token_manager
            ) # wrong type
        
        with self.assertRaisesRegex(
            TypeError, "client_cls must return Client or subclass"
            ):
            auth.build_client(
                API_KEY,
                API_SECRET,
                token_manager,
                client_cls=client_constructor
                )


class TestBuildAsyncClient(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.token_path = Path(self.tmpdir.name, TOKEN_PATH)
        self.token = {'token': '1'}
        self.wrapped_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': self.token,
            }
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    @no_duplicates
    @patch('finra.auth.AsyncClient')
    @patch('finra.auth.TokenManager')
    @patch('finra.auth.AsyncOAuth2Client', new_callable=MockAsyncOAuth2Client)
    def test_build(self, session, token_manager, client):
        session.return_value = session
        
        token_manager.token = self.token
        
        client.return_value = client
        
        c = auth.build_async_client(API_KEY, API_SECRET, token_manager)
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=token_manager,
            mock=False,
            test_environment=False
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._PROD_TOKEN_ENDPOINT,
            update_token=ANY, leeway=ANY
            )
        
    @no_duplicates
    @patch('finra.auth.AsyncClient')
    @patch('finra.auth.TokenManager')
    @patch('finra.auth.AsyncOAuth2Client', new_callable=MockAsyncOAuth2Client)
    def test_with_params(self, session, token_manager, client):
        session.return_value = session
        
        token_manager.token = self.token
        
        client.return_value = client
        
        c = auth.build_async_client(
            API_KEY,
            API_SECRET,
            token_manager,
            leeway=123,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=token_manager,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._TEST_TOKEN_ENDPOINT,
            update_token=ANY, leeway=123
            )
        
    @no_duplicates
    @patch('finra.auth.AsyncClient')
    @patch('finra.auth.TokenManager')
    @patch('finra.auth.AsyncOAuth2Client', new_callable=MockAsyncOAuth2Client)
    def test_async_update_token(self, session, token_manager, client):
        session.return_value = session
        
        token_manager.token = self.token
        
        client.return_value = client
        
        auth.build_async_client(
            API_KEY,
            API_SECRET,
            token_manager
            )
        
        session_call = session.mock_calls[0]
        update_token = session_call[2]['update_token'] # async update
        
        self.assertTrue(inspect.iscoroutinefunction(update_token))
        
        loop = asyncio.new_event_loop()
        loop.run_until_complete(update_token(self.token))
        loop.close()
        
        token_manager.update_token.assert_called_once_with(self.token)
        
    @no_duplicates
    @patch('finra.auth.TokenManager')
    def test_async_client_constructor(self, token_manager):
        token_manager.token = self.token
        
        async_client_constructor = Mock()
        async_client_constructor.return_value = auth.AsyncClient(
            API_KEY,
            auth.AsyncOAuth2Client(API_KEY, API_SECRET),
            token_manager=token_manager
            )
        
        auth.build_async_client(
            API_KEY,
            API_SECRET,
            token_manager,
            async_client_cls=async_client_constructor
            )
        
        async_client_constructor.assert_called_once_with(
            API_KEY, ANY, token_manager=token_manager,
            mock=False, test_environment=False
            )
        
    @no_duplicates
    @patch('finra.auth.TokenManager')
    def test_async_client_constructor_wrong_client_type(self, token_manager):
        token_manager.token = self.token
        
        async_client_constructor = Mock()
        async_client_constructor.return_value = auth.Client(
            API_KEY,
            auth.OAuth2Client(API_KEY, API_SECRET),
            token_manager=token_manager
            ) # wrong type
        
        with self.assertRaisesRegex(
            TypeError, "async_client_cls must return AsyncClient or subclass"
            ):
            auth.build_async_client(
                API_KEY,
                API_SECRET,
                token_manager,
                async_client_cls=async_client_constructor
                )


##############################################################################
# CLIENT FROM READ & WRITE FUNCTIONS

class TestDefaultTokenWriterConstructor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.token_path = Path(self.tmpdir.name, TOKEN_PATH)
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    @no_duplicates
    @patch('finra.auth.Path')
    def test_path_parent_not_a_dir(self, path):
        path.return_value = path
        path.parent = path
        path.exists.return_value = True
        path.is_dir.return_value = False
        path.__str__.return_value = 'test_path'
        
        with self.assertRaisesRegex(
            NotADirectoryError,
            "Token path parent is not a directory: test_path"
            ):
            getattr(auth, '__token_writer')(self.token_path)
        
    @no_duplicates
    @patch('finra.auth.Path')
    def test_path_parent_make_dir(self, path):
        path.return_value = path
        path.parent = path
        path.exists.return_value = False
        path.is_dir.return_value = True
        
        getattr(auth, '__token_writer')(self.token_path)
        
        path.mkdir.assert_called_once()


class TestClientFromStorageFunctions(unittest.TestCase):
    def setUp(self):
        self.token = {'token': '1'}
        self.wrapped_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': self.token,
            }
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('finra.auth.register_redactions')
    def test_token_write_func(self, register_redactions, session, client):
        session.return_value = session
        
        client.return_value = client
        
        token_read_func = Mock()
        token_read_func.return_value = self.wrapped_token
        
        written = []
        def token_write_func(token):
            written.append(token)
        
        c = auth.client_from_storage_functions(
            API_KEY,
            API_SECRET,
            token_read_func,
            token_write_func
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock=False,
            test_environment=False
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._PROD_TOKEN_ENDPOINT,
            update_token=ANY, leeway=ANY
            )
        
        register_redactions.assert_called_once_with(self.token)
        
        token_read_func.assert_called_once()
        
        session_call = session.mock_calls[0]
        update_token = session_call[2]['update_token'] # token manager method
        
        update_token(self.token)
        
        self.assertEqual([self.wrapped_token], written)
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('finra.auth.register_redactions')
    def test_with_params(self, register_redactions, session, client):
        session.return_value = session
        
        client.return_value = client
        
        token_read_func = Mock()
        token_read_func.return_value = self.wrapped_token
        
        token_write_func = Mock()
        
        c = auth.client_from_storage_functions(
            API_KEY,
            API_SECRET,
            token_read_func,
            token_write_func,
            leeway=123,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._TEST_TOKEN_ENDPOINT,
            update_token=ANY, leeway=123
            )
        
        register_redactions.assert_called_once_with(self.token)
        
    @no_duplicates
    @patch('finra.auth.AsyncClient')
    @patch('finra.auth.AsyncOAuth2Client', new_callable=MockAsyncOAuth2Client)
    @patch('finra.auth.register_redactions')
    def test_asyncio_with_params(self, register_redactions, session, client):
        session.return_value = session
        
        client.return_value = client
        
        token_read_func = Mock()
        token_read_func.return_value = self.wrapped_token
        
        token_write_func = Mock()
        
        c = auth.client_from_storage_functions(
            API_KEY,
            API_SECRET,
            token_read_func,
            token_write_func,
            is_asyncio=True,
            leeway=123,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._TEST_TOKEN_ENDPOINT,
            update_token=ANY, leeway=123
            )
        
        register_redactions.assert_called_once_with(self.token)


##############################################################################
# CLIENT FROM TOKEN FILE

class TestClientFromTokenFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.token_path = Path(self.tmpdir.name, TOKEN_PATH)
        self.token = {'token': '1'}
        self.wrapped_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': self.token,
            }
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    def write_token(self):
        with open(self.token_path, 'w') as f:
            json.dump(self.wrapped_token, f)
        
    def read_token(self):
        with open(self.token_path, 'r') as f:
            return json.load(f)
        
    @no_duplicates
    def test_no_token_file(self):
        with self.assertRaises(FileNotFoundError):
            auth.client_from_token_file(API_KEY, API_SECRET, self.token_path)
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_token_read_func(self, session, client):
        session.return_value = session
        
        client.return_value = client
        
        self.write_token()
        
        c = auth.client_from_token_file(API_KEY, API_SECRET, self.token_path)
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock=False,
            test_environment=False
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._PROD_TOKEN_ENDPOINT,
            update_token=ANY, leeway=ANY
            )
                
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_update_token(self, session, client):
        self.write_token()
        
        auth.client_from_token_file(API_KEY, API_SECRET, self.token_path)
        
        client.assert_called_once()
        session.assert_called_once()
        
        session_call = session.mock_calls[0]
        update_token = session_call[2]['update_token'] # token manager method
        
        updated_token = {'updated': 'token'}
        update_token(updated_token)
        
        wrapped_updated_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': updated_token,
            }
        self.assertEqual(self.read_token(), wrapped_updated_token)
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_with_params(self, session, client):
        session.return_value = session
        
        client.return_value = client
        
        self.write_token()
        
        c = auth.client_from_token_file(
            API_KEY,
            API_SECRET,
            self.token_path,
            leeway=123,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        session.assert_called_once_with(
            API_KEY, API_SECRET, token=self.token,
            token_endpoint=auth._TEST_TOKEN_ENDPOINT,
            update_token=ANY, leeway=123
            )


##############################################################################
# CLIENT FROM NEW TOKEN

class TestClientFromNewToken(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.token_path = Path(self.tmpdir.name, TOKEN_PATH)
        self.token = {'token': '1'}
        self.wrapped_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': self.token,
            }
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    def read_token(self):
        with open(self.token_path, 'r') as f:
            return json.load(f)
    
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('finra.auth.register_redactions')
    @patch('time.time', Mock(return_value=TOKEN_CREATED_TIMESTAMP))
    def test_token_write_func(self, register_redactions, session, client):
        session.return_value = session
        session.fetch_token.return_value = self.token
        
        client.return_value = client
        
        written = []
        def token_write_func(token):
            written.append(token)
        
        c = auth.client_from_new_token(
            API_KEY, API_SECRET, None, # token path ignored if token_write_func
            token_write_func=token_write_func
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock=False,
            test_environment=False
            )
        
        session.fetch_token.assert_called_once()
        
        register_redactions.assert_called_once_with(self.token)
        
        self.assertEqual([self.wrapped_token], written)
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('time.time', Mock(return_value=TOKEN_CREATED_TIMESTAMP))
    def test_token_write_func_token_path_none(self, client):
        with self.assertRaisesRegex(
            ValueError, "Must set token path to use default token_write_func"
            ):
            auth.client_from_new_token(API_KEY, API_SECRET, None)
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('finra.auth.register_redactions')
    @patch('time.time', Mock(return_value=TOKEN_CREATED_TIMESTAMP))
    def test_new_token(self, register_redactions, session, client):
        session.return_value = session
        session.fetch_token.return_value = self.token
        
        client.return_value = client
        
        c = auth.client_from_new_token(API_KEY, API_SECRET, self.token_path)
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock=False,
            test_environment=False
            )
        
        session.fetch_token.assert_called_once()
        
        self.assertEqual(len(session.mock_calls), 3) # w/ fetch_token
        
        session_call = session.mock_calls[2] # called to create client session
        self.assertEqual(session_call[1], (API_KEY, API_SECRET))
        self.assertEqual(session_call[2]['token'], self.token)
        self.assertEqual(
            session_call[2]['token_endpoint'], auth._PROD_TOKEN_ENDPOINT
            )
        
        register_redactions.assert_called_once_with(self.token)
        
        self.assertEqual(self.read_token(), self.wrapped_token)
        
    @no_duplicates
    @patch('finra.auth.AsyncClient')
    @patch('finra.auth.AsyncOAuth2Client', new_callable=MockAsyncOAuth2Client)
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('finra.auth.register_redactions')
    @patch('time.time', Mock(return_value=TOKEN_CREATED_TIMESTAMP))
    def test_asyncio_new_token(self, register_redactions, sync_session,
                               async_session, client):
        sync_session.return_value = sync_session
        sync_session.fetch_token.return_value = self.token
        
        async_session.return_value = async_session
        
        client.return_value = client
        
        c = auth.client_from_new_token(
            API_KEY,
            API_SECRET,
            self.token_path,
            is_asyncio=True
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            async_session,
            token_manager=ANY,
            mock=False,
            test_environment=False
            )
        
        # Synchronous OAuth2Client to fetch new token before creating client
        sync_session.fetch_token.assert_called_once()
        
        self.assertEqual(len(sync_session.mock_calls), 2) # w/ fetch_token
        
        sync_session_call = sync_session.mock_calls[0]
        self.assertEqual(sync_session_call[1], (API_KEY, API_SECRET))
        self.assertEqual(
            sync_session_call[2]['token_endpoint'], auth._PROD_TOKEN_ENDPOINT
            )
        
        # Asynchronous AsyncOAuth2Client as async client session
        self.assertEqual(len(async_session.mock_calls), 1)
        
        async_session_call = async_session.mock_calls[0]
        self.assertEqual(async_session_call[1], (API_KEY, API_SECRET))
        self.assertEqual(async_session_call[2]['token'], self.token)
        self.assertEqual(
            async_session_call[2]['token_endpoint'], auth._PROD_TOKEN_ENDPOINT
            )
        
        register_redactions.assert_called_once_with(self.token)
        
        self.assertEqual(self.read_token(), self.wrapped_token)
        
    @no_duplicates
    @patch('finra.auth.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('finra.auth.register_redactions')
    @patch('time.time', Mock(return_value=TOKEN_CREATED_TIMESTAMP))
    def test_with_params(self, register_redactions, session, client):
        session.return_value = session
        session.fetch_token.return_value = self.token
        
        client.return_value = client
        
        c = auth.client_from_new_token(
            API_KEY,
            API_SECRET,
            self.token_path,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        self.assertEqual(c, client)
        
        client.assert_called_once_with(
            API_KEY,
            session,
            token_manager=ANY,
            mock='mock',
            test_environment='test_environment',
            timeout='timeout',
            accept_json='accept_json',
            require_enums='require_enums'
            )
        
        session.fetch_token.assert_called_once()
        
        self.assertEqual(len(session.mock_calls), 3) # w/ fetch_token
        
        session_call = session.mock_calls[2] # called to create client session
        self.assertEqual(session_call[1], (API_KEY, API_SECRET))
        self.assertEqual(session_call[2]['token'], self.token)
        self.assertEqual(
            session_call[2]['token_endpoint'], auth._TEST_TOKEN_ENDPOINT
            )
        
        register_redactions.assert_called_once_with(self.token)


##############################################################################
# GET CLIENT

class TestGetClient(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.token_path = Path(self.tmpdir.name, TOKEN_PATH)
        self.token = {'token': '1'}
        self.wrapped_token = {
            'created_timestamp': TOKEN_CREATED_TIMESTAMP,
            'token': self.token,
            }
        
    def tearDown(self):
        self.tmpdir.cleanup()
        
    def write_token(self):
        with open(self.token_path, 'w') as f:
            json.dump(self.wrapped_token, f)
    
    @no_duplicates
    @patch('finra.auth.client_from_new_token')
    def test_new_token(self, client_from_new_token):
        mock_client = Mock()
        client_from_new_token.return_value = mock_client
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path
            )
        
        self.assertIs(c, mock_client)
        
    @no_duplicates
    @patch('finra.auth.client_from_new_token')
    def test_new_token_with_params(self, client_from_new_token):
        mock_client = Mock()
        client_from_new_token.return_value = mock_client
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path,
            token_write_func='token_write_func',
            is_asyncio='is_asyncio',
            mock='mock',
            test_environment='test_environment'
            )
        
        self.assertIs(c, mock_client)
        
        client_from_new_token.assert_called_once_with(
            API_KEY,
            API_SECRET,
            self.token_path,
            token_write_func='token_write_func',
            is_asyncio='is_asyncio',
            mock='mock',
            test_environment='test_environment'
            )
        
    @no_duplicates
    @patch('finra.auth.client_from_token_file')
    def test_token_file(self, client_from_token_file):
        self.write_token()
        
        mock_client = Mock()
        client_from_token_file.return_value = mock_client
        mock_client.token_expires_in = 10_000
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path
            )
        
        self.assertIs(c, mock_client)
        
    @no_duplicates
    @patch('finra.auth.client_from_token_file')
    def test_token_file_with_params(self, client_from_token_file):
        self.write_token()
        
        mock_client = Mock()
        client_from_token_file.return_value = mock_client
        mock_client.token_expires_in = 10_000
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path,
            is_asyncio='is_asyncio',
            mock='mock',
            test_environment='test_environment'
            )
        
        self.assertIs(c, mock_client)
        
        client_from_token_file.assert_called_once_with(
            API_KEY,
            API_SECRET,
            self.token_path,
            is_asyncio='is_asyncio',
            mock='mock',
            test_environment='test_environment'
            )
        
    @no_duplicates
    @patch('finra.auth.client_from_token_file')
    @patch('finra.auth.client_from_new_token')
    def test_token_file_token_expired(self, client_from_new_token,
                                      client_from_token_file):
        self.write_token()
        
        mock_client = Mock()
        client_from_token_file.return_value = mock_client
        mock_client.token_expires_in = -1
        
        mock_new_token_client = Mock()
        client_from_new_token.return_value = mock_new_token_client
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path
            )
        
        self.assertIs(c, mock_new_token_client)
        
    @no_duplicates
    def test_missing_token_path_and_read_write_funcs(self):
        with self.assertRaisesRegex(
            ValueError,
            "Must either provide local token path, or both token "
            "read and write functions"
            ):
            auth.get_client(API_KEY, API_SECRET)
        
    @no_duplicates
    @patch('finra.auth.client_from_storage_functions')
    def test_storage_functions(self, client_from_storage_functions):
        mock_client = Mock()
        client_from_storage_functions.return_value = mock_client
        mock_client.token_expires_in = 10_000
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_read_func='token_read_func',
            token_write_func='token_write_func'
            )
        
        self.assertIs(c, mock_client)
        
    @no_duplicates
    @patch('finra.auth.client_from_storage_functions')
    def test_storage_functions_with_params(
        self, client_from_storage_functions
        ):
        mock_client = Mock()
        client_from_storage_functions.return_value = mock_client
        mock_client.token_expires_in = 10_000
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_read_func='token_read_func',
            token_write_func='token_write_func',
            is_asyncio='is_asyncio',
            mock='mock',
            test_environment='test_environment'
            )
        
        self.assertIs(c, mock_client)
        
        client_from_storage_functions.assert_called_once_with(
            API_KEY,
            API_SECRET,
            'token_read_func',
            'token_write_func',
            is_asyncio='is_asyncio',
            mock='mock',
            test_environment='test_environment'
            )
        
    @no_duplicates
    @patch('finra.auth.client_from_storage_functions')
    @patch('finra.auth.client_from_new_token')
    def test_storage_functions_raise_exception(
        self, client_from_new_token, client_from_storage_functions
        ):
        client_from_storage_functions.side_effect = Exception()
        
        mock_client = Mock()
        client_from_new_token.return_value = mock_client
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_read_func='token_read_func',
            token_write_func='token_write_func'
            )
        
        self.assertIs(c, mock_client)
        
    @no_duplicates
    @patch('finra.auth.client_from_storage_functions')
    @patch('finra.auth.client_from_new_token')
    def test_storage_functions_token_expired(
        self, client_from_new_token, client_from_storage_functions
        ):
        mock_client = Mock()
        client_from_storage_functions.return_value = mock_client
        mock_client.token_expires_in = -1
        
        mock_new_token_client = Mock()
        client_from_new_token.return_value = mock_new_token_client
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_read_func='token_read_func',
            token_write_func='token_write_func'
            )
        
        self.assertIs(c, mock_new_token_client)
        
    @no_duplicates
    @patch('finra.auth.client_from_token_file')
    def test_negative_min_expires_in(self, client_from_token_file):
        with self.assertRaisesRegex(
                ValueError, "'min_expires_in' must be non-negative, or None"
                ):
            auth.get_client(
                API_KEY,
                API_SECRET,
                token_path=self.token_path,
                min_expires_in=-1
                )
        
    @no_duplicates
    @patch('finra.auth.client_from_token_file')
    def test_none_min_expires_in(self, client_from_token_file):
        self.write_token()
        
        mock_client = Mock()
        client_from_token_file.return_value = mock_client
        mock_client.token_expires_in = 10_000
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path,
            min_expires_in=None
            )
        
        self.assertIs(c, mock_client)
        
    @no_duplicates
    @patch('finra.auth.client_from_token_file')
    def test_zero_min_expires_in(self, client_from_token_file):
        self.write_token()
        
        mock_client = Mock()
        client_from_token_file.return_value = mock_client
        mock_client.token_expires_in = 10_000
        
        c = auth.get_client(
            API_KEY,
            API_SECRET,
            token_path=self.token_path,
            min_expires_in=0
            )
        
        self.assertIs(c, mock_client)


if __name__ == "__main__": # pragma: no cover
    unittest.main()
