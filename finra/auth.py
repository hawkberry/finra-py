from __future__ import annotations

import inspect
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable, Optional, cast

from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client

from .async_client import AsyncClient
from .client import Client
from .log_redactor import register_redactions
from .token_manager import TokenManager, TokenType


__all__ = [
    "get_logger",
    "get_client",
    "client_from_token_file",
    "client_from_new_token",
    "client_from_storage_functions",
    "get_async_client",
    "async_client_from_new_token",
    "async_client_from_storage_functions",
    "build_async_client",
    "build_client",
    ]


##############################################################################
# CONFIG

#: FINRA Identify Platform production OAuth 2.0 authentication URL
_PROD_TOKEN_ENDPOINT = (
    "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token"
    )

#: FINRA Identify Platform QA Test Environment OAuth 2.0 authentication URL
_TEST_TOKEN_ENDPOINT = (
    "https://ews-qaint.fip.qa.finra.org/fip/rest/ews/oauth2/access_token"
    )


##############################################################################
# LOGGING

def get_logger() -> logging.Logger:
    """Logger for :mod:`auth` module"""
    return logging.getLogger(__name__)


##############################################################################
# DOCUMENTATION

def _add_auth_params_docs(func: Callable, *params: str) -> None:
    _params = []
    for p in params:
        if p == "api_key":
            _params.append("""
:param api_key: FINRA API Key
""")
        elif p == "api_secret":
            _params.append("""
:param api_secret: FINRA API Secret
""")
        elif p == "token_path":
            _params.append("""
:param token_path: The file system path to the token file
""")
        elif p == "token_read_func":
            _params.append("""
:param token_read_func: Callable that reads the token from the token path. This
    function takes no arguments.
""")
        elif p == "token_write_func":
            _params.append("""
:param token_write_func: Callable that writes the token to the token path. This
    function is called by the OAuth2 session to write a token. It must
    accept the token as the first positional argument, as well as any
    additional positional and keyword arguments passed by the OAuth2 session.
    Example: ``token_write_func(token, *args, **kwds)``.
""")
        elif p == "token_manager":
            _params.append("""
:param token_manager: Instance of
    :py:class:`TokenManager <finra.token_manager.TokenManager>`
""")
        elif p == "is_asyncio":
            _params.append("""
:param is_asyncio: Option to enable asyncio support. If using
    :py:class:`AsyncClient <finra.async_client.AsyncClient>`, this option must
    be set to ``True``.
""")
        elif p == "mock":
            _params.append("""
:param mock: Option to use Mock API datasets. This requires Mock API
    credentials.
""")
        elif p == "test_environment":
            _params.append("""
:param test_environment: Option to use the QA Test Environment. This requires
    QA Test Environment credentials.
""")
        elif p == "leeway":
            _params.append("""
:param leeway: Time allowed when checking if a token is expired, useful for
    ensuring that tokens are not prematurely considered invalid due to minor
    timing discrepancies
""")
        elif p == "automatic_refresh":
            _params.append("""
:param automatic_refresh: Option to enable automatic token refreshing by the
    OAuth2 session
""")
        elif p == "client_cls":
            _params.append("""
:param client_cls: Class (or constructor) that returns a synchronous client.
    Default: :py:class:`Client <finra.client.Client>`
""")
        elif p == "async_client_cls":
            _params.append("""
:param async_client_cls: Class (or constructor) that returns an asynchronous
    client. Default: :py:class:`AsyncClient <finra.async_client.AsyncClient>`
""")
        elif p == "min_expires_in":
            _params.append("""
:param min_expires_in: If the token is loaded from a file, but has less than
    this time remaining (in seconds), proactively fetch a new token and replace
    it. Assists in managing :ref:`token_expiration`. If set to ``None``, never
    proactively delete the token.
""")
        elif p == "kwds":
            _params.append("""
:param kwds: Additional keyword arguments passed to the client class (or
    constructor) on instantiation
""")
        else:
            _all = [
                "api_key", "api_secret", "token_path",
                "token_read_func", "token_write_func",
                "token_manager", "token_endpoint",
                "is_asyncio", "client_cls", "async_client_cls", "leeway",
                "mock", "test_environment", "min_expires_in", "kwds",
                ]
            unknown = ", ".join([f"'{p}'" for p in params if p not in _all])
            available = ", ".join([f"'{p}'" for p in _all])
            raise ValueError(
                f"Unknown parameters: {unknown}" + "\n"
                f"Available parameters: {available}"
                )
    
    func.__doc__ = (getattr(func, "__doc__") or "") + "".join(_params)


