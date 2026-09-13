import time
from typing import Any, Callable, Self


__all__ = ["TokenManager"]


class TokenManager:
    """
    Manages metadata associated with the client's authentication token
    
    :param token: The raw token managed by this object
    :param created_timestamp: The timestamp when the token was created
    :param token_write_func: Callable that accepts the raw token as an argument
        and writes it to disk or another storage location
    """
    
    def __init__(
        self,
        token: dict[str, Any],
        created_timestamp: int,
        token_write_func: Callable
        ):
        self.token = token # raw token
        self.created_timestamp = created_timestamp
        self._token_write_func = token_write_func # callback to store token
        
    @property
    def token_age(self) -> int:
        """Returns the number of seconds since the token was created"""
        return int(time.time()) - self.created_timestamp
    
    @property
    def expires_at(self) -> int:
        """Returns the expiration timestamp"""
        return int(self.token["expires_at"])
    
    @property
    def expires_in(self) -> int:
        """Returns the number of seconds until the token expires"""
        return self.expires_at - int(time.time()) - 1 # round down
    
    def _wrap_metadata(self, token: dict[str, Any]) -> dict[str, Any]:
        return {
            "created_timestamp": self.created_timestamp,
            "token": token,
            }
    
    # OAuth2Client can pass ``refresh_token`` and ``access_token`` kwds
    # These are passed directly to token_write_func
    def update_token(
        self,
        token: dict[str, Any],
        *args: Any,
        **kwds: Any
        ) -> Any:
        """
        Wraps the ``token`` with metadata and passes it to the
        ``token_write_func`` to write it to disk or some other storage
        location.
        
        If ``token_write_func`` is an asynchronous callback, its awaitable
        coroutine will be returned and must be awaited to write the token.
        
        :param token: The raw token to wrap in metadata
        :param args: Arguments passed to the ``token_write_func``
        :param kwds: Keyword arguments passed to the ``token_write_func``
        :return: The value returned by ``token_write_func``
        """
        self.token = token
        self.created_timestamp = int(time.time())
        return self._token_write_func(
            self._wrap_metadata(token), *args, **kwds
            )
    
    @classmethod
    def from_wrapped_token(
        cls,
        token: dict[str, Any],
        token_write_func: Callable
        ) -> Self:
        """
        Construct a new :py:class:`TokenManager` object from the metadata of
        the provided ``token``. If the ``token`` has no metadata, a
        ``ValueError`` is raised, indicating that the ``token`` is invalid, and
        a new one must be created.
        
        :param token: The wrapped token, wrapped in metadata
        :param token_write_func: Function that accepts a raw token and writes
            it to disk or other persistent storage
        """
        if "created_timestamp" not in token:
            raise ValueError(
                "WARNING: The token format has changed since this token "
                "was created. Please delete it and create a new one."
                )
        
        return cls(
            token["token"], token["created_timestamp"], token_write_func
            )

