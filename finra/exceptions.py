from typing import Any


__all__ = ["MockException", "QATestEnvException"]


class MockException(ValueError):
    """
    Raised if the client is set to use the Mock API, and tries to call an
    endpoint that does not have a mock dataset
    """
    
    def __init__(self):
        super().__init__(
            "This method does not have a Mock endpoint. To use this method "
            "set mock=False when creating the client, and use non-Mock API "
            "credentials."
            )


class QATestEnvException(ValueError):
    """
    Raised if the client is not set to use the QA Test Environment, and tries
    to call an endpoint that only supports the QA Test Environment
    """
    
    def __init__(self):
        super().__init__(
            "This endpoint is only available in the QA Test Environment. To "
            "use this method set test_environment=True when creating the "
            "client, and use QA Test Environment credentials."
            )


def _type_error(key: str, value: Any, expected_types: tuple[Any, ...]) -> None:
    """
    Generic type error message
    
    :param key:
    :param value:
    :param expected_types:
    """
    _type = type(value)
    if len(expected_types) == 1:
        t = expected_types[0]
        raise TypeError(
            f"Expected type {t.__module__}.{t.__name__} for '{key}', "
            f"but received {_type.__module__}.{_type.__name__}"
            )
    
    _expected_types = [f"{t.__module__}.{t.__name__}" for t in expected_types]
    raise TypeError(
        f"Expected type in ({', '.join(_expected_types)}) for '{key}', "
        f"but received {_type.__module__}.{_type.__name__}"
        )