##############################################################################
# UTILS

# Constructor for default token read function
def __token_reader(
    token_path: str | Path
    ) -> Callable[[], TokenType]:
    
    def token_read_func() -> TokenType:
        get_logger().info("Reading token from file %s", token_path)
        with open(token_path, "r") as f:
            return json.load(f)
    
    return token_read_func


# Constructor for default token write function
def __token_writer(
    token_path: str | Path
    ) -> Callable[..., Any]:
    
    Path(token_path).parent.mkdir(parents=True, exist_ok=True)
    
    def token_write_func(
        token: TokenType,
        *args: Any,
        **kwds: Any
        ) -> None:
        with open(token_path, "w") as f:
            json.dump(token, f)
        get_logger().info("New token written to file %s", token_path)
    
    return token_write_func


##############################################################################
# BUILD CLIENT

def build_client(
    api_key: str,
    api_secret: str,
    token_manager: TokenManager,
    *,
    mock: bool=False,
    test_environment: bool=False,
    leeway: float=300.0,
    automatic_refresh: bool=False,
    client_cls: Optional[Callable[..., Client]]=None,
    **kwds
    ) -> Client:
    """
    Build a :py:class:`Client <finra.client.Client>` with an
    `OAuth2Client
    <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html>`__
    session and :py:class:`TokenManager <finra.token_manager.TokenManager>`
    """
    if test_environment:
        token_endpoint = _TEST_TOKEN_ENDPOINT
    else:
        token_endpoint = _PROD_TOKEN_ENDPOINT
    
    if automatic_refresh:
        metadata = {"grant_type": "client_credentials"}
    else:
        metadata = {}
    
    session = OAuth2Client(
        api_key,
        api_secret,
        token=token_manager.token,
        token_endpoint=token_endpoint,
        update_token=token_manager.update_token,
        leeway=leeway,
        **metadata
        )
    
    client = (client_cls or Client)(
        api_key,
        session,
        token_manager=token_manager,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )
    
    if client_cls is not None and not isinstance(client, Client):
        raise TypeError("client_cls must return Client or subclass")
    
    get_logger().debug(
        "Created %s with mock=%s, test_environment=%s, token_manager=%s",
        client.__class__.__name__,
        mock, test_environment, token_manager.__class__.__name__
        )
    return client

_add_auth_params_docs(
    build_client,
    "api_key", "api_secret", "token_manager", "mock", "test_environment",
    "leeway", "automatic_refresh", "client_cls", "kwds"
    )


def build_async_client(
    api_key: str,
    api_secret: str,
    token_manager: TokenManager,
    *,
    mock: bool=False,
    test_environment: bool=False,
    leeway: float=300.0,
    automatic_refresh: bool=False,
    async_client_cls: Optional[Callable[..., AsyncClient]]=None,
    **kwds
    ) -> AsyncClient:
    """
    Build an :py:class:`AsyncClient <finra.async_client.AsyncClient>` with an
    `AsyncOAuth2Client
    <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html#
    async-oauth-2-0>`__
    session and :py:class:`TokenManager <finra.token_manager.TokenManager>`
    """
    async def update_token(token: TokenType, *args, **kwds) -> Any:
        out = token_manager.update_token(token, *args, **kwds)
        if inspect.isawaitable(out):
            return await out
        return out
    
    if test_environment:
        token_endpoint = _TEST_TOKEN_ENDPOINT
    else:
        token_endpoint = _PROD_TOKEN_ENDPOINT
    
    if automatic_refresh:
        metadata = {"grant_type": "client_credentials"}
    else:
        metadata = {}
    
    session = AsyncOAuth2Client(
        api_key,
        api_secret,
        token=token_manager.token,
        token_endpoint=token_endpoint,
        update_token=update_token,
        leeway=leeway,
        **metadata
        )
    
    client = (async_client_cls or AsyncClient)(
        api_key,
        session,
        token_manager=token_manager,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )
    
    if async_client_cls is not None and not isinstance(client, AsyncClient):
        raise TypeError("async_client_cls must return AsyncClient or subclass")
    
    get_logger().debug(
        "Created %s with mock=%s, test_environment=%s, token_manager=%s",
        client.__class__.__name__,
        mock, test_environment, token_manager.__class__.__name__
        )
    return client

