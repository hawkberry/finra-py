from typing import Any, Optional, cast

import jsonschema
import referencing

from .base_filing import BaseFiling


__all__ = ["Validator"]


# Custom retrieval using client, sets draft schema if missing from sub-schema
# Stores schema registry, so multiple objects can be validated, but only
# retrieve schemas once. Proxy behavior for accessing underlying validator
# methods and attributes; does not support setting attributes on underlying.
class Validator:
    """
    Client-side JSON Object Validator.
    
    This class can be used to fetch a JSON Schema from the FINRA API Platform
    and validate JSON objects against it. It can be used outside of the client,
    however it requires an authenticated client instance to fetch the JSON
    Schemas.
    
    To do client-side validation, use :py:class:`Client <finra.client.Client>`.
    Integration with :py:class:`AsyncClient <finra.async_client.AsyncClient>`
    is not currently supported.
    
    This class also supports proxy behavior for accessing the underlying
    ``jsonschema`` validator's methods and attributes if they haven't been
    overridden. See more about the underlying validation process `here
    <https://python-jsonschema.readthedocs.io/en/stable/validate/>`__.
    
    See more information in the :ref:`validation` tutorial.
    
    :param client: An instance of :py:class:`Client <finra.client.Client>`
    :param schema_url: The URL of the top-level JSON Schema for an object
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
    
    # Fetch schema from URL, fetch only once, save in registry
    def _retrieve(self, url: str) -> referencing.Resource:
        if url in self._schema_registry: # from stored schema
            schema = self._schema_registry[url]
            
        else: # fetch schema using authenticated client session
            r = self.client._session.get(
                url,
                params=None,
                headers=self.client._prepare_headers(True, None),
                follow_redirects=True
                )
            r.raise_for_status()
            schema = r.json()
            
            # Set JSON Schema draft-07 standard, if schema attribute is missing
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
        Validate a filing JSON object against the given JSON Schema, and return
        a bool indicating validation status.
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
        Validate a filing JSON object against the given JSON Schema, and raise
        ``jsonschema.ValidationError`` if validation fails.
        """
        if isinstance(obj, BaseFiling):
            obj = obj.build()
        self._validator.validate(obj)

