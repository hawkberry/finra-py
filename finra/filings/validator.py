from typing import Any, Optional, cast

import httpx
import jsonschema
import referencing

from .._utils import validate_url
from .base_filing import BaseFiling


__all__ = ["Validator"]


# Schema retrieval requires sending the OAuth access token in many cases,
# therefore network operations are restricted to these FINRA hosts
_ALLOWED_HOSTS = (
    'datacollection-api.finra.org',
    'fingerprints.finra.org',
    'ramp-schemas.datacollection.finra.org',
    'schemas.api.finra.org',
    'static.rampweb.finra.org',
    'static.rampweb.qa.finra.org',
    )


# Custom retrieval using client, sets draft schema if missing from sub-schema
# Stores schema registry, so multiple objects can be validated, but only
# retrieve schemas once. Proxy behavior for accessing underlying validator
# methods and attributes; does not support setting attributes on underlying.
class Validator:
    """
    Client-side JSON Object Validator.
    
    This class can be used to fetch a JSON Schema from the FINRA API Platform
    and validate JSON objects against it. It can be used independently of the
    client's submission methods, but it requires a configured client instance
    to fetch schemas. Schema retrieval can require sending the access token,
    and is therefore restricted to known FINRA schema hosts.
    
    To do client-side validation, use :py:class:`Client <finra.client.Client>`.
    Integration with :py:class:`AsyncClient <finra.async_client.AsyncClient>`
    is not currently supported.
    
    This class also acts as a proxy for accessing the underlying ``jsonschema``
    validator's methods and attributes, if they haven't been overridden. See
    more about the underlying validation process `here
    <https://python-jsonschema.readthedocs.io/en/stable/validate/>`__.
    
    See more information in the :ref:`validation` tutorial.
    
    :param client: An instance of :py:class:`Client <finra.client.Client>`
    :param schema_url: The URL of the top-level JSON Schema for the object
    :param schema_registry: A ``dict`` storing the retrieved JSON Schemas
        {url: schema}. The registry is searched first before fetching a JSON
        Schema with the client. This greatly speeds up validation by preventing
        redundant network operations, particularly if the registry is re-used
        across validator instances. If a registry is not provided, one is
        created automatically. 
    :param validator_cls: The underlying validator class from the
        ``jsonschema`` library. Default: ``jsonschema.Draft7Validator``.
    """
    
    def __init__(
        self,
        client,
        schema_url: str,
        *,
        schema_registry: Optional[dict[str, Any]]=None,
        validator_cls: Optional[type]=None
        ):
        self.client = client
        self.schema_url = schema_url
        
        if schema_registry is None:
            schema_registry = client.schema_registry
        self._schema_registry = schema_registry
        
        if validator_cls is None:
            validator_cls = jsonschema.Draft7Validator
        self._validator = validator_cls(
            {"$ref": self.schema_url},
            registry=cast(Any, referencing.Registry)(retrieve=self._retrieve),
            )
        
    def __getattr__(self, name: str) -> Any:
        return getattr(self._validator, name) # raises AttributeError if DNE
    
    @property
    def schema_registry(self) -> dict[str, Any]:
        """Local schema store"""
        return self._schema_registry
    
    # Fetch a schema while validating every redirect URL
    def _get_schema_response(self, url: str | httpx.URL) -> httpx.Response:
        current_url = validate_url(url, _ALLOWED_HOSTS)
        redirects = 0
        max_redirects = self.client._session.max_redirects
        headers = self.client._prepare_headers(True, None)
        while True:
            r = self.client._session.get(
                current_url,
                params=None,
                headers=headers,
                follow_redirects=False
                )
            
            next_request = r.next_request
            if next_request is None:
                return r
            
            redirects += 1
            try:
                next_url = validate_url(next_request.url, _ALLOWED_HOSTS)
                
                if redirects > max_redirects:
                    raise httpx.TooManyRedirects(
                        "Exceeded maximum allowed schema redirects",
                        request=r.request
                        )
            finally:
                r.close()
            
            current_url = next_url
        
    # Fetch schema from URL, fetch only once, save in registry
    def _retrieve(self, url: str) -> referencing.Resource:
        if url in self._schema_registry: # from stored schema
            schema = self._schema_registry[url]
            
        else: # fetch schema using authenticated client session
            r = self._get_schema_response(url)
            r.raise_for_status()
            schema = r.json()
            
            # Set JSON Schema draft-07 standard, if the schema omits $schema
            if "$schema" not in schema:
                schema["$schema"] = "http://json-schema.org/draft-07/schema#"
            
            self._schema_registry[url] = schema  # save schema in registry
        
        return referencing.Resource.from_contents(schema)
    
    # Validate a filing object, return bool
    def is_valid(
        self,
        obj: BaseFiling | dict[str, Any]
        ) -> bool:
        """
        Validate a filing JSON object against the given FINRA JSON Schema, and
        return a bool indicating validation status.
        """
        if isinstance(obj, BaseFiling):
            obj = obj.build()
        return self._validator.is_valid(obj)
    
    # Validate a filing object, raise exception
    def validate(
        self,
        obj: BaseFiling | dict[str, Any]
        ) -> None:
        """
        Validate a filing JSON object against the given FINRA JSON Schema, and
        raise ``jsonschema.ValidationError`` if validation fails.
        """
        if isinstance(obj, BaseFiling):
            obj = obj.build()
        self._validator.validate(obj)