_add_auth_params_docs(
    build_async_client,
    "api_key", "api_secret", "token_manager", "mock", "test_environment",
    "leeway", "automatic_refresh", "async_client_cls", "kwds"
    )


##############################################################################
# CLIENT FROM READ & WRITE FUNCTIONS

def client_from_storage_functions(
    api_key: str,
    api_secret: str,
    token_read_func: Callable[[], TokenType],
    token_write_func: Callable[..., Any],
    *,
    is_asyncio: bool=False,
    mock: bool=False,
    test_environment: bool=False,
    **kwds
    ) -> Client | AsyncClient:
    """
    Build a client from custom storage functions. This is useful if the client
    credentials or token file do not exist locally, for example if the
    application is running in a cloud environment.
    """
    wrapped_token = token_read_func() # read wrapped token from storage
    
    token_manager = TokenManager.from_wrapped_token(
        wrapped_token,
        token_write_func
        ) # build token manager object from wrapped token
    
    # Don't emit token details in debug logs
    register_redactions(token_manager.token) # raw token
    
    if is_asyncio:
        return build_async_client(
            api_key,
            api_secret,
            token_manager,
            mock=mock,
            test_environment=test_environment,
            **kwds
            )
    
    return build_client(
        api_key,
        api_secret,
        token_manager,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )

_add_auth_params_docs(
    client_from_storage_functions,
    "api_key", "api_secret", "token_read_func", "token_write_func",
    "is_asyncio", "mock", "test_environment", "kwds"
    )


async def async_client_from_storage_functions(
    api_key: str,
    api_secret: str,
    token_read_func: Callable[[], TokenType],
    token_write_func: Callable[..., Any],
    *,
    mock: bool=False,
    test_environment: bool=False,
    **kwds
    ) -> AsyncClient:
    """
    Asynchronous version of :py:func:`client_from_storage_functions`.
    
    This is useful if the application uses a custom ``token_read_func``
    callback that is asynchronous, however this is not required. This function
    only returns :py:class:`AsyncClient <finra.async_client.AsyncClient>`.
    """
    wrapped_token = token_read_func() # read wrapped token from storage
    if inspect.isawaitable(wrapped_token): # optionally async
        _wrapped_token = await wrapped_token
    else:
        _wrapped_token = wrapped_token
    
    token_manager = TokenManager.from_wrapped_token(
        _wrapped_token,
        token_write_func
        ) # build token manager object from wrapped token
    
    # Don't emit token details in debug logs
    register_redactions(token_manager.token) # raw token
    
    return build_async_client(
        api_key,
        api_secret,
        token_manager,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )

_add_auth_params_docs(
    async_client_from_storage_functions,
    "api_key", "api_secret", "token_read_func", "token_write_func",
    "mock", "test_environment", "kwds"
    )


##############################################################################
# CLIENT FROM TOKEN FILE

def client_from_token_file(
    api_key: str,
    api_secret: str,
    token_path: str | Path,
    *,
    is_asyncio: bool=False,
    mock: bool=False,
    test_environment: bool=False,
    **kwds
    ) -> Client | AsyncClient:
    """
    Build a client from a token file that is already saved locally
    """
    token_read_func = __token_reader(token_path)
    token_write_func = __token_writer(token_path)
    return client_from_storage_functions(
        api_key,
        api_secret,
        token_read_func,
        token_write_func,
        is_asyncio=is_asyncio,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )

_add_auth_params_docs(
    client_from_token_file,
    "api_key", "api_secret", "token_path",
    "is_asyncio", "mock", "test_environment", "kwds"
    )


##############################################################################
# CLIENT FROM NEW TOKEN

