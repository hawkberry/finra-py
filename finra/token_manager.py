import time
from typing import Any, Callable, Self


__all__ = ["TokenManager"]


class TokenManager:
    """
    Provides the functionality required to maintain and update token metadata
    
    :param token: The token to wrap in metadata
    :param created_timestamp: Timestamp at which this token was initially
        created. This timestamp does not change when the token is updated.
    :param token_write_func: Function that accepts a raw token and writes it to
        disk or other persistent storage
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
        """
        Returns the number of seconds since the token was initially created
        """
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
    
    def update_token(self, token: dict[str, Any], *args, **kwds) -> None:
        """
        Returns a version of the write function that wraps the ``token`` in
        additional metadata, and writes it to disk or some other persistent
        storage location
        
        :param token: The raw token to wrap in metadata
        :param args: Arguments for the ``token_write_func``
        :param kwds: Keyword arguments for the ``token_write_func``
        """
        self._token_write_func(self._wrap_metadata(token), *args, **kwds)
        self.token = token
        
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

