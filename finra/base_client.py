import inspect
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum, EnumType
from functools import wraps
from itertools import count
from typing import Any, Callable, Iterable, Optional, TypeAlias, cast
from zoneinfo import ZoneInfo

import httpx

from . import _enums
from ._utils import (
    date_isoformat, datetime_isoformat_ms, datetime_naive, LazyLog,
    )
from .enum_converter import _add_require_enums_docs, E, EnumStr, EnumConverter
from .exceptions import MockException, QATestEnvException, _type_error
from .filters import Filter, FiltersDictType
from .filings.base_filing import BaseFiling, BaseFilingOps, FilingDictType
from .filings.create_individual import CreateIndividual
from .filings.form_br import FormBR
from .filings.form_u4 import FormU4
from .filings.form_u5 import FormU5
from .filings.non_registered_fingerprint import NonRegisteredFingerprint
from .filings.validator import Validator
from .log_redactor import (
    _LOG_REDACTOR, register_redactions, register_redactions_from_response,
    )
from .token_manager import TokenManager


__all__ = [
    "BaseClient",
    "FieldsType",
    "SortFieldsType",
    ]


_TZ = ZoneInfo("America/New_York") # FINRA API server timezone


##############################################################################
# TYPES

_EndpointType: TypeAlias = EnumStr[_enums.Endpoint]
_FiltersType: TypeAlias = Filter | FiltersDictType

#: Type for a dataset query method's ``fields`` keyword, parameterized by
#: its ``Enum``.
FieldsType: TypeAlias = EnumStr[E] | Iterable[EnumStr[E]]

_SortFieldsType: TypeAlias = EnumStr[E] | tuple[int | float, EnumStr[E]]

#: Type for a dataset query method's ``sort_fields`` keyword, parameterized by
#: its ``Enum``.
SortFieldsType: TypeAlias = _SortFieldsType[E] | Iterable[_SortFieldsType[E]]



##############################################################################
# LOGGING

def get_logger() -> logging.Logger:
    """Logger for :py:mod:`base_client` module"""
    return logging.getLogger(__name__)


# Global singleton, count requests for logging
_REQUEST_COUNTER = count()


# Decorator that wraps Client methods in order to log API calls
# See debug module
# Required: request_type string for API calls
def _log_wrapper(request_type: str) -> Callable:
    logger = get_logger()
    
    log_resp = "%s: %s response: %s, content=%s"
    
    def log_response(response, request_count) -> None:
        register_redactions_from_response(response)
        logger.debug(
            log_resp, request_count, request_type, response.status_code,
            response.text.strip()
            )
        
    if request_type == "GET RESOURCE":
        log_msg = "%s: %s to %s, params=%s"
        
        def log_request(url, data) -> int:
            request_count = next(_REQUEST_COUNTER)
            register_redactions(data)
            logger.debug(
                log_msg, request_count, request_type, url,
                LazyLog(lambda: json.dumps(data, indent=4))
                )
            return request_count
        
    elif request_type == "DELETE":
        log_msg = "%s: %s to %s"
        
        def log_request(url, data) -> int:
            request_count = next(_REQUEST_COUNTER)
            logger.debug(log_msg, request_count, request_type, url)
            return request_count
        
    else: # GET, POST, PATCH, PUT
        log_msg = (
            "%s: %s to %s, params=%s"
            if request_type == "GET"
            else "%s: %s to %s, data=%s"
            ) # POST, PATCH, PUT
        
        def log_request(url, data) -> int:
            request_count = next(_REQUEST_COUNTER)
            register_redactions(data)
            logger.debug(
                log_msg, request_count, request_type, url,
                LazyLog(lambda: json.dumps(data, indent=4))
                )
            return request_count
        
    def _wrapper(func) -> Callable:
        if inspect.iscoroutinefunction(func): # AsyncClient (asynchronous)
            
            @wraps(func)
            async def wrapper(self, url, data, headers) -> httpx.Response:
                debug = logger.level <= logging.DEBUG
                if debug:
                    request_count = log_request(url, data)
                try:
                    response = await func(self, url, data, headers)
                except Exception:
                    logging.error(
                        "%s: %s", request_count, request_type, exc_info=True
                        )
                    raise
                
                if debug:
                    log_response(response, request_count)
                return response
            
        else: # Client (synchronous)
            
            @wraps(func)
            def wrapper(self, url, data, headers) -> httpx.Response:
                debug = logger.level <= logging.DEBUG
                if debug:
                    request_count = log_request(url, data)
                try:
                    response = func(self, url, data, headers)
                except Exception:
                    logging.error(
                        "%s: %s", request_count, request_type, exc_info=True
                        )
                    raise
                
                if debug:
                    log_response(response, request_count)
                return response
            
        return wrapper
    
    return _wrapper


##############################################################################
# DOCUMENTATION

def _add_client_init_docs(cls: type, session_info: Any) -> None:
    init_params = f"""
:param api_key: FINRA API key
:param session: {session_info} configured with FINRA API credentials
    and token information
:param mock: Option to use Mock API datasets. This requires the session to be
    built with Mock API credentials.
:param test_environment: Option to use the QA Test Environment. This requires
    the session to be built with QA Test Environment credentials.
:param token_manager: An instance of
    :py:class:`TokenManager <finra.token_manager.TokenManager>`
:param timeout: The session timeout for all requests made by this client.
    See :py:meth:`BaseClient.set_timeout()
    <finra.base_client.BaseClient.set_timeout>`.
:param accept_json: The default content type for requests made by this client:
    ``True`` for ``application/json``, ``False`` for ``text/plain``, or
    ``None`` for the **API's** default. See
    :py:meth:`BaseClient.set_default_accept_json()
    <finra.base_client.BaseClient.set_default_accept_json>`.
"""
    cls.__doc__ =  getattr(cls, "__doc__", "") + init_params
    _add_require_enums_docs(cls)


def _api_version_docs() -> str:
    return """
:param version: The dataset version. If ``None``, use the **API's** default.
    See :ref:`data_version`.
"""


def _add_params_docs(
    method: Callable,
    *params: str,
    enum: Optional[EnumType]=None,
    limit_default: int=1_000,
    limit_sync_max: Optional[int]=5_000,
    limit_async_max: Optional[int]=100_000
    ) -> None:
    _limit_default = format(limit_default, ",")
    if limit_sync_max is not None:
        _limit_sync_max = format(limit_sync_max, ",")
    if limit_async_max is not None:
        _limit_async_max = format(limit_async_max, ",")
    _params = []
    for p in params:
        
        # Equity / Fixed Income / FINRA
        if p == "endpoint":
            _params.append("""
:param endpoint: Query a specific resource endpoint by providing an enum
    member. Default: :py:attr:`Endpoint.DATA`. See :ref:`endpoints`.
""")
        elif p == "fields":
            if enum is None:
                raise ValueError("Missing enum")
            
            _params.append(f"""
:param fields: Request only specific data fields by providing an enum member or
    an iterable of members. Default: request all fields. See :ref:`fields`.
:type fields: :py:type:`FieldsType`\\[:py:class:`{enum.__qualname__}`]
    | :py:type:`None`
""")
        elif p == "filters":
            _params.append("""
:param filters: Perform advanced query selection by providing an instance of
    :py:class:`Filter <finra.filters.Filter>`, or equivalent JSON object.
    See :ref:`filters`.
:type filters: :py:type:`Filter <finra.filters.Filter>`
    | :py:type:`FiltersDictType <finra.filters.FiltersDictType>`
    | :py:type:`None`
""")
        elif p == "sort_fields":
            if enum is None:
                raise ValueError("Missing enum")
            
            _params.append(f"""
:param sort_fields: Sort the requested data by providing an enum member or an
    iterable of members. To reverse sort by a field, provide it as a 2-tuple
    ``(-1, <member>)``. See :ref:`sorting`.
:type sort_fields: :py:type:`SortFieldsType`\\[:py:class:`{enum.__qualname__}`]
    | :py:type:`None`
""")
        elif p == "limit":
            s = """
:param limit: The number of records to request"""
            if limit_sync_max is not None:
                s += (
                    f". Maximum value: {_limit_sync_max} "
                    "for synchronous requests"
                    )
            if limit_async_max is not None:
                s += (
                    ". Maximum value: " if limit_sync_max is None else ", or "
                    ) + f"{_limit_async_max} for asynchronous requests"
            s += (
                f". Default: {_limit_default}. See :ref:`large_datasets`."
                "\n"
                )
            _params.append(s)
        elif p == "offset":
            _params.append("""
:param offset: The record number to start with (exclusive). The index of the
    last record requested is the offset plus the limit.
""")
        elif p == "async_request":
            _params.append("""
:param async_request: The API request type: ``True`` for asynchronous
    request, ``False`` for synchronous request, or ``None`` for the **API's**
    default. See :ref:`async_requests`.
""")
        elif p == "accept_json":
            _params.append("""
:param accept_json: The content type for this request: ``True`` for
    ``application/json``, ``False`` for ``text/plain``, or ``None`` for the
    **client's** default. See :ref:`content_types`.
""")
        elif p == "delimiter":
            _params.append("""
:param delimiter: A single character that separates fields when requesting
    ``text/plain`` content. Accepted values: comma ``,``, pipe ``|``,
    tab ``\\t`` or ``\\x09``, and ctrl+A ``\\x01``. Default: comma ``,``.
""")
        elif p == "quote_values":
            _params.append("""
:param quote_values: Quote values when requesting ``text/plain`` content.
    Default: ``False``.
""")
        elif p == "version":
            _params.append(_api_version_docs())
            
        # Firm / Registration
        elif p == "firm_crd_number":
            _params.append("""
:param firm_crd_number: Firm's CRD Number
""")
        elif p == "individual_crd_number":
            _params.append("""
:param individual_crd_number: Individual's CRD Number
""")
        elif p == "date_of_birth":
            _params.append("""
:param date_of_birth: Date of Birth
""")
        elif p == "ssn":
            _params.append("""
:param ssn: Social Security Number
""")
        elif p == "last_name":
            _params.append("""
:param last_name: Individual's Last Name
""")
        elif p == "first_name":
            _params.append("""
:param first_name: Individual's First Name
""")
        # Report Card
        elif p == "period":
            _params.append("""
:param period: First day of the month for the report
""")
        elif p == "firm_market_id":
            _params.append("""
:param firm_market_id: Market Participant ID (MPID) of the requesting firm
""")
        elif p == "request_id":
            _params.append("""
:param request_id: UUID used when processing the asynchronous request. This is
    required when checking the status of the request
""")
        else:
            _all = [
                "endpoint", "fields", "filters", "sort_fields",
                "limit", "offset", "async_request", "accept_json",
                "delimiter", "quote_values", "version",
                "firm_crd_number", "individual_crd_number",
                "date_of_birth", "ssn", "last_name", "first_name",
                "period", "firm_market_id",
                ]
            unknown = ", ".join([f"'{p}'" for p in params if p not in _all])
            available = ", ".join([f"'{p}'" for p in _all])
            raise ValueError(
                f"Unknown parameters: {unknown}" + "\n"
                f"Available parameters: {available}"
                )
    
    _params.append("""
:rtype: :py:class:`httpx.Response`
""")
    method.__doc__ = (getattr(method, "__doc__") or "") + "".join(_params)


def _add_filing_params_docs(
    method: Callable,
    *params: str,
    filing_cls: Optional[str]=None,
    filing_name: Optional[str]=None
    ) -> None:
    _params = []
    for p in params:
        if p == "request_id":
            _params.append("""
:param request_id: UUID used when processing the asynchronous request. This is
    required when checking the status of the request.
""")
        elif p == "filing":
            if filing_cls is None or filing_name is None:
                raise ValueError("Expected filing_cls and filing_name")
            
            _filing_cls = filing_cls.rsplit(".", 1)[-1]
            _params.append(f"""
:param filing: Provide an instance of :py:class:`{_filing_cls}
    <{filing_cls}>`, or a valid data structure representing a {filing_name}
    filing
""")
        elif p == "put":
            _params.append("""
:param put: Use a PUT request rather than PATCH request when updating. This
    will replace the data sub-structure, rather than merging with updated data.
""")
        elif p == "delete":
            _params.append("""
:param delete: Delete a previously submitted request using the ``request_id``
    returned by the initial response. Only submissions with a ``draft`` filing
    status can be deleted. If successful, the response's ``result_status``
    field will equal ``DELETED``.
""")
        elif p == "validate":
            _params.append("""
:param validate: Validate a filing or operation on the client-side before
    submitting it to the API
""")
        elif p == "schema_url":
            _params.append("""
:param schema_url: The URL used to fetch the schema during client-side
    validation. This will override the default schema URL for a filing.
    Required if filing object does not subclass :py:class:`BaseFiling
    <finra.filings.base_filing.BaseFiling>`. The URL must include the protocol
    prefix (such as ``https://``).
""")
        elif p == "version":
            _params.append(_api_version_docs())
        else:
            _all = [
                "request_id", "filing", "put", "delete",
                "validate", "schema_url", "version",
                ]
            unknown = ", ".join([f"'{p}'" for p in params if p not in _all])
            available = ", ".join([f"'{p}'" for p in _all])
            raise ValueError(
                f"Unknown parameters: {unknown}" + "\n"
                f"Available parameters: {available}"
                )
    
    _params.append("""
:rtype: :py:class:`httpx.Response`
""")
    method.__doc__ = (getattr(method, "__doc__") or "") + "".join(_params)


##############################################################################
# BASE CLIENT