def client_from_new_token(
    api_key: str,
    api_secret: str,
    token_path: Optional[str | Path],
    *,
    token_write_func: Optional[Callable[..., Any]]=None,
    is_asyncio: bool=False,
    mock: bool=False,
    test_environment: bool=False,
    **kwds
    ) -> Client | AsyncClient:
    """
    Fetch a new token from the `FINRA Identity Platform
    <https://developer.finra.org/docs#
    getting_started-api_platform_basics-authorization>`__
    and build a client. Any existing token file will be overwritten.
    """
    if token_write_func is None:
        if token_path is None:
            raise ValueError(
                "Must set token path to use default token_write_func"
                )
        token_write_func = __token_writer(token_path)
    
    # Fetch new token
    if test_environment:
        token_endpoint = _TEST_TOKEN_ENDPOINT
    else:
        token_endpoint = _PROD_TOKEN_ENDPOINT
    
    # Use a separate session to fetch, since client not created yet
    # NOTE: authlib typing stubs do not contain underlying httpx behavior
    session: Any = OAuth2Client(
        api_key,
        api_secret,
        token_endpoint=token_endpoint
        )
    try:
        token = session.fetch_token(grant_type="client_credentials")
    finally:
        session.close()
    
    # Don't emit token details in debug logs
    register_redactions(token)
    
    # Wrap token with metadata & write to storage
    token_manager = TokenManager(token, int(time.time()), token_write_func)
    token_manager.update_token(token) # write to storage
    
    if is_asyncio:
        return build_async_client(
            api_key,
            api_secret,
            token_manager,
            mock=mock,
            test_environment=test_environment,
            **kwds
            )
    
    return build_client(
        api_key,
        api_secret,
        token_manager,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )

_add_auth_params_docs(
    client_from_new_token,
    "api_key", "api_secret", "token_path", "token_write_func",
    "is_asyncio", "mock", "test_environment", "kwds"
    )


async def async_client_from_new_token(
    api_key: str,
    api_secret: str,
    token_path: Optional[str | Path],
    *,
    token_write_func: Optional[Callable[..., Any]]=None,
    mock: bool=False,
    test_environment: bool=False,
    **kwds
    ) -> AsyncClient:
    """
    Asynchronous version of :py:func:`client_from_new_token`.
    
    This function uses `AsyncOAuth2Client
    <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html#
    async-oauth-2-0>`__ during the initial token fetch, so
    it won't block other coroutines. This is also useful if the application
    uses a custom ``token_write_func`` callback that is asynchronous, however
    this is not required. This function only returns
    :py:class:`AsyncClient <finra.async_client.AsyncClient>`.
    """
    if token_write_func is None:
        if token_path is None:
            raise ValueError(
                "Must set token path to use default token_write_func"
                )
        token_write_func = __token_writer(token_path)
    
    # Fetch new token
    if test_environment:
        token_endpoint = _TEST_TOKEN_ENDPOINT
    else:
        token_endpoint = _PROD_TOKEN_ENDPOINT
    
    # Use a separate session to fetch, since client not created yet
    # NOTE: authlib typing stubs do not contain underlying httpx behavior
    session: Any = AsyncOAuth2Client(
        api_key,
        api_secret,
        token_endpoint=token_endpoint
        )
    try:
        token = await session.fetch_token(grant_type="client_credentials")
    finally:
        await session.aclose()
    
    # Don't emit token details in debug logs
    register_redactions(token)
    
    # Wrap token with metadata & write to storage
    token_manager = TokenManager(token, int(time.time()), token_write_func)
    out = token_manager.update_token(token) # write to storage
    if inspect.isawaitable(out): # optionally async
        await out
    
    return build_async_client(
        api_key,
        api_secret,
        token_manager,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )

_add_auth_params_docs(
    async_client_from_new_token,
    "api_key", "api_secret", "token_path", "token_write_func",
    "mock", "test_environment", "kwds"
    )


##############################################################################
# GET CLIENT

