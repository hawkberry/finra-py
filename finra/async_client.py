from types import TracebackType
from typing import Any, Optional, Self

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from .base_client import BaseClient, _log_wrapper, _add_client_init_docs
from .token_manager import TokenManager


__all__ = ["AsyncClient"]


class AsyncClient(BaseClient):
    """
    `FINRA API <https://developer.finra.org/docs>`__ Client with asyncio
    support for all API endpoints
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
        if not isinstance(session, AsyncOAuth2Client):
            raise TypeError(
                f"Unknown session type {type(session).__name__}, "
                "expected a subclass of "
                "authlib.integrations.httpx_client.AsyncOAuth2Client"
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
        
    @_log_wrapper("GET")
    async def _get_request(self,
        url: str,
        params: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return await self._session.get(url, params=params, headers=headers)
    
    @_log_wrapper("POST")
    async def _post_request(self,
        url: str,
        data: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return await self._session.post(url, json=data, headers=headers)
    
    @_log_wrapper("PUT")
    async def _put_request(self,
        url: str,
        data: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return await self._session.put(url, json=data, headers=headers)
    
    @_log_wrapper("PATCH")
    async def _patch_request(self,
        url: str,
        data: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return await self._session.patch(url, json=data, headers=headers)
    
    @_log_wrapper("DELETE")
    async def _delete_request(
        self,
        url: str,
        _: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return await self._session.delete(url, headers=headers)
    
    @_log_wrapper("GET RESOURCE") # request for pre-signed URLs
    async def _get_resource_request(
        self,
        url: str,
        params: Optional[dict[str, Any]],
        headers: Optional[dict[str, str]]
        ) -> httpx.Response:
        return await self._resource_session.get(
            url, params=params, headers=headers
            )
    
    def _set_resource_session(self) -> None:
        self._resource_session = httpx.AsyncClient(
            timeout=self._session.timeout
            )
        
    async def refresh_token(self) -> None:
        """
        Fetch a new token from the `FINRA Identity Platform
        <https://developer.finra.org/docs#
        getting_started-api_platform_basics-authorization>`__
        """
        self._set_token(
            await self._session.fetch_token(grant_type="client_credentials")
            )
        
    async def close(self) -> None:
        """
        Close the `AsyncOAuth2Client
        <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html#
        async-oauth-2-0>`__
        session to free up resources
        """
        await self._session.aclose()
        if getattr(self, "_resource_session", None):
            await self._resource_session.aclose()
        
    async def __aenter__(self) -> Self:
        """Enter asynchronous context to automatically close client on exit"""
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
        ) -> None:
        """
        Exit asynchronous context
        
        :param exc_type:
        :param exc_value:
        :param traceback:
        """
        await self.close()
        return

_add_client_init_docs(
    AsyncClient,
    "The asynchronous `AsyncOAuth2Client "
    "<https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html#"
    "async-oauth-2-0>`__"
    )

