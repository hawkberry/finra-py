from types import TracebackType
from typing import Any, Optional, Self

import httpx
from authlib.integrations.httpx_client import OAuth2Client

from .base_client import BaseClient, _log_wrapper, _add_client_init_docs
from .token_manager import TokenManager


__all__ = ["Client"]


class Client(BaseClient):
    """
    `FINRA API <https://developer.finra.org/docs>`__ Client that supports all
    API endpoints
    """
    
    def __init__(
        self,
        api_key: str,
        session: Any,
        *,
        mock: bool=False,
        test_environment: bool=False,
        token_manager: Optional[TokenManager]=None,
        timeout: float=30.0,
        accept_json: Optional[bool]=True,
        require_enums: bool=True
        ):
        if not isinstance(session, OAuth2Client):
            raise TypeError(
                f"Unknown session type {type(session).__name__}, "
                "expected a subclass of "
                "authlib.integrations.httpx_client.OAuth2Client"
                )
        
        super().__init__(
            api_key,
            session,
            mock=mock,
            test_environment=test_environment,
            token_manager=token_manager,
            timeout=timeout,
            accept_json=accept_json,
            require_enums=require_enums
            )
        
        self._schema_registry: dict[str, Any] = {}
        
    @property
    def schema_registry(self) -> dict[str, Any]:
        return self._schema_registry
    
    @_log_wrapper("GET")
    def _get_request(self,
        url: str,
        params: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return self._session.get(url, params=params, headers=headers)
    
    @_log_wrapper("POST")
    def _post_request(self,
        url: str,
        data: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return self._session.post(url, json=data, headers=headers)
    
    @_log_wrapper("PUT")
    def _put_request(self,
        url: str,
        data: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return self._session.put(url, json=data, headers=headers)
    
    @_log_wrapper("PATCH")
    def _patch_request(self,
        url: str,
        data: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return self._session.patch(url, json=data, headers=headers)
    
    @_log_wrapper("DELETE")
    def _delete_request(self,
        url: str,
        _: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return self._session.delete(url, headers=headers)
    
    @_log_wrapper("GET RESOURCE") # request for pre-signed URLs
    def _get_resource_request(
        self,
        url: str,
        params: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return self._resource_session.get(url, params=params, headers=headers)
    
    def _set_resource_session(self) -> None:
        self._resource_session = httpx.Client(timeout=self._session.timeout)
    
    def refresh_token(self) -> None:
        """
        Fetch a new token from the `FINRA Identity Platform
        <https://developer.finra.org/docs#
        getting_started-api_platform_basics-authorization>`__
        """
        self._set_token(
            self._session.fetch_token(grant_type="client_credentials")
            )
    
    def close(self) -> None:
        """
        Close the `OAuth2Client
        <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html>`__
        session to free up resources
        """
        self._session.close()
        if getattr(self, "_resource_session", None):
            self._resource_session.close()
    
    def __enter__(self) -> Self:
        """Enter context to automatically close client on exit"""
        return self
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
        ) -> None:
        """
        Exit context
        
        :param exc_type:
        :param exc_value:
        :param traceback:
        """
        self.close()
        return

_add_client_init_docs(
    Client,
    "The synchronous `OAuth2Client "
    "<https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html>`__"
    )