def get_client(
    api_key: str,
    api_secret: str,
    *,
    token_path: Optional[str | Path]=None,
    token_read_func: Optional[Callable[[], TokenType]]=None,
    token_write_func: Optional[Callable[..., Any]]=None,
    is_asyncio: bool=False,
    mock: bool=False,
    test_environment: bool=False,
    min_expires_in: Optional[float]=60.0 * 60.0,
    **kwds
    ) -> Client | AsyncClient:
    """
    This is the easiest way to create a client. If a token exists at the given
    path and it has not expired, it will be used. Otherwise, a new token will
    be fetched, and any existing token file will be overwritten.
    """
    if min_expires_in is None:
        min_expires_in = 0.0
    if min_expires_in < 0:
        raise ValueError("'min_expires_in' must be non-negative, or None")
    
    logger = get_logger()
    
    # Load token from local file path
    if token_path is not None:
        if Path(token_path).exists():
            c = client_from_token_file(
                api_key,
                api_secret,
                token_path,
                is_asyncio=is_asyncio,
                mock=mock,
                test_environment=test_environment,
                **kwds
                )
            logger.info("Loaded token from file '%s'", token_path)
            if c.token_expires_in > min_expires_in:
                return c
            
            logger.info("Token has expired, proactively creating a new one")
        else:
            logger.info("Token file not found, creating a new one")
        
    elif token_read_func is None or token_write_func is None:
        raise ValueError(
            "Must either provide local token path, or both token "
            "read and write functions"
            )
    
    # Load token using custom storage functions
    else:
        try:
            c = client_from_storage_functions(
                api_key,
                api_secret,
                token_read_func,
                token_write_func,
                is_asyncio=is_asyncio,
                mock=mock,
                test_environment=test_environment,
                **kwds
                )
        except Exception:
            logger.info("Token failed to load, creating a new one")
        else:
            logger.info("Loaded token using token read function")
            if c.token_expires_in > min_expires_in:
                return c
            
            logger.info("Token has expired, proactively creating a new one")
    
    # Fetch a new token from the authorization server
    c = client_from_new_token(
        api_key,
        api_secret,
        token_path,
        token_write_func=token_write_func,
        is_asyncio=is_asyncio,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )
    logger.info(
        "Returning client with new token, writing token to '%s'", token_path
        )
    return c

_add_auth_params_docs(
    get_client,
    "api_key", "api_secret", "token_path",
    "token_read_func", "token_write_func",
    "is_asyncio", "mock", "test_environment", "min_expires_in", "kwds"
    )


async def get_async_client(
    api_key: str,
    api_secret: str,
    *,
    token_path: Optional[str | Path]=None,
    token_read_func: Optional[Callable[[], TokenType]]=None,
    token_write_func: Optional[Callable[..., Any]]=None,
    mock: bool=False,
    test_environment: bool=False,
    min_expires_in: Optional[float]=60.0 * 60.0,
    **kwds
    ) -> AsyncClient:
    """
    Asynchronous version of :py:func:`get_client`.
    
    This function won't block other coroutines during an initial token fetch.
    This is also useful if the application uses custom ``token_read_func`` and
    ``token_write_func`` callbacks that are asynchronous, however this is not
    required. This function only returns
    :py:class:`AsyncClient <finra.async_client.AsyncClient>`.
    """
    if min_expires_in is None:
        min_expires_in = 0.0
    if min_expires_in < 0:
        raise ValueError("'min_expires_in' must be non-negative, or None")
    
    logger = get_logger()
    
    # Load token from local file path
    if token_path is not None:
        if Path(token_path).exists():
            c = client_from_token_file(
                api_key,
                api_secret,
                token_path,
                is_asyncio=True,
                mock=mock,
                test_environment=test_environment,
                **kwds
                )
            logger.info("Loaded token from file '%s'", token_path)
            if c.token_expires_in > min_expires_in:
                return cast(AsyncClient, c)
            
            logger.info("Token has expired, proactively creating a new one")
        else:
            logger.info("Token file not found, creating a new one")
        
    elif token_read_func is None or token_write_func is None:
        raise ValueError(
            "Must either provide local token path, or both token "
            "read and write functions"
            )
    
    # Load token using custom storage functions
    else:
        try:
            c = await async_client_from_storage_functions(
                api_key,
                api_secret,
                token_read_func,
                token_write_func,
                mock=mock,
                test_environment=test_environment,
                **kwds
                )
        except Exception:
            logger.info("Token failed to load, creating a new one")
        else:
            logger.info("Loaded token using token read function")
            if c.token_expires_in > min_expires_in:
                return c
            
            logger.info("Token has expired, proactively creating a new one")
    
    # Fetch a new token from the authorization server
    c = await async_client_from_new_token(
        api_key,
        api_secret,
        token_path,
        token_write_func=token_write_func,
        mock=mock,
        test_environment=test_environment,
        **kwds
        )
    logger.info(
        "Returning client with new token, writing token to '%s'", token_path
        )
    return c

_add_auth_params_docs(
    get_async_client,
    "api_key", "api_secret", "token_path",
    "token_read_func", "token_write_func",
    "mock", "test_environment", "min_expires_in", "kwds"
    )
