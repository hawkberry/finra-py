import difflib
import inspect
import json
from functools import partial, wraps
from unittest.mock import MagicMock

import httpx
from colorama import Fore


# Decorator to prevent duplicate test names
__NO_DUPLICATES: set[str] = set()

def no_duplicates(f): # pragma: no cover
    if f.__qualname__ in __NO_DUPLICATES:
        raise AttributeError(f"Duplicate definition of {f.__qualname__}")
    __NO_DUPLICATES.add(f.__qualname__)
    return f


# Set partial function as a method on a test object with a unique name
def set_meth(obj, method, func, *args, **kwds):
    p = partial(func, *args, **kwds)
    @wraps(func)
    def f(self, *args, **kwds):
        return p(self, *args, **kwds)
    f.__qualname__ = f"{obj.__qualname__}.{method}"
    setattr(obj, method, no_duplicates(f))


# Print difference message and return boolean, if there is a difference
def has_diff(old, new, sort_keys=True): # pragma: no cover
    old_out = json.dumps(old, indent=4, sort_keys=sort_keys).splitlines()
    new_out = json.dumps(new, indent=4, sort_keys=sort_keys).splitlines()
    diff = difflib.ndiff(old_out, new_out)
    diff, has_diff = color_diff(diff)
    if has_diff:
        print('\n'.join(diff))
    return has_diff


# Apply color to output message
def color_diff(diff): # pragma: no cover
    has_diff = False
    output = []
    for line in diff:
        if line.startswith('+'):
            output.append(Fore.GREEN + line + Fore.RESET)
            has_diff = True
        elif line.startswith('-'):
            output.append(Fore.RED + line + Fore.RESET)
            has_diff = True
        elif line.startswith('^'):
            output.append(Fore.BLUE + line + Fore.RESET)
            has_diff = True
        else:
            output.append(line)
    return output, has_diff


class MockOAuth2Client(MagicMock):
    def __call__(self, *args, **kwds):
        if 'update_token' in kwds:
            assert not inspect.iscoroutinefunction(kwds['update_token'])
        return MagicMock.__call__(self, *args, **kwds)
    

class MockAsyncOAuth2Client(MagicMock): # NOTE: not async mock, for auth tests
    def __call__(self, *args, **kwds):
        if 'update_token' in kwds: # pragma: no cover
            assert inspect.iscoroutinefunction(kwds['update_token'])
        return MagicMock.__call__(self, *args, **kwds)
    

class MockResponse(httpx.Response): # pragma: no cover
    def raise_for_status(self):
        if self.status_code > 299:
            raise Exception(f"Failed status code: {self.status_code}")

