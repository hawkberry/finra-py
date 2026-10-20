import unittest
from unittest.mock import patch, Mock

import httpx
import jsonschema
import referencing

from finra.filings import validator
from finra.filings.base_filing import BaseFiling

from ..common import MockOAuth2Client, MockResponse, no_duplicates


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.url = "https://schemas.api.finra.org/schema.json"
        self.headers = {'Accept': "application/json"}
        self.obj = {"test": 1}
        self.schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "test": {
                    "type": "integer",
                    "example": 1,
                    }
                },
            "required": ["test"],
            "additionalProperties": False,
            }
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('jsonschema.Draft7Validator')
    @patch('referencing.Registry')
    def test_creation(self, registry, draft7_validator, client):
        returned_registry = Mock()
        registry.return_value = returned_registry
        
        schema_registry = {}
        client.schema_registry = schema_registry
        
        v = validator.Validator(client, self.url)
        
        self.assertEqual(v.schema_registry, schema_registry)
        
        registry.assert_called_once_with(retrieve=v._retrieve)
        
        draft7_validator.assert_called_once_with(
            {"$ref": self.url}, registry=returned_registry
            )
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_retrieve_schema(self, session, client):
        session.return_value = session
        session.get.return_value = MockResponse(200, json=self.schema)
        
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        schema_registry = {} # new
        client.schema_registry = schema_registry
        
        v = validator.Validator(client, self.url)
        resource = v._retrieve(self.url)
        
        self.assertEqual(resource.contents, self.schema)
        self.assertEqual(schema_registry, {self.url: self.schema})
        
        client._prepare_headers.assert_called_once_with(True, None)
        session.get.assert_called_once_with(
            httpx.URL(self.url),
            params=None,
            headers=self.headers,
            follow_redirects=False
            )
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_retrieve_schema_missing(self, session, client):
        schema = self.schema.copy()
        del schema["$schema"] # key removed
        
        session.return_value = session
        session.get.return_value = MockResponse(200, json=schema) # missing key
        
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        schema_registry = {} # new
        client.schema_registry = schema_registry
        
        v = validator.Validator(client, self.url)
        resource = v._retrieve(self.url) # adds key here
        
        self.assertEqual(resource.contents, self.schema)
        self.assertEqual(schema_registry, {self.url: self.schema}) # key added
        
        client._prepare_headers.assert_called_once_with(True, None)
        session.get.assert_called_once_with(
            httpx.URL(self.url),
            params=None,
            headers=self.headers,
            follow_redirects=False
            )
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_retrieve_stored_schema(self, session, client):
        url = "https://some.url.com" # not an allowed subdomain
        schema_registry = {url: self.schema} # stored
        
        session.return_value = session
        
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        v = validator.Validator(client, url, schema_registry=schema_registry)
        resource = v._retrieve(url)
        
        self.assertEqual(resource.contents, self.schema)
        self.assertEqual(v.schema_registry, schema_registry)
        
        client._prepare_headers.assert_not_called()
        session.get.assert_not_called()
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_retrieve_follows_allowed_redirect(self, session, client):
        url = "https://ramp-schemas.datacollection.finra.org/schema.json"
        
        redirect = httpx.Response(
            302,
            headers={"Location": url},
            request=httpx.Request("GET", self.url)
            )
        redirect.next_request = httpx.Request("GET", url)
        
        response = httpx.Response(
            200,
            json=self.schema,
            request=httpx.Request("GET", url)
            )
        
        session.return_value = session
        session.max_redirects = 20
        session.get.side_effect = [redirect, response]
        
        client.schema_registry = {}
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        with patch.object(redirect, "close", wraps=redirect.close) as close:
            v = validator.Validator(client, self.url)
            resource = v._retrieve(self.url)
        
        self.assertEqual(resource.contents, self.schema)
        self.assertEqual(v.schema_registry, {self.url: self.schema})
        self.assertEqual(session.get.call_count, 2)
        
        get_calls = session.get.call_args_list
        self.assertEqual(get_calls[0].args[0], httpx.URL(self.url))
        self.assertEqual(get_calls[1].args[0], httpx.URL(url))
        
        self.assertEqual(client._prepare_headers.call_count, 1)
        close.assert_called_once_with()
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_retrieve_rejects_disallowed_redirect(self, session, client):
        url = "https://attacker.example/schema.json"
        
        redirect = httpx.Response(
            302,
            headers={"Location": url},
            request=httpx.Request("GET", self.url)
            )
        redirect.next_request = httpx.Request("GET", url)
        
        session.return_value = session
        session.max_redirects = 0
        session.get.return_value = redirect
        
        client.schema_registry = {}
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        with patch.object(redirect, "close", wraps=redirect.close) as close:
            with self.assertRaisesRegex(
                ValueError, "URLs must use an approved host"
                ):
                validator.Validator(client, self.url)._retrieve(self.url)

        session.get.assert_called_once()
        close.assert_called_once_with()
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    def test_retrieve_redirect_limit(self, session, client):
        first_target = (
            "https://ramp-schemas.datacollection.finra.org/first.json"
            )
        second_target = (
            "https://static.rampweb.finra.org/second.json"
            )
        
        first_redirect = httpx.Response(
            302,
            headers={"Location": first_target},
            request=httpx.Request("GET", self.url)
            )
        first_redirect.next_request = httpx.Request("GET", first_target)
        
        second_redirect = httpx.Response(
            302,
            headers={"Location": second_target},
            request=httpx.Request("GET", first_target)
            )
        second_redirect.next_request = httpx.Request("GET", second_target)
        
        session.return_value = session
        session.max_redirects = 1
        session.get.side_effect = [first_redirect, second_redirect]
        
        client.schema_registry = {}
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        with (
            patch.object(
                first_redirect, "close", wraps=first_redirect.close
                ) as first_close,
            patch.object(
                second_redirect, "close", wraps=second_redirect.close
                ) as second_close,
            ):
            with self.assertRaises(httpx.TooManyRedirects):
                validator.Validator(client, self.url)._retrieve(self.url)
        
        self.assertEqual(session.get.call_count, 2)
        first_close.assert_called_once_with()
        second_close.assert_called_once_with()
        
    @no_duplicates
    @patch('finra.client.Client')
    def test_is_valid(self, client):
        url = self.url
        obj = self.obj
        
        class NewFiling(BaseFiling):
            @property
            def schema_url(self):
                return url
            def build(self):
                return obj
        
        filing = NewFiling()
        
        retrieve = Mock()
        retrieve.return_value = referencing.Resource.from_contents(self.schema)
        
        v = validator.Validator(client, filing.schema_url)
        v._validator = jsonschema.Draft7Validator(
            {"$ref": filing.schema_url},
            registry=referencing.Registry(retrieve=retrieve)
            )
        
        self.assertTrue(v.is_valid(filing))
        self.assertTrue(v.is_valid(filing.build()))
        self.assertEqual(len(retrieve.mock_calls), 2)
        self.assertEqual(retrieve.mock_calls[-1][1][0], self.url)
        
    @no_duplicates
    @patch('finra.client.Client')
    def test_validate(self, client):
        url = self.url
        obj = self.obj
        
        class NewFiling(BaseFiling):
            @property
            def schema_url(self):
                return url
            def build(self):
                return obj
        
        filing = NewFiling()
        
        retrieve = Mock()
        retrieve.return_value = referencing.Resource.from_contents(self.schema)
        
        v = validator.Validator(client, filing.schema_url)
        v._validator = jsonschema.Draft7Validator(
            {"$ref": filing.schema_url},
            registry=referencing.Registry(retrieve=retrieve)
            )
        v.validate(filing)
        
        retrieve.assert_called_once_with(self.url)
        
    @no_duplicates
    @patch('finra.client.Client')
    def test_validate_with_another_validator_cls(self, client):
        retrieve = Mock()
        retrieve.return_value = referencing.Resource.from_contents(self.schema)
        
        v = validator.Validator(
            client,
            self.url,
            validator_cls=jsonschema.Draft202012Validator
            )
        
        self.assertEqual(
            v._validator.__class__.__name__, 'Draft202012Validator'
            )
        
        v._validator = v._validator.__class__(
            {"$ref": self.url},
            registry=referencing.Registry(retrieve=retrieve)
            )
        v.validate(self.obj)
        
        retrieve.assert_called_once_with(self.url)
        
    @no_duplicates
    @patch('finra.client.Client')
    def test_super_get_attr(self, client):
        with self.assertRaises(AttributeError):
            validator.Validator(client, self.url).missing_attribute


if __name__ == "__main__": # pragma: no cover
    unittest.main()
