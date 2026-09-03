import unittest
from unittest.mock import patch, Mock

import jsonschema
import referencing

from finra.filings import validator
from finra.filings.base_filing import BaseFiling

from ..common import MockOAuth2Client, MockResponse, no_duplicates


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.url = "https://some.url.com"
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
    @patch('referencing.Resource')
    def test_retrieve_schema(self, resource, session, client):
        resource.from_contents.return_value = "returned resource"
        
        session.return_value = session
        session.get.return_value = MockResponse(200, json=self.schema)
        
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        schema_registry = {} # new
        client.schema_registry = schema_registry
        
        v = validator.Validator(client, self.url)
        r = v._retrieve(self.url)
        
        self.assertEqual(r, "returned resource")
        self.assertEqual(schema_registry, {self.url: self.schema})
        
        client._prepare_headers.assert_called_once_with(True, None)
        session.get.assert_called_once_with(
            self.url, params=None, headers=self.headers, follow_redirects=True
            )
        resource.from_contents.assert_called_once_with(self.schema)
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('referencing.Resource')
    def test_retrieve_schema_missing(self, resource, session, client):
        schema = self.schema.copy()
        del schema["$schema"] # key removed
        
        resource.from_contents.return_value = "returned resource"
        
        session.return_value = session
        session.get.return_value = MockResponse(200, json=schema) # missing key
        
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        schema_registry = {} # new
        client.schema_registry = schema_registry
        
        v = validator.Validator(client, self.url)
        r = v._retrieve(self.url) # adds key here
        
        self.assertEqual(r, "returned resource")
        self.assertEqual(schema_registry, {self.url: self.schema}) # key added
        
        client._prepare_headers.assert_called_once_with(True, None)
        session.get.assert_called_once_with(
            self.url, params=None, headers=self.headers, follow_redirects=True
            )
        resource.from_contents.assert_called_once_with(self.schema)
        
    @no_duplicates
    @patch('finra.client.Client')
    @patch('finra.auth.OAuth2Client', new_callable=MockOAuth2Client)
    @patch('referencing.Resource')
    def test_retrieve_stored_schema(self, resource, session, client):
        resource.from_contents.return_value = "returned resource"
        
        session.return_value = session
        session.get.return_value = MockResponse(200, json=self.schema)
        
        client._prepare_headers.return_value = self.headers
        client._session = session()
        
        schema_registry = {self.url: self.schema} # stored
        
        v = validator.Validator(
            client, self.url, schema_registry=schema_registry
            )
        r = v._retrieve(self.url)
        
        self.assertEqual(r, "returned resource")
        self.assertEqual(v.schema_registry, schema_registry)
        
        client._prepare_headers.assert_not_called()
        session.get.assert_not_called()
        resource.from_contents.assert_called_once_with(self.schema)
        
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
