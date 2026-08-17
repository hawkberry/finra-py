from enum import Enum, EnumType
from difflib import get_close_matches
from typing import Any, Iterable, TypeAlias, TypeVar


__all__ = ["EnumConverter"]


# Typing parameterization, internal types
E = TypeVar("E", bound=Enum)

EnumStr: TypeAlias = E | str

EnumAny: TypeAlias = E | Any


def _add_require_enums_docs(cls: type) -> None:
    cls.__doc__ = (getattr(cls, "__doc__") or "") + """
:param require_enums: Option to require enums within this object. If ``True``,
    a ``TypeError`` will be raised if a provided value is not a member of the
    expected enum.
"""


# Include module in enum's fully qualified name
# Names should reflect user facing attribute access where applicable
def _fully_qualified(enum: EnumType) -> str:
    out = f"{enum.__module__}.{enum.__qualname__}"
    if ".filings." in out:
        if ".Op" in out:
            out = out.replace(".Op", ".BaseFilingOps.Op")
        elif ".FilingStatus" in out:
            out = out.replace(".FilingStatus", ".BaseFilingOps.FilingStatus")
        elif ".form_br." in out:
            out = out.replace(".FilingType", ".FormBR.FilingType")
        elif ".form_u4." in out:
            out = out.replace(".FilingType", ".FormU4.FilingType")
            out = out.replace(".RepAccessType", ".FormU4.RepAccessType")
        elif ".form_u5." in out:
            out = out.replace(".FilingType", ".FormU5.FilingType")
        else: # ".non_registered_fingerprint." in out
            out = out.replace(
                ".FilingType", ".NonRegisteredFingerprint.FilingType"
                )
    elif ".filters." in out:
        out = out.replace(".CompareType", ".Filter.CompareType")
    else:
        out = out.replace("_enums.", "base_client.BaseClient.")
    return out


# Get possible enum members resembling passed value using difflib matching
# If passed value is an enum, check it against member names
# If passed value is a string, check it against member names and values
def _possible_members(value: Enum | str, enum: EnumType, **kwds) -> list[str]:
    
    # Normalize string to case-insensitive with underscores removed
    def norm_str(s: str) -> str:
        return s.replace("_", "").strip().casefold()
    
    enum_name = _fully_qualified(enum)
    names = {norm_str(n): n for n in enum.__members__.keys()}
    
    # Check similarity with member names
    if isinstance(value, Enum):
        value = value.name
        candidates = get_close_matches(norm_str(value), names, **kwds)
        suggestions = [f"{enum_name}.{names[c]}" for c in candidates]
        
    # Check similarity with member names and values
    else:
        values = {norm_str(enum[n].value): n for n in enum.__members__.keys()}
        candidates = get_close_matches(norm_str(value), names | values, **kwds)
        suggestions = [
            f"{enum_name}.{names[c]}" if c in names else
            f"{enum_name}.{values[c]}" for c in candidates
            ]
    
    # Return unique values from iterable, preserving order
    seen = set()
    out = []
    for v in suggestions: # msg should reflect enums accessed via BaseClient
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


class EnumConverter:
    """
    Base class for objects that require enums and perform enum conversion
    """
    
    def __init__(self, require_enums: bool):
        self.require_enums = require_enums
        
    @staticmethod
    def _raise_type_error(
        enum_name: str,
        val_name: str,
        msg: str
        ) -> None:
        raise TypeError(
            f"Expected type(s): {enum_name}. Got type '{val_name}'. "
            + (f"Did you mean: {msg}? " if msg else "")
            + "(Initialize with require_enums=False to disable this check)"
            )
    
    def _type_error(
        self,
        value: EnumAny[E],
        enum: type[E]
        ) -> None:
        val_type = type(value)
        val_name = getattr(val_type, "__qualname__", val_type.__name__)
        enum_name = _fully_qualified(enum)
        if isinstance(value, (Enum, str)):
            msg = ", ".join(_possible_members(value, enum))
        else:
            msg = ""
        self._raise_type_error(enum_name, val_name, msg)
        
    # Convert an enum member to its value
    def _convert(
        self,
        value: EnumAny[E],
        enum: type[E]
        ) -> Any:
        if isinstance(value, enum):
            return value.value
        if self.require_enums: # raise if enums required & value is non-enum
            self._type_error(value, enum)
        return value
    
    # Convert an iterable of enum members to their values
    def _convert_iterable(
        self,
        values: EnumAny[E] | Iterable[EnumAny[E]],
        enum: type[E]
        ) -> list[Any]:
        if isinstance(values, str) or not isinstance(values, Iterable):
            values = [values]
        if self.require_enums: # raise if enums required & a value is non-enum
            _values: list[Any] = []
            for value in values:
                if isinstance(value, enum):
                    _values.append(value.value)
                else:
                    self._type_error(value, enum)
            return _values
        return [v.value if isinstance(v, enum) else v for v in values]
    
    def _type_error_union(
        self,
        value: Enum | Any,
        enum: tuple[EnumType, ...]
        ) -> None:
        val_type = type(value)
        val_name = getattr(val_type, "__qualname__", val_type.__name__)
        enum_name = ", ".join(map(_fully_qualified, enum))
        if isinstance(value, (Enum, str)):
            _members = []
            for e in enum:
                members = _possible_members(value, e)
                if members:
                    _members.append(", ".join(members))
            msg = "\n" + "\n".join(_members) if _members else ""
        else:
            msg = ""
        self._raise_type_error(enum_name, val_name, msg)
        
    # Convert an enum member that belongs to one of several enums
    # Union of enums **cannot** be parameterized
    def _convert_union(
        self,
        value: Enum | Any,
        enum: tuple[EnumType, ...]
        ) -> Any:
        if isinstance(value, enum):
            return value.value
        if self.require_enums: # raise if enums required & value is non-enum
            self._type_error_union(value, enum)
        return value
    
    def set_require_enums(self, require_enums: bool) -> None:
        """
        Set the option to require enums within this object for all values that
        use enums. If ``True``, a ``TypeError`` will be raised if a provided
        value is not a member of the expected enum. If ``False``, this behavior
        will be disabled for all values that use enums. For most cases, it is
        suggested to use ``require_enums=True`` unless absolutely necessary.
        """
        self.require_enums = require_enums


_add_require_enums_docs(EnumConverter)