class BaseClient(EnumConverter, ABC):
    """
    Abstract base class for FINRA API :py:class:`Client <finra.client.Client>`
    and :py:class:`AsyncClient <finra.async_client.AsyncClient>`
    """
    
    def __init__(
        self,
        api_key: str,
        session: Any, # authlib typing stubs are janky
        *, mock: bool=False,
        test_environment: bool=False,
        token_manager: Optional[TokenManager]=None,
        timeout: float=30.0,
        accept_json: Optional[bool]=True,
        require_enums: bool=True
        ):
        super().__init__(require_enums)
        
        self._session = session
        
        if test_environment: # QA Test Environment
            self._base_url = "https://api-int.qa.finra.org"
        else: # Production Environment
            self._base_url = "https://api.finra.org"
        
        self._mock = mock
        self._test_environment = test_environment
        
        self._token_manager = token_manager
        
        self.set_timeout(timeout) # set default timeout, in seconds
        self.set_default_accept_json(accept_json) # set default accept type
        
        _LOG_REDACTOR.register(api_key, "API_KEY")
    
    
    ##########################################################################
    # ABSTRACT
    
    @abstractmethod
    def _get_request(self, url, params, headers):
        raise NotImplementedError
    
    @abstractmethod
    def _post_request(self, url, data, headers):
        raise NotImplementedError
    
    @abstractmethod
    def _put_request(self, url, data, headers):
        raise NotImplementedError
    
    @abstractmethod
    def _patch_request(self, url, data, headers):
        raise NotImplementedError
    
    @abstractmethod
    def _delete_request(self, url, _, headers):
        raise NotImplementedError
    
    @abstractmethod
    def _get_resource_request(self, url, params, headers):
        raise NotImplementedError
    
    @abstractmethod
    def _set_resource_session(self):
        raise NotImplementedError
    
    @abstractmethod
    def refresh_token(self):
        raise NotImplementedError
    
    @abstractmethod
    def close(self):
        raise NotImplementedError
    
    
    ##########################################################################
    # PROPERTIES
    
    @property
    def base_url(self) -> str:
        """The base URL used to create this client"""
        return self._base_url
    
    @property
    def mock(self) -> bool:
        """
        The mock endpoint setting configured when creating this client. If
        ``True``, this client will query mock dataset API endpoints. This
        setting must be accompanied by Mock API credentials.
        """
        return self._mock
    
    @property
    def test_environment(self) -> bool:
        """
        The test environment setting configured when creating this client. If
        ``True``, this client will query test environment API endpoints. This
        setting must be accompanied by Test Environment API credentials.
        """
        return self._test_environment
    
    @property
    def token_age(self) -> int:
        if self._token_manager is None:
            raise ValueError("Token Manager not set")
        return self._token_manager.token_age
    
    token_age.__doc__ = TokenManager.token_age.__doc__
    
    @property
    def token_expires_at(self) -> int:
        if self._token_manager is None:
            raise ValueError("Token Manager not set")
        return self._token_manager.expires_at
    
    token_expires_at.__doc__ = TokenManager.expires_at.__doc__
    
    @property
    def token_expires_in(self) -> int:
        if self._token_manager is None:
            raise ValueError("Token Manager not set")
        return self._token_manager.expires_in
    
    token_expires_in.__doc__ = TokenManager.expires_in.__doc__
    
    
    ##########################################################################
    # SESSION MANAGEMENT
    
    def _set_token(self, token: dict[str, Any]) -> None:
        register_redactions(token)
        if self._token_manager is None:
            raise ValueError("Token Manager not set")
        
        self._token_manager.created_timestamp = int(time.time())
        self._token_manager.update_token(token)
        get_logger().info("Retrieved and stored new token")
        
    def get_timeout(self) -> Optional[float]:
        """
        Get the session timeout for all requests made by this client
        """
        return self._session.timeout.read
    
    def set_timeout(self, timeout: Optional[float]) -> None:
        """
        Set the session timeout for all requests made by this client
        
        :param timeout: The session timeout in seconds.
        """
        self._session.timeout = httpx.Timeout(timeout)
        if hasattr(self, "_resource_session"):
            self._resource_session.timeout = httpx.Timeout(timeout)
        
    def get_default_accept_json(self) -> Optional[str]:
        """
        Get the default response content type for all requests made by this
        client
        """
        return self._session.headers.get("Accept")
    
    def set_default_accept_json(
        self,
        accept_json: Optional[bool]=True
        ) -> None:
        """
        Set the default response content type for all requests made by this
        client
        
        :param accept_json: ``True`` for ``application/json``, ``False`` for
            ``text/plain``, or ``None`` for the **API's** default.
        """
        if accept_json is None:
            self._session.headers["Accept"] = "*/*"
        elif accept_json:
            self._session.headers["Accept"] = "application/json"
        else:
            self._session.headers["Accept"] = "text/plain"
        
   # Used to override default headers for a request if values are supplied
    def _prepare_headers(
        self,
        accept_json: Optional[bool],
        version: Optional[int]
        ) -> Optional[dict[str, str]]:
        headers = {} # headers to override defaults
        if accept_json is not None: # set accept data type for this request
            if accept_json:
                headers["Accept"] = "application/json"
            else:
                headers["Accept"] = "text/plain"
        if version is not None: # set api version for this request
            headers["Data-Version"] = f"{version}"
        return headers or None # use default headers if both are None
    
    
    ##########################################################################
    # ASYNC REQUEST METHODS
    
    def get_async_request_status(self, check_status_link: str):
        """
        Asynchronous request second leg: check the status of a request.
        
        Query a check status URL, typically found in the ``Location`` header of
        a response, or in the ``checkStatusLink`` field of a response body.
        
        Response body always has json data type.
        
        Helper functions for extracting metadata from responses are available
        in the :py:mod:`utils <finra.utils>` module. Specifically see:
        :py:func:`extract_location() <finra.utils.extract_location>` and
        :py:func:`extract_check_status_link()
        <finra.utils.extract_check_status_link>`.
        
        See :ref:`async_requests` for more information and examples.
        
        :param check_status_link: Check Status Link URL
        """
        return self._get_request(
            check_status_link, None, self._prepare_headers(True, None)
            )
    
    def get_async_result(self, result_link: str):
        """
        Asynchronous request final leg: fetch the result.
        
        Query the **pre-signed** result URL returned by
        :py:meth:`BaseClient.get_async_request_status` after the response
        returns with status ``complete``.
        
        Helper functions for extracting metadata from response objects are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_status() <finra.utils.extract_status>`,
        :py:func:`extract_result_link() <finra.utils.extract_result_link>`, and
        :py:func:`extract_expires() <finra.utils.extract_expires>`.
        
        See :ref:`async_requests` for more information and examples.
        
        :param result_link: Result Link URL
        """
        if not getattr(self, "_resource_session", None):
            self._set_resource_session()
        return self._get_resource_request(result_link, None, None)
    
    
    ##########################################################################
    # QUERY API
    
    Endpoint = _enums.Endpoint
    
    @staticmethod
    def _verify_sorting_partitions(
        enum: EnumType,
        partitions: Iterable[Enum],
        filters: Optional[_FiltersType]
        ) -> None:
        if filters:
            if isinstance(filters, Filter):
                compare = filters._compareFilters
            elif isinstance(filters, dict):
                compare = filters.get("compareFilters")
            else:
                raise TypeError("filters must be a Filter object or dict")
            
            if compare:
                d = {c["fieldName"]: c["compareType"] for c in compare}
                eq = Filter.CompareType.EQUAL.value
                if all([
                    f.value in d and d[f.value] == eq for f in partitions
                    ]):
                    return
        
        enum_name = enum.__qualname__
        _partitions = [f"{enum_name}.{f.name}" for f in partitions]
        raise ValueError(
            "Using sort_fields with this dataset requires a compare filter "
            "with 'CompareType.EQUAL' for each of the following partition "
            f"fields: {', '.join(_partitions)}."
            )
    
    def _sort_fields(
        self,
        sort_fields: SortFieldsType[E],
        enum: type[E]
        ) -> list[str]:
        if isinstance(sort_fields, (Enum, str, tuple)):
            sort_fields = [sort_fields]
        
        _sort_fields = []
        for f in sort_fields:
            if isinstance(f, tuple):
                if (len(f) == 2
                    and isinstance(f[0], (int, float))
                    and isinstance(f[1], (Enum, str))):
                    _sort_fields.append(f)
                else:
                    if len(f) == 2:
                        exc_type = TypeError
                    else:
                        exc_type = ValueError
                    raise exc_type(
                        f"Received a bad tuple for sort_fields: {f}. "
                        "A sort fields tuple must have exactly two elements. "
                        "The first element must be a number 'n' to specify "
                        "the sort direction, with n >= 0 for ascending "
                        "order, or n < 0 for descending order. "
                        "The second element must be set to the field to "
                        "sort by, specified as an enum member, or a string "
                        "if require_enums=False."
                        )
            else:
                _sort_fields.append((1, f))
        
        signs, sort_fields = zip(*_sort_fields)
        return [
            "-" + f if s < 0 else f
            for s, f in zip(signs, self._convert_iterable(sort_fields, enum))
            ]
    
    # Build GET queries for non-data endpoints
    def _get_non_data_query(
        self,
        base_url: str,
        endpoint: str,
        group: str,
        name: str,
        version: Optional[int]
        ):
        if endpoint == "metadata":
            return self._get_request(
                f"{base_url}/metadata/group/{group}/name/{name}", None,
                self._prepare_headers(True, version)
                )
        
        if endpoint == "partitions":
            return self._get_request(
                f"{base_url}/partitions/group/{group}/name/{name}", None,
                self._prepare_headers(True, version)
                )
        
        if endpoint == "datasets":
            return self._get_request(
                f"{base_url}/datasets", {"group": group, "name": name},
                self._prepare_headers(True, None)
                )
        
        raise ValueError(f"Unknown resource endpoint: '{endpoint}'")
    
    # Build GET queries only for all endpoints
    # Only supports the application/json response data type
    # No support for fields, sort_fields, filters, limit or offset
    def _get_query(
        self,
        base_url: str,
        group: str,
        name: str,
        id: Optional[str],
        endpoint: Optional[_EndpointType],
        async_request: Optional[bool],
        version: Optional[int],
        **params
        ):
        if self._mock:
            name += "Mock"
        if endpoint is None: # default to data endpoint
            _endpoint = "data"
        else:
            _endpoint = self._convert(endpoint, self.Endpoint)
        if _endpoint == "data":
            
            if id is not None: # id subpath
                name += f"/{id}"
            if async_request is not None:
                params["async"] = async_request
            return self._get_request(
                f"{base_url}/data/group/{group}/name/{name}", params,
                self._prepare_headers(True, version)
                )
        
        return self._get_non_data_query(
            base_url, _endpoint, group, name, version
            )
    
    # Build all query types for all endpoints
    # Supports POST to data endpoint
    # Filters support one additional type, constructed internally by one method
    def _query(
        self,
        base_url: str,
        group: str,
        name: str,
        id: Optional[str],
        enum: Optional[type[E]],
        partitions: Iterable[E],
        endpoint: Optional[_EndpointType],
        fields: Optional[FieldsType[E]],
        filters: Optional[_FiltersType | dict[str, dict[str, list[int]]]],
        sort_fields: Optional[SortFieldsType[E]],
        limit: Optional[int],
        offset: int,
        async_request: Optional[bool],
        accept_json: Optional[bool],
        delimiter: Optional[str],
        quote_values: Optional[bool],
        version: Optional[int],
        **params
        ):
        if self._mock:
            name += "Mock"
        if endpoint is None: # default to data endpoint
            _endpoint = "data"
        else:
            _endpoint = self._convert(endpoint, self.Endpoint)
        if _endpoint == "data":
            _fields: Optional[list[str]] = None
            _sort_fields: Optional[list[str]] = None
            if id is not None: # id subpath
                name += f"/{id}"
            if fields:
                _fields = self._convert_iterable(
                    fields, cast(type[E], enum)
                    )
            if sort_fields:
                enum = cast(type[E], enum)
                if partitions: # partition fields require filter & POST
                    filters = cast(Optional[_FiltersType], filters)
                    self._verify_sorting_partitions(enum, partitions, filters)
                _sort_fields = self._sort_fields(sort_fields, enum)
            if limit is not None:
                params["limit"] = limit
            if offset > 0: # works for GET even though it's undocumented by API
                params["offset"] = offset
            if quote_values is not None:
                params["quoteValues"] = quote_values
            if delimiter is not None:
                params["delimiter"] = delimiter
            if async_request is not None:
                params["async"] = async_request
            if filters is not None: # POST
                if _fields is not None:
                    params["fields"] = _fields
                if _sort_fields is not None:
                    params["sortFields"] = _sort_fields
                if filters:
                    if isinstance(filters, Filter):
                        filters = filters.build()
                    elif not isinstance(filters, dict):
                        raise TypeError(
                            "filters must be a Filter object or dict"
                            )
                    params.update(filters)
                return self._post_request(
                    f"{base_url}/data/group/{group}/name/{name}", params,
                    self._prepare_headers(accept_json, version)
                    )
            
            if _fields is not None: # comma-deliminate iterables for GET params
                params["fields"] = ",".join(_fields)
            if _sort_fields is not None:
                params["sortFields"] = ",".join(_sort_fields)
            return self._get_request(
                f"{base_url}/data/group/{group}/name/{name}", params,
                self._prepare_headers(accept_json, version)
                )
        
        return self._get_non_data_query(
            base_url, _endpoint, group, name, version
            )
    
    
    ##########################################################################
    # DATASETS
    
    Groups = _enums.Groups
    EquityGroup = _enums.EquityGroup
    FixedIncomeGroup = _enums.FixedIncomeGroup
    FINRAGroup = _enums.FINRAGroup
    FirmGroup = _enums.FirmGroup
    RegistrationGroup = _enums.RegistrationGroup
    ReportCardGroup = _enums.ReportCardGroup
    
    def get_datasets(
        self,
        group: Optional[EnumStr[_enums.Groups]]=None,
        name: Optional[
            _enums.EquityGroup |
            _enums.FixedIncomeGroup |
            _enums.FINRAGroup |
            _enums.FirmGroup |
            _enums.RegistrationGroup |
            _enums.ReportCardGroup | str
            ]=None
        ):
        """
        The datasets resource endpoint returns information about the
        capabilities and features supported by each Query API dataset,
        including query methods, data format, versioning, and whether or not it
        is currently active.
        
        Depending on the provided arguments, this endpoint will return
        information for all datasets, all datasets in a group, or a specific
        production dataset by name. If no arguments are provided, all datasets
        available through this endpoint are returned, including undocumented
        and unsupported datasets.
        
        This information is also accessible via a dataset's query method using
        the ``endpoint`` keyword. For more information and examples see
        :ref:`endpoints`.
        
        Most of the response fields from this endpoint are self-explanatory,
        however detailed descriptions can be found in the `Datasets schema
        <https://schemas.api.finra.org/FINRAApiPlatformDatasetsDetail.json>`__.
        
        :param group: Return only datasets belonging to an API group by
            providing a member of :py:class:`Groups`
        :param name: Return a specific dataset by name by providing a member of
            one of the expected group enums
        """
        params = {}
        if group is not None:
            params["group"] = self._convert(group, self.Groups)
        if name is not None:
            params["name"] = self._convert_union(
                name, (
                    self.EquityGroup,
                    self.FixedIncomeGroup,
                    self.FINRAGroup,
                    self.FirmGroup,
                    self.RegistrationGroup,
                    self.ReportCardGroup,
                    )
                )
        return self._get_request(
            self._base_url + "/datasets", params,
            self._prepare_headers(True, None)
            )
    
    
    ##########################################################################
    # EQUITY GROUP
    
    ATSBlockSummary = _enums.ATSBlockSummary
    
    def get_ats_block_summary(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.ATSBlockSummary]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.ATSBlockSummary]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Aggregated ATS trade data in NMS stocks that meets certain share based
        and dollar based thresholds.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.ATSBlockSummary.MONTH_START_DATE]
        return self._query(
            self._base_url, "otcMarket", "blocksSummary", None,
            self.ATSBlockSummary,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_ats_block_summary, "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=ATSBlockSummary,
        )
    
    OTCBlockSummary = _enums.OTCBlockSummary
    
    def get_otc_block_summary(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.OTCBlockSummary]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.OTCBlockSummary]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Aggregated OTC (Non-ATS) trade data in NMS stocks that meets certain
        share based and dollar based thresholds.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.OTCBlockSummary.MONTH_START_DATE]
        return self._query(
            self._base_url, "otcMarket", "otcBlocksSummary", None,
            self.OTCBlockSummary,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_otc_block_summary, "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=OTCBlockSummary
        )
    
    ConsolidatedShortInterest = _enums.ConsolidatedShortInterest
    
    def get_consolidated_short_interest(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.ConsolidatedShortInterest]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.ConsolidatedShortInterest
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        A single view of OTC short interest positions submitted across all
        exchanges.
        
        `FINRA Rule 4560
        <https://www.finra.org/rules-guidance/rulebooks/finra-rules/4560>`__
        requires FINRA member firms to report their short
        positions in all over-the-counter (OTC) equity securities to FINRA.
        OTC equity short interest is available for view by issue, or by
        downloadable pipe-delimited (``|``) text file containing all OTC equity
        securities reported with a short position. Data is available online for
        one rolling year based on the settlement date provided in the Short
        Interest Reporting Deadlines.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.ConsolidatedShortInterest.SETTLEMENT_DATE]
        return self._query(
            self._base_url, "otcMarket", "consolidatedShortInterest", None,
            self.ConsolidatedShortInterest,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_consolidated_short_interest,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=ConsolidatedShortInterest
        )
    
    DailyShortSaleVolume = _enums.DailyShortSaleVolume
    
    def get_daily_short_sale_volume(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.DailyShortSaleVolume]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.DailyShortSaleVolume
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        `Regulation SHO <https://www.sec.gov/investor/pubs/regsho.htm>`__ daily
        short sale volume.
        
        Daily short sale aggregated volume by security for all short sale
        trades executed and reported to a FINRA trade reporting facility.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.DailyShortSaleVolume.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "otcMarket", "regShoDaily", None,
            self.DailyShortSaleVolume,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_daily_short_sale_volume,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=DailyShortSaleVolume
        )
    
    ThresholdList = _enums.ThresholdList
    
    def get_threshold_list(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.ThresholdList]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.ThresholdList]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        OTC Regulation SHO and FINRA Rule 4320 Threshold Securities.
        
        Pursuant to `Rule 203(b)(3) of Regulation SHO
        <https://www.sec.gov/investor/pubs/regsho.htm>`__
        and `FINRA Rule 4320
        <https://www.finra.org/rules-guidance/rulebooks/finra-rules/4320>`__,
        a participant of a registered clearing agency (i.e., a clearing firm),
        that has a fail to deliver position at a registered clearing agency
        (i.e., National Securities Clearing Corporation) in a Threshold
        Security for 13 consecutive settlement days must immediately close out
        that fail to deliver position by purchasing shares of like kind and
        quantity.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.ThresholdList.TRADE_DATE]
        return self._query(
            self._base_url, "otcMarket", "thresholdList", None,
            self.ThresholdList,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_threshold_list,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=ThresholdList
        )
    
    WeeklySummary = _enums.WeeklySummary
    
    def get_weekly_summary(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.WeeklySummary]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.WeeklySummary]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Weekly aggregate trade data for OTC (ATS and non-ATS) trading data for
        each ATS/firm with trade reporting obligations under FINRA rules.
        
        The production dataset contains a rolling twelve months of data.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [
            self.WeeklySummary.WEEK_START_DATE,
            self.WeeklySummary.TIER_IDENTIFIER,
            ]
        return self._query(
            self._base_url, "otcMarket", "weeklySummary", None,
            self.WeeklySummary,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_weekly_summary,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=WeeklySummary
        )
    
    def get_weekly_summary_historic(
        self,
        week_start_date: Optional[date | datetime]=None,
        *,
        historical_week: Optional[date | datetime]=None,
        historical_month: Optional[date | datetime]=None,
        tier_identifier: Optional[str]=None,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.WeeklySummary]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Historic OTC Transparency Weekly Summary.
        
        The datasets provides a historical 4-year rolling window of data
        starting with one year prior to the current date.

        The :py:attr:`Endpoint.DATA` resource endpoint requires EXACTLY one of
        the following fields be provided: ``week_start_date``,
        ``historical_week``, or ``historical_month``. The ``tier_identifier``
        can optionally be provided as an additional query parameter.
        
        Due to the volume of data, use an async request (by setting
        ``async_request=True``) whenever querying time periods that exceed one
        week, or if timeout errors occur. Data older than one year is static
        and is not updated. Do not repeatedly download older data expecting
        updates.
        
        In addition, this dataset does not support sorting or filtering.
        
        No mock API available.
        
        Requires Public, Firm or Organization API credentials.
        
        :param week_start_date: Date field that must be a Monday. If a date
            other than a Monday is provided no data will be returned.
        :param historical_week: If a date other than a Monday is provided the
            platform will calculate the corresponding ``week_start_date`` for
            the provided date.
        :param historical_month: The platform will provide all data with a
            ``week_start_date`` within the month provided.
        :param tier_identifier: Tier identifier. Known values:
            
            - ``T1`` : Securities included in the S&P 500, Russell 1000 and
              selected exchange-traded products
            - ``T2`` : All other NMS stocks
            - ``OTCE`` : Over-the-Counter equity securities
            - ``NMS`` : ??? (undocumented)
            - ``NA`` : Not applicable (undocumented)
            
        """
        if self._mock:
            raise MockException()
        
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or (not self.require_enums and endpoint == "data")):
            
            # Data endpoint requires exactly one of these fields with...
            # ...EQUAL compare filter
            if week_start_date is not None:
                if not isinstance(week_start_date, date):
                    _type_error(
                        "week_start_date", week_start_date, (date, datetime)
                        )
                filters = {"compareFilters": [{
                    "fieldName": "weekStartDate",
                    "fieldValue": date_isoformat(week_start_date),
                    "compareType": "EQUAL",
                    }]}
            elif historical_week is not None:
                if not isinstance(historical_week, date):
                    _type_error(
                        "historical_week", historical_week, (date, datetime)
                        )
                filters = {"compareFilters": [{
                    "fieldName": "historicalWeek",
                    "fieldValue": date_isoformat(historical_week),
                    "compareType": "EQUAL",
                    }]}
            elif historical_month is not None:
                if isinstance(historical_month, datetime):
                    pass
                elif isinstance(historical_month, date): # convert to datetime
                    historical_month = datetime.combine(
                        historical_month, datetime.min.time()
                        )
                else:
                    _type_error(
                        "historical_month", historical_month, (date, datetime)
                        )
                filters = {"compareFilters": [{
                    "fieldName": "historicalMonth",
                    "fieldValue": historical_month.strftime("%Y-%m"), # yyyy-MM
                    "compareType": "EQUAL",
                    }]}
            else:
                raise ValueError(
                    "When querying the DATA resource endpoint, EXACTLY one "
                    "of the following must be provided as a datetime.date: "
                    "'week_start_date', 'historical_week', or "
                    "'historical_month'."
                    )
            
            # Additional optional field with EQUAL compare filter
            if tier_identifier is not None:
                if not isinstance(tier_identifier, str):
                    _type_error("tier_identifier", tier_identifier, (str,))
                filters["compareFilters"].append({
                    "fieldName": "tierIdentifier",
                    "fieldValue": tier_identifier.upper(),
                    "compareType": "EQUAL",
                    })
        else:
            filters = None
        
        partitions = [
            self.WeeklySummary.WEEK_START_DATE,
            self.WeeklySummary.TIER_IDENTIFIER,
            ]
        return self._query(
            self._base_url, "otcMarket", "weeklySummaryHistoric", None,
            self.WeeklySummary,
            partitions, endpoint, fields, filters, None, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_weekly_summary_historic,
        "endpoint", "fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=WeeklySummary
        )
    
    MonthlySummary = _enums.MonthlySummary
    
    def get_monthly_summary(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.MonthlySummary]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.MonthlySummary]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Monthly aggregate trade data for OTC (non-ATS) trading data for each
        firm with trade reporting obligations under FINRA rules.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [
            self.MonthlySummary.MONTH_START_DATE,
            self.MonthlySummary.TIER_IDENTIFIER,
            ]
        return self._query(
            self._base_url, "otcMarket", "monthlySummary", None,
            self.MonthlySummary,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_monthly_summary,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=MonthlySummary
        )
    
    OTCDailyList = _enums.OTCDailyList
    
    def get_otc_daily_list(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.OTCDailyList]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.OTCDailyList]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        OTC Daily List is a list of new issues, deleted issues, symbol and name
        changes, and other corporate actions for over-the-counter (OTC) equity
        securities, as well as historical OTC Bulletin Board (OTCBB)
        securities. OTCBB was a FINRA interdealer quotation system that was
        retired in November 2021. The dataset provides the same data as
        available at `OTCE Daily List
        <https://otce.finra.org/otce/dailyList>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.OTCDailyList.CALENDAR_DAY]
        return self._query(
            self._base_url, "otcMarket", "otcDailyList", None,
            self.OTCDailyList,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_otc_daily_list,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=OTCDailyList
        )
    
    
    ##########################################################################
    # FIXED INCOME GROUP
    
    AgencyTBAPricing = _enums.AgencyTBAPricing
    
    def get_agency_tba_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyTBAPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Agency Pass-Thru Mortgage-Backed
        Securities (MBS) traded on To-Be-Announced (TBA), Standardized Trade
        Information Protocol (STIP), and Dollar Roll basis.
        
        This dataset covers Single Family 15-year and 30-year pools issued by
        UMBS (Uniform MBS, the joint Fannie Mae / Freddie Mac security), FHLMC
        (Freddie Mac), and GNMA (Ginnie Mae).
        
        Returned data follows the `Agency TBA Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/agencyTbaPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyTBAPricing", None,
            self.AgencyTBAPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_agency_tba_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version", enum=AgencyTBAPricing
        )
    
    AgencyCMOPricing = _enums.AgencyCMOPricing
    
    def get_agency_cmo_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyCMOPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Agency Collateralized Mortgage Obligation
        (CMO) by deal vintage.
        
        Returned data follows the `Agency CMO Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/agencyCmoPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyCMOPricing", None,
            self.AgencyCMOPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_agency_cmo_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version", enum=AgencyCMOPricing
        )
    
    AgencyDebtMarketBreadth = _enums.AgencyDebtMarketBreadth
    
    def get_agency_debt_market_breadth(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyDebtMarketBreadth]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.AgencyDebtMarketBreadth
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE market breadth calculations for Agency debt securities.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.AgencyDebtMarketBreadth.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyMarketBreadth", None,
            self.AgencyDebtMarketBreadth,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_agency_debt_market_breadth,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=AgencyDebtMarketBreadth
        )
    
    AgencyDebtMarketSentiment = _enums.AgencyDebtMarketSentiment
    
    def get_agency_debt_market_sentiment(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyDebtMarketSentiment]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.AgencyDebtMarketSentiment
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE market sentiment calculations for Agency debt securities.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.AgencyDebtMarketSentiment.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyMarketSentiment", None,
            self.AgencyDebtMarketSentiment,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_agency_debt_market_sentiment,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=AgencyDebtMarketSentiment
        )
    
    AgencyMBSTradingActivity = _enums.AgencyMBSTradingActivity
    
    def get_agency_mbs_trading_activity(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyMBSTradingActivity]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily trading activity statistics for Agency Mortgage-Backed Securities
        (MBS).
        
        Returned data follows the `Agency MBS Trading Activity schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/agencyMbsTradingActivity.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyMBSTradingActivity",
            None,
            self.AgencyMBSTradingActivity,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_agency_mbs_trading_activity,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version",
        enum=AgencyMBSTradingActivity
        )
    
    AgencyMBSARMHybridPricing = _enums.AgencyMBSARMHybridPricing
    
    def get_agency_mbs_arm_hybrid_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyMBSARMHybridPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Agency Pass-Thru adjustable-rate (ARM) and
        hybrid Mortgage-Backed Securities (MBS).
        
        Returned data follows the `Agency MBS ARM Hybrid Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/agencyMbsArmHybridPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyMBSArmHybridPricing",
            None,
            self.AgencyMBSARMHybridPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_agency_mbs_arm_hybrid_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version",
        enum=AgencyMBSARMHybridPricing
        )
    
    AgencyMBSPricing = _enums.AgencyMBSPricing
    
    def get_agency_mbs_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.AgencyMBSPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for specified Agency Pass-Thru fixed-rate
        Mortgage-Backed Securities (MBS).
        
        This dataset covers fixed-rate products: Single Family 15-year, Single
        Family 30-year, and other fixed-rate term variants for UMBS, FHLMC, and
        GNMA. 
        
        Returned data follows the `Agency MBS Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/agencyMbsPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "agencyMBSPricing", None,
            self.AgencyMBSPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_agency_mbs_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version", enum=AgencyMBSPricing
        )
    
    CollateralizedObligationsPricing = \
        _enums.CollateralizedObligationsPricing
    
    def get_collateralized_obligations_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.CollateralizedObligationsPricing
            ]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Collateralized Bond Obligations (CBOs),
        Collateralized Debt Obligations (CDOs), and Collateralized Loan
        Obligations (CLOs) by credit tier and vintage.
        
        Returned data follows the `Collateralized Obligation Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/collateralizedObligationPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket",
            "collateralizedObligationPricing", None,
            self.CollateralizedObligationsPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_collateralized_obligations_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version",
        enum=CollateralizedObligationsPricing
        )
    
    Corporate144ADebtMarketBreadth = \
        _enums.Corporate144ADebtMarketBreadth
    
    def get_corporate_144a_debt_market_breadth(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.Corporate144ADebtMarketBreadth
            ]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.Corporate144ADebtMarketBreadth
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE market breadth calculations for Rule 144A corporate debt
        securities.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.Corporate144ADebtMarketBreadth.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "corporate144AMarketBreadth",
            None,
            self.Corporate144ADebtMarketBreadth,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_corporate_144a_debt_market_breadth,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version",
        enum=Corporate144ADebtMarketBreadth
        )
    
    Corporate144ADebtMarketSentiment = \
        _enums.Corporate144ADebtMarketSentiment
    
    def get_corporate_144a_debt_market_sentiment(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.Corporate144ADebtMarketSentiment
            ]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.Corporate144ADebtMarketSentiment
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE market sentiment calculations for Rule 144A corporate debt
        securities.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.Corporate144ADebtMarketSentiment.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket",
            "corporate144AMarketSentiment", None,
            self.Corporate144ADebtMarketSentiment,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_corporate_144a_debt_market_sentiment,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version",
        enum=Corporate144ADebtMarketSentiment
        )
    
    CorporateAndAgencyCappedVolume = \
        _enums.CorporateAndAgencyCappedVolume
    
    def get_corporate_and_agency_capped_volume(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.CorporateAndAgencyCappedVolume
            ]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.CorporateAndAgencyCappedVolume
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE capped volume calculations for corporate and agency debt.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.CorporateAndAgencyCappedVolume.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket",
            "corporatesAndAgenciesCappedVolume", None,
            self.CorporateAndAgencyCappedVolume,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_corporate_and_agency_capped_volume,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version",
        enum=CorporateAndAgencyCappedVolume
        )
    
    CorporateDebtMarketBreadth = _enums.CorporateDebtMarketBreadth
    
    def get_corporate_debt_market_breadth(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.CorporateDebtMarketBreadth]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.CorporateDebtMarketBreadth
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE market breadth calculations for corporate debt securities.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.CorporateDebtMarketBreadth.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "corporateMarketBreadth",
            None,
            self.CorporateDebtMarketBreadth,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_corporate_debt_market_breadth,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=CorporateDebtMarketBreadth
        )
    
    CorporateDebtMarketSentiment = _enums.CorporateDebtMarketSentiment
    
    def get_corporate_debt_market_sentiment(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.CorporateDebtMarketSentiment]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.CorporateDebtMarketSentiment
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE market sentiment calculations for corporate debt securities.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.CorporateDebtMarketSentiment.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "corporateMarketSentiment",
            None,
            self.CorporateDebtMarketSentiment,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_corporate_debt_market_sentiment,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version",
        enum=CorporateDebtMarketSentiment
        )
    
    DailyCMBSPricing = _enums.DailyCMBSPricing
    
    def get_daily_cmbs_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.DailyCMBSPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Commercial Mortgage-Backed Securities
        (CMBS) by deal vintage.
        
        Returned data follows the `Daily CMBS Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/dailyCmbsPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "dailyCMBSPricing", None,
            self.DailyCMBSPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_daily_cmbs_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version", enum=DailyCMBSPricing
        )
    
    NonAgencyCMOABSPricing = _enums.NonAgencyCMOABSPricing
    
    def get_non_agency_cmo_abs_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.NonAgencyCMOABSPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Non-Agency Collateralized Mortgage
        Obligations (CMOs) and Asset-Backed Securities (ABS) by product.
        
        Returned data follows the `Non-Agency CMO ABS Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/nonAgencyCmoAbsPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "nonAgencyCMOABSPricing",
            None,
            self.NonAgencyCMOABSPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_non_agency_cmo_abs_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version",
        enum=NonAgencyCMOABSPricing
        )
    
    NonAgencyCMOPricing = _enums.NonAgencyCMOPricing
    
    def get_non_agency_cmo_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.NonAgencyCMOPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily pricing statistics for Non-Agency Collateralized Mortgage
        Obligation (CMO) P&I securities by deal vintage.
        
        Returned data follows the `Non-Agency CMO Vintage Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/nonAgencyCmoVintagePricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "nonAgencyCMOVintagePricing",
            None,
            self.NonAgencyCMOPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_non_agency_cmo_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version", enum=NonAgencyCMOPricing
        )
    
    SecuritizedProductsCappedVolume = \
        _enums.SecuritizedProductsCappedVolume
    
    def get_securitized_products_capped_volume(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.SecuritizedProductsCappedVolume
            ]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.SecuritizedProductsCappedVolume
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        TRACE capped volume calculations for securitized products.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.SecuritizedProductsCappedVolume.TRADE_REPORT_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket",
            "securitizedProductsCappedVolume", None,
            self.SecuritizedProductsCappedVolume,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_securitized_products_capped_volume,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version",
        enum=SecuritizedProductsCappedVolume
        )
    
    SecuritizedProductsErrata = _enums.SecuritizedProductsErrata
    
    def get_securitized_products_errata(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.SecuritizedProductsErrata]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Cumulative log of corrections to previously published securitized
        products data.
        
        Returned data follows the `Securitized Products Data Errata schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/securitizedProductErrata.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "securitizedProductErrata",
            None,
            self.SecuritizedProductsErrata,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_securitized_products_errata,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version",
        enum=SecuritizedProductsErrata
        )
    
    SecuritizedProductsTradingActivity = \
        _enums.SecuritizedProductsTradingActivity
    
    def get_securitized_products_trading_activity(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.SecuritizedProductsTradingActivity
            ]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily trading activity statistics for securitized products other than
        Agency Pass-Thru Mortgage-Backed Securities (MBS), including Non-Agency
        MBS and Commercial Mortgage-Backed Securities (CMBS).
        
        Returned data follows the `Securitized Product Trading Activity schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/securitizedProductTradingActivity.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket",
            "securitizedProductTradingActivity", None,
            self.SecuritizedProductsTradingActivity,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_securitized_products_trading_activity,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version",
        enum=SecuritizedProductsTradingActivity
        )
    
    TreasuryDailyAggregates = _enums.TreasuryDailyAggregates
    
    def get_treasury_daily_aggregates(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.TreasuryDailyAggregates]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.TreasuryDailyAggregates
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Daily trading volume in US Treasury Securities reported to TRACE.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.TreasuryDailyAggregates.TRADE_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "treasuryDailyAggregates",
            None,
            self.TreasuryDailyAggregates,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_treasury_daily_aggregates,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=TreasuryDailyAggregates
        )
    
    TreasuryMonthlyAggregates = _enums.TreasuryMonthlyAggregates
    
    def get_treasury_monthly_aggregates(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.TreasuryMonthlyAggregates]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.TreasuryMonthlyAggregates
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Monthly trading volume in US Treasury Securities reported to TRACE.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.TreasuryMonthlyAggregates.BEGINNING_OF_MONTH_DATE]
        return self._query(
            self._base_url, "fixedIncomeMarket", "treasuryMonthlyAggregates",
            None,
            self.TreasuryMonthlyAggregates,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_treasury_monthly_aggregates,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=TreasuryMonthlyAggregates
        )
    
    WeeklyCMBSPricing = _enums.WeeklyCMBSPricing
    
    def get_weekly_cmbs_pricing(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.WeeklyCMBSPricing]]=None,
        filters: Optional[_FiltersType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Weekly pricing statistics for Agency Commercial Mortgage-Backed
        Securities (CMBS) by deal vintage, aggregated across a full
        Monday-to-Friday trading week.
        
        Returned data follows the `Weekly CMBS Pricing schema
        <https://schemas.api.finra.org/v1/
        fixedIncomeMarket/weeklyCmbsPricing.json>`__.
        
        Requires Public, Firm or Organization API credentials.
        """
        return self._query(
            self._base_url, "fixedIncomeMarket", "weeklyCMBSPricing",
            None,
            self.WeeklyCMBSPricing,
            [], endpoint, fields, filters or {}, None, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_weekly_cmbs_pricing,
        "endpoint", "fields", "filters", 
        "limit", "offset", "async_request", "version", enum=WeeklyCMBSPricing
        )
    
    
    ##########################################################################
    # FINRA GROUP
    
    FINRARulebook = _enums.FINRARulebook
    
    def get_finra_rulebook(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.FINRARulebook]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.FINRARulebook]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        FINRA's current and historical rules and regulations.
        
        Requires Firm or Organization API credentials.
        """
        partitions = [self.FINRARulebook.RULE_NUMBER]
        return self._query(
            self._base_url, "finra", "finraRulebook", None,
            self.FINRARulebook,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_finra_rulebook,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "version", enum=FINRARulebook
        )
    
    FirmsRegistrationTypes = _enums.FirmsRegistrationTypes
    
    def get_firm_registration_types(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.FirmsRegistrationTypes]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.FirmsRegistrationTypes
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Industry Snapshot - Firm Registration Types.
        
        Breakdown of securities industry registered firms by type of
        registration.
        
        Requires Public, Firm or Organization API credentials.
        """
        partitions = [self.FirmsRegistrationTypes.REPORT_DATE]
        return self._query(
            self._base_url, "finra", "industrySnapshotFirmsByRegistrationType",
            None,
            self.FirmsRegistrationTypes,
            partitions, endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_firm_registration_types,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=FirmsRegistrationTypes
        )
    
    
    ##########################################################################
    # FIRM GROUP
    
    FirmCustomerComplaints = _enums.FirmCustomerComplaints
    
    def get_firm_customer_complaints(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.FirmCustomerComplaints]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.FirmCustomerComplaints
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        accept_json: Optional[bool]=None,
        delimiter: Optional[str]=None,
        quote_values: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Form 4530 customer complaint filings submitted against the firm.
        
        No partition field.
        
        Requires Firm API credentials.
        """
        return self._query(
            self._base_url, "firm", "4530filings", None,
            self.FirmCustomerComplaints,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, accept_json, delimiter, quote_values, version
            )
    
    _add_params_docs(
        get_firm_customer_complaints,
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "accept_json",
        "delimiter", "quote_values", "version", enum=FirmCustomerComplaints
        )
    
    FirmDisclosures = _enums.FirmDisclosures
    
    def get_firm_disclosures(
        self,
        firm_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.FirmDisclosures]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.FirmDisclosures]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Firm disclosure information.
        
        The ``firm_crd_number`` can optionally be passed as an argument when
        querying the :py:attr:`Endpoint.DATA` resource endpoint.
        
        No partition field.
        
        Requires Firm API credentials.
        """
        return self._query(
            self._base_url, "firm", "firmDisclosures",
            None if firm_crd_number is None else f"id/{firm_crd_number}",
            self.FirmDisclosures,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_firm_disclosures,
        "firm_crd_number",
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "version", enum=FirmDisclosures
        )
    
    FirmProfile = _enums.FirmProfile
    
    def get_firm_profile(
        self,
        firm_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.FirmProfile]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.FirmProfile]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Basic information about a firm.
        
        The ``firm_crd_number`` can optionally be passed as an argument when
        querying the :py:attr:`Endpoint.DATA` resource endpoint.
        
        No partition field.
        
        Requires Firm API credentials.
        """
        return self._query(
            self._base_url, "firm", "firmProfile",
            None if firm_crd_number is None else f"id/{firm_crd_number}",
            self.FirmProfile,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_firm_profile,
        "firm_crd_number",
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "version", enum=FirmProfile
        )
    
    FirmRegistrationStatusHistory = _enums.FirmRegistrationStatusHistory
    
    def get_firm_registration_status_history(
        self,
        firm_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.FirmRegistrationStatusHistory
            ]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.FirmRegistrationStatusHistory
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        A complete listing of registration notices for a firm.
        
        The ``firm_crd_number`` can optionally be passed as an argument when
        querying the :py:attr:`Endpoint.DATA` resource endpoint.
        
        No partition field.
        
        Requires Firm API credentials.
        """
        return self._query(
            self._base_url, "firm", "firmRegistrationStatusHistory",
            None if firm_crd_number is None else f"id/{firm_crd_number}",
            self.FirmRegistrationStatusHistory,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_firm_registration_status_history,
        "firm_crd_number",
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "version",
        enum=FirmRegistrationStatusHistory
        )
    
    FirmRegistrations = _enums.FirmRegistrations
    
    def get_firm_registrations(
        self,
        firm_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[_enums.FirmRegistrations]]=None,
        filters: Optional[_FiltersType]=None,
        sort_fields: Optional[SortFieldsType[_enums.FirmRegistrations]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Firm registration information.
        
        The ``firm_crd_number`` can optionally be passed as an argument when
        querying the :py:attr:`Endpoint.DATA` resource endpoint.
        
        No partition field.
        
        Requires Firm API credentials.
        """
        return self._query(
            self._base_url, "firm", "firmRegistrations",
            None if firm_crd_number is None else f"id/{firm_crd_number}",
            self.FirmRegistrations,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_firm_registrations,
        "firm_crd_number",
        "endpoint", "fields", "filters", "sort_fields",
        "limit", "offset", "async_request", "version",
        enum=FirmRegistrations
        )
    
    
    ##########################################################################
    # REGISTRATION GROUP
    
    # This dataset only supports GET requests to DATA endpoint
    def get_accounting(
        self,
        start_date: Optional[date | datetime]=None,
        end_date: Optional[date | datetime]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        CRD accounting transactions of the requesting firm for a given date
        range, up to 30 days prior to today.
        
        Returned data follows the `Accounting schema
        <https://static.rampweb.finra.org/schemas/accounting.json>`__.
        
        The ``start_date`` cannot be more than 30 days prior to today's date in
        the Eastern timezone.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        
        :param start_date: Date of the start of the query window.
            Default: 30 days prior to today.
        :param end_date: Date of the end of the query window
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if start_date is None: # default 30 days ago
                start_date = datetime.now(_TZ).date() - timedelta(days=30)
            else:
                if isinstance(start_date, datetime):
                    start_date = start_date.date()
                elif not isinstance(start_date, date):
                    _type_error("start_date", start_date, (date, datetime))
                now = datetime.now(_TZ).date()
                if (now - start_date).days > 30:
                    raise ValueError(
                        "start_date cannot be more than 30 days prior to "
                        "today's date in the Eastern timezone"
                        )
            
            params = {"startDate": start_date.isoformat()}
            if end_date is not None:
                if isinstance(end_date, datetime):
                    end_date = end_date.date()
                elif not isinstance(end_date, date):
                    _type_error("end_date", end_date, (date, datetime))
                now = datetime.now(_TZ).date()
                if (end_date - now).days > 0:
                    raise ValueError("end_date cannot be in the future")
                
                params["endDate"] = end_date.isoformat()
        else:
            params = {}
        
        return self._get_query(
            self._base_url, "registration", "accounting", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(get_accounting, "endpoint", "version")
    
    # This dataset only supports POST requests to DATA endpoint
    def get_altered_ssn_and_dob(
        self,
        *individual_crd_numbers: int,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        Altered identifiers of registered individuals (only available in the
        QA Test Environment).
        
        The dataset is **only available in QA Test environment** and not in
        production.
        
        One or more ``individual_crd_numbers`` are required as positional
        arguments when querying the :py:attr:`Endpoint.DATA` resource endpoint,
        but no more than 25 per call.
        
        This dataset only supports synchronous requests.
        
        No mock API available.
        
        Requires Firm API credentials.
        
        :param individual_crd_numbers: Individual CRD Numbers as positional
            arguments
        """
        if not self._test_environment:
            raise QATestEnvException()
        if self._mock:
            raise MockException()
        
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if not individual_crd_numbers:
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Altered SSN and DOB requires one or more "
                    "individual_crd_numbers."
                    )
            
            if len(individual_crd_numbers) > 25:
                raise ValueError(
                    "Too many Individual CRD Numbers for request. "
                    "Supports up to 25 per call."
                    )
            
            filters = {"metaData": {
                "individualCrdNumbers": list(individual_crd_numbers),
                }}
        else:
            filters = None
        
        return self._query(
            self._base_url, "registration", "alteredSSNandDOB", None, None,
            [], endpoint, None, filters, None, None, 0,
            None, True, None, None, version
            )
    
    _add_params_docs(get_altered_ssn_and_dob, "endpoint", "version")
    
    # This dataset only supports GET requests to DATA endpoint
    def get_branch_delta(
        self,
        start_datetime: Optional[date | datetime]=None,
        end_datetime: Optional[date | datetime]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        Identify the requesting firm's branches where information has changed
        within a given datetime range.
        
        The dataset returns active branches or those closed in the last 30
        days.
        
        The ``start_datetime`` cannot be more than 30 days prior to today's
        date in the Eastern timezone.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        
        :param start_datetime: Datetime of the start of the query window.
            Default: 30 days prior to today.
        :param end_datetime: Datetime of the end of the query window
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if start_datetime is None: # default 30 days ago, midnight in TZ
                start_datetime = datetime_naive(
                    datetime.now(_TZ).date() - timedelta(days=30), _TZ
                    )
            else:
                if not isinstance(start_datetime, date):
                    _type_error(
                        "start_datetime", start_datetime, (date, datetime)
                        )
                start_datetime = datetime_naive(start_datetime, _TZ)
                now = datetime.now(_TZ).replace(tzinfo=None)
                if (now - start_datetime).days > 30:
                    raise ValueError(
                        "start_datetime cannot be more than 30 days prior "
                        "to today's date in the Eastern timezone"
                        )
            
            params = {"startDateTime": datetime_isoformat_ms(
                start_datetime, suffix="Z"
                )}
            if end_datetime is not None:
                if not isinstance(end_datetime, date):
                    _type_error("end_datetime", end_datetime, (date, datetime))
                end_datetime = datetime_naive(end_datetime, _TZ)
                params["endDateTime"] = datetime_isoformat_ms(
                    end_datetime, suffix="Z"
                    )
        else:
            params = {}
        
        return self._get_query(
            self._base_url, "registration", "branchDelta", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(get_branch_delta, "endpoint", "version")
    
    # This dataset only supports GET requests to DATA endpoint
    def get_branch_list(
        self,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        List active branches for the requesting firm.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        """
        return self._get_query(
            self._base_url, "registration", "branchList", None,
            endpoint, None, version
            )
    
    _add_params_docs(get_branch_list, "endpoint", "version")
    
    def get_broker_dealer_firm_list(
        self,
        firm_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        version: Optional[int]=None
        ):
        """
        Provides comprehensive information about all broker-dealer firms
        registered with and regulated by FINRA.
        
        The dataset mirrors what is publicly available through FINRA's
        `BrokerCheck <www.finra.org/brokercheck>`__ service. However, it
        returns only firms actively registered with FINRA, as well as firms for
        which a termination request has been received. It will not return
        terminated firms. Each firm record provides rich details including:
        
         - Registration Information: CRD number, SEC number, legal status, and
           registration status dates.
         - Business Details: Legal name, DBA name, types of business
           activities, and contact addresses.
         - Geographic Coverage: States where the firm is registered to conduct
           business.
         - Ownership Structure: Information on owners, officers, and control
           persons with ownership percentages.
         - Form BD Data: Key regulatory form responses and disclosures.
        
        Returned data follows the `Broker Dealer Firm List schema
        <https://static.rampweb.finra.org
        /schemas/brokerdealerfirmlist.json>`__.
        
        To retrieve data about a specific firm pass the firm's
        ``firm_crd_number`` as an argument when querying the
        :py:attr:`Endpoint.DATA` resource endpoint. Otherwise, all firms are
        returned with pagination attributes included in the response headers.
        
        Helper functions for extracting values from response headers are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_record_limit() <finra.utils.extract_record_limit>`,
        :py:func:`extract_record_offset() <finra.utils.extract_record_offset>`,
        and
        :py:func:`extract_record_total() <finra.utils.extract_record_total>`.
        
        This dataset does not have a :py:attr:`Endpoint.METADATA` endpoint.
        
        This dataset only supports synchronous requests.
        
        This dataset has unique record limits. See parameters below.
        
        Requires Firm or Organization API credentials.
        """
        if firm_crd_number is None:
            params = {}
        else:
            params = {"firmCrdNumber": firm_crd_number}
        
        return self._query(
            self._base_url, "registration", "brokerDealerFirmList", None, None,
            [], endpoint, None, None, None, limit, offset,
            None, True, None, None, version, **params
            )
    
    _add_params_docs(
        get_broker_dealer_firm_list,
        "firm_crd_number",
        "endpoint", "limit", "offset", "version",
        limit_default=100, limit_sync_max=500, limit_async_max=None
        )
    
    CompositeBranchSections = _enums.CompositeBranchSections
    
    # This dataset only supports GET requests to DATA endpoint
    def get_composite_branch(
        self,
        branch_crd_number: Optional[int]=None,
        *,
        sections: Optional[FieldsType[_enums.CompositeBranchSections]]=None,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        Comprehensive real-time data that FINRA has for a given Branch CRD
        Number.
        
        The ``branch_crd_number`` is required when querying the
        :py:attr:`Endpoint.DATA` resource endpoint.
        
        Returned data follows the `Composite Branch schema
        <https://static.rampweb.finra.org/schemas/branchcomposite.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        
        :param branch_crd_number: A Branch's CRD Number
        :param sections: Filter query results for one or more sections from
            :py:class:`CompositeBranchSections`
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if branch_crd_number is None:
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Composite Branch requires the first argument to be the "
                    "branch_crd_number."
                    )
            
            params: dict[str, Any] = {"branchCrdNumber": branch_crd_number}
            if sections:
                params["sections"] = ",".join(self._convert_iterable(
                    sections, self.CompositeBranchSections
                    ))
        else:
            params = {}
        
        return self._get_query(
            self._base_url, "registration", "compositeBranch", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(get_composite_branch, "endpoint", "version")
    
    CompositeIndividualSections = _enums.CompositeIndividualSections
    
    # This dataset only supports GET requests to DATA endpoint
    def get_composite_individual(
        self,
        individual_crd_number: Optional[int]=None,
        *,
        sections: Optional[FieldsType[
            _enums.CompositeIndividualSections
            ]]=None,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        Comprehensive real-time data that FINRA has for a given Individual CRD
        Number.
        
        The ``individual_crd_number`` is required when querying the
        :py:attr:`Endpoint.DATA` resource endpoint.
        
        Returned data follows the `Composite Individual schema
        <https://static.rampweb.finra.org/schemas/individualcomposite.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        
        :param individual_crd_number: Individual's CRD Number
        :param sections: Filter query results for one or more sections from
            :py:class:`CompositeIndividualSections`
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if individual_crd_number is None:
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Composite Individual requires the first argument to be "
                    "the individual_crd_number."
                    )
            
            params: dict[str, Any] = {
                "individualCrdNumber": individual_crd_number
                }
            if sections:
                params["sections"] = ",".join(self._convert_iterable(
                    sections, self.CompositeIndividualSections
                    ))
        else:
            params = {}
        
        return self._get_query(
            self._base_url, "registration", "compositeIndividual", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(get_composite_individual, "endpoint", "version")
    
    def get_composite_individual_seed(
        self,
        request_id: Optional[str]=None,
        *,
        sections: Optional[FieldsType[
            _enums.CompositeIndividualSections
            ]]=None,
        version: Optional[int]=None
        ):
        """
        JSON file download of all the individuals currently employed by the
        requesting firm, and individuals terminated within the last 30 calendar
        days.
        
        If a file is requested by ``12:00 AM Eastern`` on a given day, it is
        made available the following day via a **pre-signed** URL after
        ``7:00 AM Eastern`` on weekdays and ``9:00 AM Eastern`` on weekends.
        Once the file is generated, it will be available for 30 days. Users can
        request the file download up to 3 times a month in production and up to
        30 times a month in the QA Test environment. This limit is applied at
        the firm level.
        
        Returned data follows the `Composite Individual schema
        <https://static.rampweb.finra.org/schemas/individualcomposite.json>`__,
        the same as :py:meth:`BaseClient.get_composite_individual`, but wrapped
        with additional metadata.
        
        This dataset only supports asynchronous requests. The first response
        returns a ``request_id`` in the response body, which must be passed
        back to this method as an argument in order to check the result status.
        If the result is not ready, the response will return with a status of
        ``pending`` or ``unavailable``, and will also include the check status
        link. If the response returns with ``failed`` status, it will also
        include error messages.
        
        When the request returns with status ``complete``, the result is ready.
        The response will also contain the **pre-signed** result URL, which can
        be passed to the :py:meth:`BaseClient.get_async_result` method to fetch
        the result. The **pre-signed** URL is valid for only 30 minutes after
        the call is made, after which the URL will no longer be valid and a new
        call to this method must be made with the same ``request_id``.
        
        Helper functions for extracting metadata from response objects are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_request_id() <finra.utils.extract_request_id>`,
        :py:func:`extract_status() <finra.utils.extract_status>`,
        :py:func:`extract_check_status_link()
        <finra.utils.extract_check_status_link>`,
        :py:func:`extract_result_link() <finra.utils.extract_result_link>`,
        :py:func:`extract_expires() <finra.utils.extract_expires>`, and
        :py:func:`extract_error_messages()
        <finra.utils.extract_error_messages>`.
        
        See the `API documentation <https://developer.finra.org/
        docs#query_api-registration-composite_individual_seed>`__ for more
        information about this dataset, including URLs that you may need to
        whitelist in order to retrieve the results.
        
        No mock API available.
        
        Requires Firm API credentials.
        
        :param request_id: UUID used when processing the asynchronous request.
            This is required when checking the status of the request.
        :param sections: Filter query results for one or more sections from
            :py:class:`CompositeIndividualSections`
        """
        if self._mock:
            raise MockException()
        
        if request_id is None:
            if sections:
                filters = {"sections": self._convert_iterable(
                    sections, self.CompositeIndividualSections
                    )}
            else:
                filters = {} # invoke POST
        elif sections:
            raise ValueError(
                "Sections are not supported when checking status link"
                )
        
        else: # request_id from check status link
            filters = None # invoke GET
        
        if version is None: # changes path, not headers
            base_url = f"{self._base_url}/v1"
        else:
            base_url = f"{self._base_url}/v{version}"
        
        return self._query(
            base_url, "registration", "compositeIndividualSeed", request_id,
            None,
            [], None, None, filters, None, None, 0,
            None, True, None, None, None
            )
    
    _add_params_docs(get_composite_individual_seed, "version")
    
    # This dataset only supports GET requests to DATA endpoint
    def get_individual_delta(
        self,
        start_datetime: Optional[date | datetime]=None,
        end_datetime: Optional[date | datetime]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        limit: Optional[int]=None,
        offset: int=0,
        version: Optional[int]=2
        ):
        """
        Identify individual representatives whose information has changed
        within a given datetime range.
        
        The dataset returns individuals terminated in the last 30 days.
        
        The ``start_datetime`` cannot be more than 31 days prior to today's
        date in the Eastern timezone.
        
        Returned data follows the `Individual Delta schema
        <https://static.rampweb.finra.org/schemas/individualdelta.json>`__.
        
        Pagination keywords ``limit`` and ``offset`` are available starting
        with Version 2.
        
        Defaults to API Version 2.
        
        Version 1: Deprecated with Retirement Date: March 31, 2027
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        
        :param start_datetime: Datetime of the start of the query window. If
            querying the :py:attr:`Endpoint.DATA` resource endpoint, the
            default is 31 days prior to today.
        :param end_datetime: Datetime of the end of the query window
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            
            if ((version is None or int(version) < 2)
                and (limit is not None or offset > 0)):
                raise ValueError(
                    "Pagination keywords 'limit' and 'offset' are not "
                    "supported for API Version 1"
                    )
            
            if start_datetime is None: # default 31 days ago
                start_datetime = datetime_naive(
                    datetime.now(_TZ).date() - timedelta(days=31), _TZ
                    )
            else:
                if not isinstance(start_datetime, date):
                    _type_error(
                        "start_datetime", start_datetime, (date, datetime)
                        )
                start_datetime = datetime_naive(start_datetime, _TZ)
                now = datetime.now(_TZ).replace(tzinfo=None)
                if (now - start_datetime).days > 31:
                    raise ValueError(
                        "start_datetime cannot be more than 31 days prior "
                        "to today's date in the Eastern timezone"
                        )
            
            params = {"startDateTime": datetime_isoformat_ms(
                start_datetime, suffix="Z"
                )}
            if end_datetime is not None:
                if not isinstance(end_datetime, date):
                    _type_error("end_datetime", end_datetime, (date, datetime))
                end_datetime = datetime_naive(end_datetime, _TZ)
                params["endDateTime"] = datetime_isoformat_ms(
                    end_datetime, suffix="Z"
                    )
        else:
            params = {}
        
        return self._query(
            self._base_url, "registration", "individualDelta", None, None,
            [], endpoint, None, None, None, limit, offset,
            None, True, None, None, version, **params
            )
    
    _add_params_docs(
        get_individual_delta,
        "endpoint", "limit", "offset", "version"
        )
    
    # This method only supports GET requests to DATA endpoint
    def get_individual_fingerprint(
        self,
        individual_crd_number: Optional[int]=None,
        date_of_birth: Optional[date]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        Comprehensive real-time fingerprint data that FINRA has for a given
        Individual CRD Number.
        
        The ``individual_crd_number`` and ``date_of_birth`` are required when
        querying the :py:attr:`Endpoint.DATA` resource endpoint.
        
        Returned data follows the `Individual Fingerprint schema
        <https://fingerprints.finra.org/
        schema/data/group/registration/name/fingerprint>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Fingerprint or QA Test Environment API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if individual_crd_number is None or date_of_birth is None:
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Individual Fingerprint requires two arguments: "
                    "individual_crd_number and date_of_birth."
                    )
            
            if (not isinstance(date_of_birth, date)
                or isinstance(date_of_birth, datetime)):
                _type_error("date_of_birth", date_of_birth, (date,))
            params = {
                "individualCrdNumber": individual_crd_number,
                "DOB": date_of_birth.isoformat(),
                }
        else:
            params = {}
        
        if self._test_environment: # Fingerprints in the QA Test Environment
            base_url = "https://fingerprints-qaint.finrafp.qa.finra.org"
        else:
            base_url = "https://fingerprints.finra.org"
        
        return self._get_query(
            base_url, "registration", "fingerprint", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(
        get_individual_fingerprint,
        "individual_crd_number", "date_of_birth",
        "endpoint", "version"
        )
    
    IndividualPreRegistrationSearch = \
        _enums.IndividualPreRegistrationSearch
    
    # This method only supports POST requests to DATA endpoint
    def get_individual_pre_registration_search(
        self,
        date_of_birth: Optional[date]=None,
        *,
        ssn: Optional[str]=None,
        last_name: Optional[str]=None,
        first_name: Optional[str]=None,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.IndividualPreRegistrationSearch
            ]]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.IndividualPreRegistrationSearch
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Registration records of industry individuals being considered for
        employment.
        
        The Pre-registration Individual dataset enables firms to automate the
        due diligence portion of their hiring processes by providing them with
        information about their candidates.
        
        The :py:attr:`Endpoint.DATA` resource endpoint can only be queried by
        providing ``date_of_birth`` (with an accurate month and day), and at
        least one of the following: ``ssn`` (required if individual has a
        Social Security Number), ``last_name``, or ``first_name``. If more than
        two fields are provided, they are used in the order listed above.
        
        No partition field.
        
        Requires Firm API credentials.
        
        .. note::
            - SSN must be provided if the registered individual has an SSN.
            - DOB does not include the year; it is ignored by the client.
            - According to FINRA: *"The purpose of this dataset is to support
              the pre-registration process for firms. It is not to be used for
              downloading bulk data or for other pre-hire purposes. Each
              request is logged and audited by the API Platform. FINRA reserves
              the right to throttle or disable any API connection that appears
              to be making excessive requests that do not fit normal usage
              patterns for pre-registration searches."*
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if (date_of_birth is None
                or (ssn is None and last_name is None and first_name is None)):
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Individual Pre-Registration Search requires the "
                    "date_of_birth is provided (with an accurate month and "
                    "day), and at least one of the following: (1) ssn "
                    "(required if individual has a Social Security Number), "
                    "(2) last_name, or (3) first_name."
                    )
            
            if (not isinstance(date_of_birth, date)
                or isinstance(date_of_birth, datetime)):
                _type_error("date_of_birth", date_of_birth, (date,))
            else:
                filters = {"compareFilters": [{
                    "fieldName": "dateOfBirth",
                    "fieldValue": datetime.combine(
                        date_of_birth, datetime.min.time()
                        ).strftime("%m-%d"),
                    "compareType": "EQUAL",
                    }]}
                if ssn is not None:
                    filters["compareFilters"].append({
                        "fieldName": "ssn",
                        "fieldValue": ssn,
                        "compareType": "EQUAL",
                        })
                if last_name is not None:
                    filters["compareFilters"].append({
                        "fieldName": "lastName",
                        "fieldValue": last_name,
                        "compareType": "EQUAL",
                        })
                if first_name is not None:
                    filters["compareFilters"].append({
                        "fieldName": "firstName",
                        "fieldValue": first_name,
                        "compareType": "EQUAL",
                        })                
        else:
            filters = None
        
        return self._query(
            self._base_url, "registration", "preRegistrationIndividual", None,
            self.IndividualPreRegistrationSearch,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_individual_pre_registration_search,
        "date_of_birth", "ssn", "last_name", "first_name",
        "endpoint", "fields", "sort_fields", "limit", "offset",
        "async_request", "version", enum=IndividualPreRegistrationSearch
        )
    
    # This method only supports POST requests to DATA endpoint
    def get_individual_pre_registration_search_v2(
        self,
        date_of_birth: Optional[date]=None,
        *,
        ssn: Optional[str]=None,
        individual_crd_number: Optional[int]=None,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        Registration records of individuals in the industry being considered
        for employment, along with complete disclosure information.
        
        Deprecated with Retirement Date: February 26, 2027
        
        Replaced by: :py:meth:`BaseClient.get_u4_form_prefill`
        
        The :py:attr:`Endpoint.DATA` resource endpoint can only be queried by
        providing ``date_of_birth`` (with an accurate month and day), and at
        least one of the following: ``ssn`` (required if individual has a
        Social Security Number), or ``individual_crd_number``. If all three
        fields are provided, they are used in the order listed above.
        
        The returned data follows the `Form U4 schema
        <https://ramp-schemas.datacollection.finra.org/
        forms/u4/models/0.0.1/u4.json>`__. This dataset also supports
        :py:attr:`Endpoint.METADATA`. However, it contains an unwieldy 892
        fields, and the query method does not support requesting a subset of
        those fields or sorting. Therefore, as a design choice, an enum has not
        been included for this dataset.
        
        This dataset only supports asynchronous requests. See
        :ref:`async_requests` for information on how to retrieve the results.
        See the `API documentation <https://developer.finra.org/
        docs#query_api-registration-individual_pre_registration_search_v2>`__
        for more information about this dataset, including URLs that you may
        need to whitelist in order to retrieve the results.
        
        Requires Firm API credentials.
        
        .. note::
            - SSN must be provided if the registered individual has an SSN.
            - DOB does not include the year; it is ignored by the client.
            - According to FINRA: *"The purpose of this dataset is to support
              the pre-registration process for firms. It is not to be used for
              downloading bulk data or for other pre-hire purposes. Each
              request is logged and audited by the API Platform. FINRA reserves
              the right to throttle or disable any API connection that appears
              to be making excessive requests that do not fit normal usage
              patterns for pre-registration searches."*
        """
        filters: Optional[FiltersDictType]
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if (date_of_birth is None
                or (ssn is None and individual_crd_number is None)):
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Individual Pre-Registration Search V2 requires the "
                    "date_of_birth is provided (with an accurate month and "
                    "day), and at least one of the following: (1) ssn "
                    "(required if individual has a Social Security Number), "
                    "or (2) individual_crd_number."
                    )
            
            if (not isinstance(date_of_birth, date)
                or isinstance(date_of_birth, datetime)):
                _type_error("date_of_birth", date_of_birth, (date,))
            else:
                filters = {"compareFilters": [{
                    "fieldName": "dateOfBirth",
                    "fieldValue": datetime.combine(
                        date_of_birth, datetime.min.time()
                        ).strftime("%m-%d"),
                    "compareType": "EQUAL",
                    }]}
                if ssn is not None:
                    filters["compareFilters"].append({
                        "fieldName": "ssn",
                        "fieldValue": ssn,
                        "compareType": "EQUAL",
                        })
                if individual_crd_number is not None:
                    filters["compareFilters"].append({
                        "fieldName": "individualCrdNumber",
                        "fieldValue": individual_crd_number,
                        "compareType": "EQUAL",
                        })
        else:
            filters = None
        
        return self._query(
            self._base_url, "registration", "preRegistrationIndividualv2",
            None, None,
            [], endpoint, None, filters, None, None, 0,
            True, True, None, None, version
            )
    
    _add_params_docs(
        get_individual_pre_registration_search_v2,
        "date_of_birth", "ssn", "individual_crd_number",
        "endpoint", "version"
        )
    
    IndividualRegistrationValidation = \
        _enums.IndividualRegistrationValidation
    
    # This method only supports GET requests to DATA endpoint
    def get_individual_registration_validation(
        self,
        individual_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.IndividualRegistrationValidation
            ]]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.IndividualRegistrationValidation
            ]]=None,
        async_request: Optional[bool]=None,
        version: Optional[int]=None
        ):
        """
        Validate the registration status of a registered individual with FINRA
        and the States, independent of what firm they are affiliated with.
        
        The Registration Validation dataset supports industry wide validation
        of the registration status of all registered reps by firms and other
        organizations.
        
        The ``individual_crd_number`` is required when querying the
        :py:attr:`Endpoint.DATA` resource endpoint.
        
        No partition field.
        
        Requires Firm, Organization or SRO API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if individual_crd_number is None:
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Individual Registration Validation requires the first "
                    "argument to be the individual_crd_number."
                    )
        
        return self._query(
            self._base_url, "registration", "registrationValidationIndividual",
            (None if individual_crd_number is None
             else f"id/{individual_crd_number}"),
            self.IndividualRegistrationValidation,
            [], endpoint, fields, None, sort_fields, None, 0,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_individual_registration_validation,
        "individual_crd_number",
        "endpoint", "fields", "async_request", "version",
        enum=IndividualRegistrationValidation
        )
    
    # This method only supports GET requests to DATA endpoint
    # API Version 2 does not have metadata or partitions
    def get_individual_registration_validation_details(
        self,
        individual_crd_number: Optional[int]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        async_request: Optional[bool]=None,
        version: Optional[int]=2
        ):
        """
        Validate the registration status **including disclosure details** of a
        registered individual with FINRA and the States, independent of what
        firm they are affiliated with.
        
        The ``individual_crd_number`` is required when querying the
        :py:attr:`Endpoint.DATA` resource endpoint.
        
        Returned data follows the individual registration validation details
        schemas:
        
         - `API Version 1 schema <https://schemas.api.finra.org/
           IndividualRegistrationValidationDetails.json>`__
         - `API Version 2 schema <https://schemas.api.finra.org/v2/
           IndividualRegistrationValidationDetails.json>`__
        
        Defaults to API Version 2.
        
        API Version 1: Deprecated with Retirement Date: July 31, 2026
        
        Requires SRO API credentials.
        """
        params = {}
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if individual_crd_number is None:
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Individual Registration Validation Details requires "
                    "the first argument to be the individual_crd_number."
                    )
            
            # New versions use a different URL structure
            if version is not None and int(version) > 1:
                params["individualCrdNumber"] = individual_crd_number
                individual_crd_number = None # not a single query request
        
        return self._get_query(
            self._base_url, "registration",
            "individualRegistrationValidationDetails",
            (None if individual_crd_number is None
             else f"id/{individual_crd_number}"),
            endpoint, async_request, version, **params
            )
    
    _add_params_docs(
        get_individual_registration_validation_details,
        "individual_crd_number",
        "endpoint", "async_request", "version"
        )
    
    RegisteredIndividualSearch = _enums.RegisteredIndividualSearch
    
    def get_registered_individual_search(
        self,
        date_of_birth: Optional[date]=None,
        *,
        ssn: Optional[str]=None,
        last_name: Optional[str]=None,
        first_name: Optional[str]=None,
        endpoint: Optional[_EndpointType]=None,
        fields: Optional[FieldsType[
            _enums.RegisteredIndividualSearch
            ]]=None,
        sort_fields: Optional[SortFieldsType[
            _enums.RegisteredIndividualSearch
            ]]=None,
        limit: Optional[int]=None,
        offset: int=0,
        async_request: Optional[bool]=None,
        version: Optional[int]=2
        ):
        """
        CRD numbers for registered individuals.
        
        The :py:attr:`Endpoint.DATA` resource endpoint can only be queried by
        providing the ``date_of_birth`` (with an accurate month and day), and
        at least one of the following: ``ssn`` (required if individual has a
        Social Security Number), ``last_name``, or ``first_name``. If more than
        two fields are provided, they are used in the order listed above.
        
        API Version 1 returns a list of Individual CRD Numbers. API Version 2
        returns data that follows the :py:class:`RegisteredIndividualSearch`
        metadata. Data returned from API Version 2 follows the `Registered
        Individual Search schema
        <https://schemas.api.finra.org/v2/RegisteredIndividualSearch.json>`__,
        which is equivalent to :py:class:`RegisteredIndividualSearch`.
        
        Defaults to API Version 2.
        
        API Version 1: Deprecated with Retirement Date: June 30, 2026
        
        Requires Firm, Organization or SRO API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if (date_of_birth is None
                or (ssn is None and last_name is None and first_name is None)):
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "Registered Individual Search requires the "
                    "date_of_birth is provided (with an accurate month and "
                    "day), and at least one of the following: (1) ssn "
                    "(required if individual has a Social Security Number), "
                    "(2) last_name, or (3) first_name."
                    )
            
            if (not isinstance(date_of_birth, date)
                or isinstance(date_of_birth, datetime)):
                _type_error("date_of_birth", date_of_birth, (date,))
            else:
                filters = {"compareFilters": [{
                    "fieldName": "dateOfBirth",
                    "fieldValue": datetime.combine(
                        date_of_birth, datetime.min.time()
                        ).strftime("%m-%d"),
                    "compareType": "EQUAL",
                    }]}
                if ssn is not None:
                    filters["compareFilters"].append({
                        "fieldName": "ssn",
                        "fieldValue": ssn,
                        "compareType": "EQUAL",
                        })
                if last_name is not None:
                    filters["compareFilters"].append({
                        "fieldName": "lastName",
                        "fieldValue": last_name,
                        "compareType": "EQUAL",
                        })
                if first_name is not None:
                    filters["compareFilters"].append({
                        "fieldName": "firstName",
                        "fieldValue": first_name,
                        "compareType": "EQUAL",
                        })
        else:
            filters = None
        
        return self._query(
            self._base_url, "registration", "registeredIndividualSearch", None,
            self.RegisteredIndividualSearch,
            [], endpoint, fields, filters, sort_fields, limit, offset,
            async_request, True, None, None, version
            )
    
    _add_params_docs(
        get_registered_individual_search,
        "date_of_birth", "ssn", "last_name", "first_name",
        "endpoint", "fields", "sort_fields",
        "limit", "offset", "async_request", "version",
        enum=RegisteredIndividualSearch
        )
    
    # This method only supports POST requests to DATA endpoint
    def get_u4_form_prefill(
        self,
        date_of_birth: Optional[date]=None,
        *,
        ssn: Optional[str]=None,
        individual_crd_number: Optional[int]=None,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        The U4 Form Prefill dataset is a data resource that can be used to
        pre-populate Form U4 initial fields when submitting registration
        applications through the Submission API. The response of the dataset is
        returned in the same format as a Form U4 initial submission.
        
        This dataset replaces
        :py:meth:`BaseClient.get_individual_pre_registration_search_v2`, and
        supports the same query parameters.
        
        The :py:attr:`Endpoint.DATA` resource endpoint can only be queried by
        providing ``date_of_birth`` (with an accurate month and day), and at
        least one of the following: ``ssn`` (required if individual has a
        Social Security Number), or ``individual_crd_number``. If all three
        fields are provided, they are used in the order listed above.
        
        Returned data follows the `Form U4 schema
        <https://ramp-schemas.datacollection.finra.org/
        forms/u4/models/0.0.1/u4.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        
        .. note::
            - SSN must be provided if the registered individual has an SSN.
            - DOB does not include the year; it is ignored by the client.
            - According to FINRA: *"The purpose of this dataset is to support
              the support U4 initial prefill process for firms. It is not to be
              used for downloading bulk data or for other pre-hire purposes.
              Each request is logged and audited by the API Platform. FINRA
              reserves the right to throttle or disable any API connection that
              appears to be making excessive requests that do not fit normal
              usage patterns for pre-registration searches."*
        """
        filters: Optional[FiltersDictType]
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or endpoint == "data"):
            if (date_of_birth is None
                or (ssn is None and individual_crd_number is None)):
                raise ValueError(
                    "When querying the DATA resource endpoint, "
                    "U4 Form Prefill requires the "
                    "date_of_birth is provided (with an accurate month and "
                    "day), and at least one of the following: (1) ssn "
                    "(required if individual has a Social Security Number), "
                    "or (2) individual_crd_number."
                    )
            
            if (not isinstance(date_of_birth, date)
                or isinstance(date_of_birth, datetime)):
                _type_error("date_of_birth", date_of_birth, (date,))
            else:
                filters = {"compareFilters": [{
                    "fieldName": "dateOfBirth",
                    "fieldValue": datetime.combine(
                        date_of_birth, datetime.min.time()
                        ).strftime("%m-%d"),
                    "compareType": "EQUAL",
                    }]}
                if ssn is not None:
                    filters["compareFilters"].append({
                        "fieldName": "ssn",
                        "fieldValue": ssn,
                        "compareType": "EQUAL",
                        })
                if individual_crd_number is not None:
                    filters["compareFilters"].append({
                        "fieldName": "individualCrdNumber",
                        "fieldValue": individual_crd_number,
                        "compareType": "EQUAL",
                        })
        else:
            filters = None
        
        return self._query(
            self._base_url, "registration", "u4FormPrefill", None, None,
            [], endpoint, None, filters, None, None, 0,
            None, True, None, None, version
            )
    
    _add_params_docs(
        get_u4_form_prefill,
        "date_of_birth", "ssn", "individual_crd_number",
        "endpoint", "version"
        )
    
    
    ##########################################################################
    # TRACE REPORT CARDS GROUP
    
    def get_trace_agency_debt_details(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        request_id: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Agency Debt Details
        dataset is a monthly status report for transactions in agency debt
        that a member firm reported to TRACE.
        
        This dataset accompanies :py:meth:`get_trace_agency_debt_summary`
        as a tool to help firms analyze and improve compliance-related
        activities associated with reporting transactions via TRACE.
        
        Returned data follows the `TRACE Agency Debt Details schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceAgencyDetail.json>`__.
        
        The dataset only supports asynchronous requests, and returns data in
        CSV format. Retrieving data from this endpoint is a three-step process:
        
         - Submit a file request: Initiate the asynchronous request and
           receive a ``request_id`` in the response body.
         - Poll for status: Pass the ``request_id`` back to this method as a
           keyword argument to check whether the file is ready. If the result
           is not ready, the response will return with a status of
           ``unavailable``, and will also include the check status link. Repeat
           this step until the response returns with a status of ``complete``.
         - Download the file: When the response returns with a value of
           ``complete``, the result is ready. The response will also contain a
           **pre-signed** result URL, which can be passed to the
           :py:meth:`BaseClient.get_async_result` method to download the CSV.
           The **pre-signed** download URL will expire after 30 minutes.
        
        Helper functions for extracting metadata from response objects are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_request_id() <finra.utils.extract_request_id>`,
        :py:func:`extract_request_timestamp()
        <finra.utils.extract_request_timestamp>`,
        :py:func:`extract_status() <finra.utils.extract_status>`,
        :py:func:`extract_check_status_link()
        <finra.utils.extract_check_status_link>`,
        :py:func:`extract_result_link() <finra.utils.extract_result_link>`,
        :py:func:`extract_expires() <finra.utils.extract_expires>`.
        
        See the `API documentation
        <https://developer.finra.org/docs#query_api-trace_report_cards-
        trace_quality_of_markets_report_card_for_agency_debt_detail>`__
        for more information about this dataset.
        
        Requires Firm API credentials.
        """
        if request_id is None:
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if not isinstance(period, date) or isinstance(period, datetime):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        if version is None: # changes path, not headers
            base_url = f"{self._base_url}/v1"
        else:
            base_url = f"{self._base_url}/v{version}"
        
        return self._get_query(
            base_url, "reportcard", "traceAgencyDetail", request_id,
            None, None, None, **params
            )
    
    _add_params_docs(
        get_trace_agency_debt_details,
        "period", "firm_market_id", "request_id", "version"
        )
    
    def get_trace_agency_debt_summary(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Agency Debt Summary
        dataset is a monthly status report for transactions in agency debt
        that a member firm reported to TRACE.
        
        Returned data follows the `TRACE Agency Debt Summary schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceAgencySummary.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or (not self.require_enums and endpoint == "data")):
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if (not isinstance(period, date)
                or isinstance(period, datetime)):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        return self._get_query(
            self.base_url, "reportcard", "traceAgencySummary", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(
        get_trace_agency_debt_summary,
        "period", "firm_market_id", "endpoint", "version"
        )
    
    def get_trace_treasuries_details(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        request_id: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Treasuries Details
        dataset is a monthly status report for transactions in treasuries
        that a member firm reported to TRACE.
        
        This dataset accompanies :py:meth:`get_trace_treasuries_summary`
        as a tool to help firms analyze and improve compliance-related
        activities associated with reporting transactions via TRACE.
        This report is posted no later than the 13th business day of the month.
        
        Returned data follows the `TRACE Treasuries Details schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceTreasuriesDetail.json>`__.
        
        The dataset only supports asynchronous requests, and returns data in
        CSV format. Retrieving data from this endpoint is a three-step process:
        
         - Submit a file request: Initiate the asynchronous request and
           receive a ``request_id`` in the response body.
         - Poll for status: Pass the ``request_id`` back to this method as a
           keyword argument to check whether the file is ready. If the result
           is not ready, the response will return with a status of
           ``unavailable``, and will also include the check status link. Repeat
           this step until the response returns with a status of ``complete``.
         - Download the file: When the response returns with a value of
           ``complete``, the result is ready. The response will also contain a
           **pre-signed** result URL, which can be passed to the
           :py:meth:`BaseClient.get_async_result` method to download the CSV.
           The **pre-signed** download URL will expire after 30 minutes.
        
        Helper functions for extracting metadata from response objects are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_request_id() <finra.utils.extract_request_id>`,
        :py:func:`extract_request_timestamp()
        <finra.utils.extract_request_timestamp>`,
        :py:func:`extract_status() <finra.utils.extract_status>`,
        :py:func:`extract_check_status_link()
        <finra.utils.extract_check_status_link>`,
        :py:func:`extract_result_link() <finra.utils.extract_result_link>`,
        :py:func:`extract_expires() <finra.utils.extract_expires>`.
        
        See the `API documentation
        <https://developer.finra.org/docs#query_api-trace_report_cards-
        trace_quality_of_markets_report_card_treasuries_detail>`__
        for more information about this dataset.
        
        Requires Firm API credentials.
        """
        if request_id is None:
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if not isinstance(period, date) or isinstance(period, datetime):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        if version is None: # changes path, not headers
            base_url = f"{self._base_url}/v1"
        else:
            base_url = f"{self._base_url}/v{version}"
        
        return self._get_query(
            base_url, "reportcard", "traceTreasuriesDetail", request_id,
            None, None, None, **params
            )
    
    _add_params_docs(
        get_trace_treasuries_details,
        "period", "firm_market_id", "request_id", "version"
        )
    
    def get_trace_treasuries_summary(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Treasuries Summary
        dataset is a monthly status report for transactions in treasuries
        that a member firm reported to TRACE. This report is posted no later
        than the 13th business day of the month. 
        
        Returned data follows the `TRACE Treasuries Summary schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceTreasuriesSummary.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or (not self.require_enums and endpoint == "data")):
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if (not isinstance(period, date)
                or isinstance(period, datetime)):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        return self._get_query(
            self.base_url, "reportcard", "traceTreasuriesSummary", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(
        get_trace_treasuries_summary,
        "period", "firm_market_id", "endpoint", "version"
        )
    
    def get_trace_corporate_bonds_details(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        request_id: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Corporate Bonds Details
        dataset is a monthly status report for transactions in corporate bonds
        that a member firm reported to TRACE.
        
        This dataset accompanies :py:meth:`get_trace_corporate_bonds_summary`
        as a tool to help firms analyze and improve compliance-related
        activities associated with reporting transactions via TRACE.
        
        Returned data follows the `TRACE Corporate Bonds Details schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceCorporateBondDetail.json>`__.
        
        The dataset only supports asynchronous requests, and returns data in
        CSV format. Retrieving data from this endpoint is a three-step process:
        
         - Submit a file request: Initiate the asynchronous request and
           receive a ``request_id`` in the response body.
         - Poll for status: Pass the ``request_id`` back to this method as a
           keyword argument to check whether the file is ready. If the result
           is not ready, the response will return with a status of
           ``unavailable``, and will also include the check status link. Repeat
           this step until the response returns with a status of ``complete``.
         - Download the file: When the response returns with a value of
           ``complete``, the result is ready. The response will also contain a
           **pre-signed** result URL, which can be passed to the
           :py:meth:`BaseClient.get_async_result` method to download the CSV.
           The **pre-signed** download URL will expire after 30 minutes.
        
        Helper functions for extracting metadata from response objects are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_request_id() <finra.utils.extract_request_id>`,
        :py:func:`extract_request_timestamp()
        <finra.utils.extract_request_timestamp>`,
        :py:func:`extract_status() <finra.utils.extract_status>`,
        :py:func:`extract_check_status_link()
        <finra.utils.extract_check_status_link>`,
        :py:func:`extract_result_link() <finra.utils.extract_result_link>`,
        :py:func:`extract_expires() <finra.utils.extract_expires>`.
        
        See the `API documentation
        <https://developer.finra.org/docs#query_api-trace_report_cards-
        trace_quality_of_markets_report_cards_for_corporate_bonds_detail>`__
        for more information about this dataset.
        
        Requires Firm API credentials.
        """
        if request_id is None:
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if not isinstance(period, date) or isinstance(period, datetime):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        if version is None: # changes path, not headers
            base_url = f"{self._base_url}/v1"
        else:
            base_url = f"{self._base_url}/v{version}"
        
        return self._get_query(
            base_url, "reportcard", "traceCorporateBondDetail", request_id,
            None, None, None, **params
            )
    
    _add_params_docs(
        get_trace_corporate_bonds_details,
        "period", "firm_market_id", "request_id", "version"
        )
    
    def get_trace_corporate_bonds_summary(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Corporate Bonds Summary
        dataset is a monthly status report for transactions in corporate bonds
        that a member firm reported to TRACE.
        
        Returned data follows the `TRACE Corporate Bonds Summary schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceCorporateBondSummary.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or (not self.require_enums and endpoint == "data")):
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if (not isinstance(period, date)
                or isinstance(period, datetime)):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        return self._get_query(
            self.base_url, "reportcard", "traceCorporateBondSummary", None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(
        get_trace_corporate_bonds_summary,
        "period", "firm_market_id", "endpoint", "version"
        )
    
    def get_trace_securitized_products_details(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        request_id: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Securitized Products
        Details dataset is a monthly status report for transactions in
        securitized products that a member firm reported to TRACE, including
        Asset Backed Securities, Mortgage Backed Securities and other similar
        securities.
        
        This dataset accompanies
        :py:meth:`get_trace_securitized_products_summary`
        as a tool to help firms analyze and improve compliance-related
        activities associated with reporting transactions via TRACE.
        
        Returned data follows the `TRACE Securitized Products Details schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceSecuritizedProductDetail.json>`__.
        
        The dataset only supports asynchronous requests, and returns data in
        CSV format. Retrieving data from this endpoint is a three-step process:
        
         - Submit a file request: Initiate the asynchronous request and
           receive a ``request_id`` in the response body.
         - Poll for status: Pass the ``request_id`` back to this method as a
           keyword argument to check whether the file is ready. If the result
           is not ready, the response will return with a status of
           ``unavailable``, and will also include the check status link. Repeat
           this step until the response returns with a status of ``complete``.
         - Download the file: When the response returns with a value of
           ``complete``, the result is ready. The response will also contain a
           **pre-signed** result URL, which can be passed to the
           :py:meth:`BaseClient.get_async_result` method to download the CSV.
           The **pre-signed** download URL will expire after 30 minutes.
        
        Helper functions for extracting metadata from response objects are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_request_id() <finra.utils.extract_request_id>`,
        :py:func:`extract_request_timestamp()
        <finra.utils.extract_request_timestamp>`,
        :py:func:`extract_status() <finra.utils.extract_status>`,
        :py:func:`extract_check_status_link()
        <finra.utils.extract_check_status_link>`,
        :py:func:`extract_result_link() <finra.utils.extract_result_link>`,
        :py:func:`extract_expires() <finra.utils.extract_expires>`.
        
        See the `API documentation
        <https://developer.finra.org/docs#query_api-trace_report_cards-
        trace_quality_of_markets_report_cards_for_securitized_products_detail>`__
        for more information about this dataset.
        
        Requires Firm API credentials.
        """
        if request_id is None:
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if not isinstance(period, date) or isinstance(period, datetime):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        if version is None: # changes path, not headers
            base_url = f"{self._base_url}/v1"
        else:
            base_url = f"{self._base_url}/v{version}"
        
        return self._get_query(
            base_url, "reportcard", "traceSecuritizedProductDetail",
            request_id,
            None, None, None, **params
            )
    
    _add_params_docs(
        get_trace_securitized_products_details,
        "period", "firm_market_id", "request_id", "version"
        )
    
    def get_trace_securitized_products_summary(
        self,
        period: Optional[date]=None,
        firm_market_id: Optional[str]=None,
        *,
        endpoint: Optional[_EndpointType]=None,
        version: Optional[int]=None
        ):
        """
        The TRACE Quality of Markets Report Cards for Securitized Products
        Summary dataset is a monthly status report for transactions in
        securitized products that a member firm reported to TRACE, including
        Asset Backed Securities, Mortgage Backed Securities and other similar
        securities.
        
        Returned data follows the `TRACE Securitized Products Summary schema
        <https://schemas.api.finra.org/v1/
        reportCard/traceSecuritizedProductSummary.json>`__.
        
        This dataset only supports synchronous requests.
        
        Requires Firm API credentials.
        """
        if (endpoint is None
            or endpoint == self.Endpoint.DATA
            or (not self.require_enums and endpoint == "data")):
            if period is None or firm_market_id is None:
                raise ValueError(
                    "When submitting a file request (request_id is None), "
                    "TRACE Report Card methods require two arguments: "
                    "period and firm_market_id."
                    )
            
            if (not isinstance(period, date)
                or isinstance(period, datetime)):
                _type_error("period", period, (date,))
            
            params = {
                "period": period.isoformat(),
                "firmMarketIdentifier": firm_market_id,
                }
        else:
            params = {}
        
        return self._get_query(
            self.base_url, "reportcard", "traceSecuritizedProductSummary",
            None,
            endpoint, None, version, **params
            )
    
    _add_params_docs(
        get_trace_securitized_products_summary,
        "period", "firm_market_id", "endpoint", "version"
        )
    
    
    ##########################################################################
    # NOTIFICATION API
    
    def _get_notifications(
        self,
        group: str,
        event_type: str,
        start_datetime: Optional[date | datetime],
        end_datetime: Optional[date | datetime],
        limit: Optional[int],
        offset: int,
        version: Optional[int]
        ):
        if self._mock and not self._test_environment:
            raise MockException()
        
        params: dict[str, Any] = {}
        if start_datetime is not None:
            if not isinstance(start_datetime, date):
                _type_error("start_datetime", start_datetime, (date, datetime))
            params["startDateTime"] = datetime_isoformat_ms(
                datetime_naive(start_datetime, _TZ)
                ) # no Z
        if end_datetime is not None:
            if not isinstance(end_datetime, date):
                _type_error("end_datetime", end_datetime, (date, datetime))
            params["endDateTime"] = datetime_isoformat_ms(
                datetime_naive(end_datetime, _TZ)
                ) # no Z
        if limit is not None:
            params["limit"] = limit
        if offset > 0:
            params["offset"] = offset
        return self._get_request(
            (self._base_url
             + f"/notifications/group/{group}/event-type/{event_type}"),
            params, self._prepare_headers(True, version)
            )
    
    # FINRA GROUP
    def get_finra_rulebook_notifications(
        self,
        start_datetime: Optional[date | datetime]=None,
        end_datetime: Optional[date | datetime]=None,
        *,
        limit: Optional[int]=None,
        offset: int=0,
        version: Optional[int]=None
        ):
        """
        Provides notifications related to changes in the FINRA Rulebook.
        
        Only notifications from last 12 months are returned. If the datetime
        range is outside this window, no results are returned.
        
         - If only the ``start_datetime`` is provided, notifications published
           at or after ``start_datetime`` are returned.
         - If only the ``end_datetime`` is provided, notifications published
           within last 12 months up to the ``end_datetime`` are returned.
         - If neither datetimes are provided, only notifications published
           within the last month are returned.
        
        Requires Firm or Organization API credentials.
        
        :param start_datetime: Datetime of the start of the query window
        :param end_datetime: Datetime of the end of the query window
        """
        return self._get_notifications(
            "finra", "finrarulebook",
            start_datetime, end_datetime, limit, offset, version
            )
    
    _add_params_docs(
        get_finra_rulebook_notifications,
        "limit", "offset", "version"
        )
    
    # OPERATION GROUP
    def get_draft_registration_filing_notifications(
        self,
        start_datetime: Optional[date | datetime]=None,
        end_datetime: Optional[date | datetime]=None,
        *,
        limit: Optional[int]=None,
        offset: int=0,
        version: Optional[int]=None
        ):
        """
        Provides notifications related to draft registration filings.
        
        Only notifications from last 12 months are returned. If the datetime
        range is outside this window, no results are returned.
        
         - If only the ``start_datetime`` is provided, notifications published
           at or after ``start_datetime`` are returned.
         - If only the ``end_datetime`` is provided, notifications published
           within last 12 months up to the ``end_datetime`` are returned.
         - If neither datetimes are provided, only notifications published
           within the last month are returned.
        
        Requires Firm API credentials.
        
        :param start_datetime: Datetime of the start of the query window
        :param end_datetime: Datetime of the end of the query window
        """
        return self._get_notifications(
            "operation", "draftRegistrationFiling",
            start_datetime, end_datetime, limit, offset, version
            )
    
    _add_params_docs(
        get_draft_registration_filing_notifications,
        "limit", "offset", "version"
        )
    
    
    ##########################################################################
    # SUBMISSION API
    
    def _submission(
        self,
        group: str,
        name: str,
        request_id: Optional[str],
        filing: Optional[BaseFiling | FilingDictType],
        put: bool,
        delete: bool,
        validate: bool,
        schema_url: Optional[str],
        version: Optional[int]
        ):
        if self._mock and not self._test_environment:
            raise MockException()
        
        if version is None: # changes path, not headers
            version = 1
        
        url = (
            f"{self._base_url}/v{version}/submissions/filings/{group}/{name}"
            )
        
        headers = self._prepare_headers(True, None)
        
        if filing is None:
            if request_id is None:
                raise ValueError(
                    "Must provide either: (1) the request_id to GET or "
                    "DELETE a filing, (2) the filing (object or data) to "
                    "POST filing data, or if supported (3) both the "
                    "request_id and the filing (object or data) to update a "
                    "filing. If put=True, the filing data will be replaced "
                    "by the update data via a PUT, otherwise merge the "
                    "filing data with the update data via a PATCH. "
                    "Default behavior is put=False."
                    )
            if delete: # DELETE
                return self._delete_request(
                    url + f"/{request_id}", None, headers
                    )
            # GET
            return self._get_request(url + f"/{request_id}", None, headers)
        
        if delete:
            raise ValueError(
                "Filing must be None to delete. Just pass the request_id."
                )
        
        data = filing.build() if isinstance(filing, BaseFiling) else filing
        if validate:
            if isinstance(self._session, httpx.AsyncClient): # asynchronous
                raise TypeError(
                    "Client-side filing validation is not currently "
                    "supported for AsyncClient. Either set validate=False "
                    "when doing submission requests using the AsyncClient "
                    "class, or use the synchronous Client class to do "
                    "client-side validation during submission requests."
                    )
            if isinstance(filing, BaseFiling):
                if schema_url is None:
                    schema_url = filing.schema_url
            if not schema_url:
                raise ValueError(
                    "A non-empty schema_url must be provided if filing "
                    "object does not subclass BaseFiling."
                    )
            Validator(self, schema_url).validate(data)
        
        if request_id is None: # POST
            
            # Data must be included for post
            # Filings that don't have ops support also don't support put/patch,
            # but check for missing data during build method (above)
            if (isinstance(filing, BaseFilingOps)
                and filing._filingData is None
                and filing._operations is None):
                raise ValueError(
                    "Must set either Filing Data, or add at least one "
                    "Operation on existing data."
                    )
            return self._post_request(url, data, headers)
        
        if put: # PUT
            return self._put_request(url + f"/{request_id}", data, headers)
        
        # PATCH
        return self._patch_request(url + f"/{request_id}", data, headers)
    
    def create_individual_submission(
        self,
        request_id: Optional[str]=None,
        *,
        filing: Optional[CreateIndividual | FilingDictType]=None,
        validate: bool=False,
        schema_url: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        Submit the initial registration record of an individual to FINRA,
        which will include the generation of an Individual CRD Number.
        
        See :py:class:`CreateIndividual
        <finra.filings.create_individual.CreateIndividual>` for
        more information about how to create an individual registration record.
        
        The Create Individual submission is a synchronous request that returns
        a new Individual CRD Number in the response. Passing the ``request_id``
        returned by the submission back to this method as the first argument
        will return the same response. This submission type does not support
        draft filings or updates. If both a ``filing`` and ``request_id`` are
        provided, a ``ValueError`` will be raised.
        
        Filing data can be validated on the client-side prior to submission by
        setting ``validate=True``. Client-side validation is a best effort to
        match the constraints expected by the API using the provided schema, to
        catch errors before they are submitted. It is not intended as a
        replacement for the API's server-side validation.
        
        Helper functions for extracting metadata from submission responses are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_filing_request_id()
        <finra.utils.extract_filing_request_id>`,
        :py:func:`extract_filing_result_status()
        <finra.utils.extract_filing_result_status>`, and
        :py:func:`extract_filing_result_status_description()
        <finra.utils.extract_filing_result_status_description>`.
        
        Requires Firm API credentials.
        """
        if request_id is not None and filing is not None:
            raise ValueError(
                "CreateIndividual does not support updates. Filing data "
                "can only be submitted. Provide either the request_id "
                "returned by a submission to retrieve the data again, or "
                "provide the CreateIndividual filing object (or data) to "
                "submit."
                )
        return self._submission(
            "registration", "create-individual", request_id, filing,
            False, False, validate, schema_url, version
            )
    
    _add_filing_params_docs(
        create_individual_submission, "request_id", "filing",
        "validate", "schema_url", "version",
        filing_cls="finra.filings.create_individual.CreateIndividual",
        filing_name="Create Individual"
        )
    
    def form_br_submission(
        self,
        request_id: Optional[str]=None,
        *,
        filing: Optional[FormBR | FilingDictType]=None,
        put: bool=False,
        delete: bool=False,
        validate: bool=False,
        schema_url: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        Form BR establishes registration of a branch office with FINRA, the New
        York Stock Exchange (NYSE) and States that require branch registration.
        
        See :py:class:`FormBR <finra.filings.form_br.FormBR>` for more
        information about how to build a Form BR filing for submission.
        
        Form BR submission is an asynchronous request. The status of a
        submission can be checked via a subsequent request by passing the
        ``request_id`` returned by the submission back to this method as the
        first argument. Please allow 5-15 mins processing time for each
        submission before making a request for results.
        
        If only the ``filing`` is provided, the submission is considered a POST
        request. If both the ``request_id`` and a ``filing`` object are
        provided, the submission is considered an update. To update with a PUT
        request set ``put=True``, otherwise the update will be a PATCH request.
        
        Filing data can be validated on the client-side prior to submission by
        setting ``validate=True``. Client-side validation is a best effort to
        match the constraints expected by the API using the provided schema, to
        catch errors before they are submitted. It is not intended as a
        replacement for the API's server-side validation.
        
        Helper functions for extracting metadata from submission responses are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_filing_request_id()
        <finra.utils.extract_filing_request_id>`,
        :py:func:`extract_filing_result_status()
        <finra.utils.extract_filing_result_status>`, and
        :py:func:`extract_filing_result_status_description()
        <finra.utils.extract_filing_result_status_description>`.
        
        Requires Firm API credentials.
        """
        return self._submission(
            "registration", "br", request_id, filing,
            put, delete, validate, schema_url, version
            )
    
    _add_filing_params_docs(
        form_br_submission, "request_id", "filing",
        "put", "delete", "validate", "schema_url", "version",
        filing_cls="finra.filings.form_br.FormBR",
        filing_name="Form BR"
        )
    
    def form_u4_submission(
        self,
        request_id: Optional[str]=None,
        *,
        filing: Optional[FormU4 | FilingDictType]=None,
        put: bool=False,
        delete: bool=False,
        validate: bool=False,
        schema_url: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        Form U4 establishes registration of representatives of broker-dealers,
        investment advisers with appropriate jurisdictions and/or SROs.
        
        See :py:class:`FormU4 <finra.filings.form_u4.FormU4>` for more
        information about how to build a Form U4 filing for submission.
        
        Form U4 submission is an asynchronous request. The status of a
        submission can be checked via a subsequent request by passing the
        ``request_id`` returned by the submission back to this method as the
        first argument. Please allow 5-15 mins processing time for each
        submission before making a request for results.
        
        If only the ``filing`` is provided, the submission is considered a POST
        request. If both the ``request_id`` and a ``filing`` object are
        provided, the submission is considered an update. To update with a PUT
        request set ``put=True``, otherwise the update will be a PATCH request.
        
        Filing data can be validated on the client-side prior to submission by
        setting ``validate=True``. Client-side validation is a best effort to
        match the constraints expected by the API using the provided schema, to
        catch errors before they are submitted. It is not intended as a
        replacement for the API's server-side validation.
        
        Helper functions for extracting metadata from submission responses are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_filing_request_id()
        <finra.utils.extract_filing_request_id>`,
        :py:func:`extract_filing_result_status()
        <finra.utils.extract_filing_result_status>`, and
        :py:func:`extract_filing_result_status_description()
        <finra.utils.extract_filing_result_status_description>`.
        
        Requires Firm API credentials.
        """
        return self._submission(
            "registration", "u4", request_id, filing,
            put, delete, validate, schema_url, version
            )
    
    _add_filing_params_docs(
        form_u4_submission, "request_id", "filing",
        "put", "delete", "validate", "schema_url", "version",
        filing_cls="finra.filings.form_u4.FormU4",
        filing_name="Form U4"
        )
    
    def form_u5_submission(
        self,
        request_id: Optional[str]=None,
        *,
        filing: Optional[FormU5 | FilingDictType]=None,
        put: bool=False,
        delete: bool=False,
        validate: bool=False,
        schema_url: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        Form U5 is the Uniform Termination Notice for Securities Industry
        Registration.
        
        See :py:class:`FormU5 <finra.filings.form_u5.FormU5>` for more
        information about how to build a Form U5 filing for submission.
        
        Form U5 submission is an asynchronous request. The status of a
        submission can be checked via a subsequent request by passing the
        ``request_id`` returned by the submission back to this method as the
        first argument. Please allow 5-15 mins processing time for each
        submission before making a request for results.
        
        If only the ``filing`` is provided, the submission is considered a POST
        request. If both the ``request_id`` and a ``filing`` object are
        provided, the submission is considered an update. To update with a PUT
        request set ``put=True``, otherwise the update will be a PATCH request.
        
        Filing data can be validated on the client-side prior to submission by
        setting ``validate=True``. Client-side validation is a best effort to
        match the constraints expected by the API using their provided schema,
        to catch errors before they are submitted. It is not intended as a
        replacement for the API's server-side validation.
        
        Helper functions for extracting metadata from submission responses are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_filing_request_id()
        <finra.utils.extract_filing_request_id>`,
        :py:func:`extract_filing_result_status()
        <finra.utils.extract_filing_result_status>`, and
        :py:func:`extract_filing_result_status_description()
        <finra.utils.extract_filing_result_status_description>`.
        
        Requires Firm API credentials.
        """
        return self._submission(
            "registration", "u5", request_id, filing,
            put, delete, validate, schema_url, version
            )
    
    _add_filing_params_docs(
        form_u5_submission, "request_id", "filing",
        "put", "delete", "validate", "schema_url", "version",
        filing_cls="finra.filings.form_u5.FormU5",
        filing_name="Form U5"
        )
    
    def non_registered_fingerprint_submission(
        self,
        request_id: Optional[str]=None,
        *,
        filing: Optional[NonRegisteredFingerprint | FilingDictType]=None,
        validate: bool=False,
        schema_url: Optional[str]=None,
        version: Optional[int]=None
        ):
        """
        Submit a Non-Registered Fingerprint record to FINRA.
        
        See :py:class:`NonRegisteredFingerprint
        <finra.filings.non_registered_fingerprint.NonRegisteredFingerprint>`
        for more information about how to submit Non-Registered Fingerprint to
        FINRA.
        
        Non-Registered Fingerprint submission is an asynchronous request. The
        status of a submission can be checked via a subsequent request by
        passing the ``request_id`` returned by the submission back to this
        method as the first argument. Please allow 5-15 mins processing time
        for each submission before making a request for results.
        
        If a Non-Registered Fingerprint filing is submitted for a new
        individual without an Individual CRD Number, a new Individual CRD
        Number is automatically created, and will be returned in a subsequent
        request when providing the ``request_id``. Filing data must be set even
        for amendments, or it can have just the delta changes for an amendment.
        This submission type does not support draft filings, or updates via
        operations. If both a ``filing`` and ``request_id`` are provided, a
        ``ValueError`` will be raised.
        
        Filing data can be validated on the client-side prior to submission by
        setting ``validate=True``. Client-side validation is a best effort to
        match the constraints expected by the API using their provided schema,
        to catch errors before they are submitted. It is not intended as a
        replacement for the API's server-side validation.
        
        Helper functions for extracting metadata from submission responses are
        available in the :py:mod:`utils <finra.utils>` module.
        Specifically see:
        :py:func:`extract_filing_request_id()
        <finra.utils.extract_filing_request_id>`,
        :py:func:`extract_filing_result_status()
        <finra.utils.extract_filing_result_status>`, and
        :py:func:`extract_filing_result_status_description()
        <finra.utils.extract_filing_result_status_description>`.
        
        Requires Firm API credentials.
        """
        if request_id is not None and filing is not None:
            raise ValueError(
                "NonRegisteredFingerprint does not support updates. "
                "Filing data must be sent even for amendments. Filing data "
                "can also have just the delta changes for amendments. "
                "Provide either the request_id returned by a submission to "
                "retrieve the data, or provide the NonRegisteredFingerprint "
                "filing object (or data) to submit."
                )
        return self._submission(
            "registration", "nrf", request_id, filing,
            False, False, validate, schema_url, version
            )
    
    _add_filing_params_docs(
        non_registered_fingerprint_submission, "request_id", "filing",
        "validate", "schema_url", "version",
        filing_cls=("finra.filings.non_registered_fingerprint."
                    "NonRegisteredFingerprint"),
        filing_name="Non-Registered Fingerprint"
        )

