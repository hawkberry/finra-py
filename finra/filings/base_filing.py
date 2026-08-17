from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable, Optional, Self, TypeAlias

from ..enum_converter import E, EnumStr, EnumConverter
from ..exceptions import _type_error
from .._utils import build_json_object


__all__ = [
    "FilingDictType",
    "BaseFiling",
    "BaseFilingOps",
    ]


##############################################################################
# BASE FILING

#: Type of object returned by :py:meth:`BaseFiling.build`.
FilingDictType: TypeAlias = dict[str, Any]


class FilingStatus(Enum):
    """
    Used in a filing to set the filing status.
    See :py:meth:`BaseFilingOps.set_filing_status`.
    """
    __skip_module_autodoc__ = True
    
    DRAFT = "draft"
    
    SUBMITTED = "submitted"
    
    VALIDATE = "validate"


_FilingStatus: TypeAlias = EnumStr[FilingStatus]


class Op(Enum):
    """
    Used in a filing to specify an action for a JSON operation.
    See :py:meth:`BaseFilingOps.add_operation`.
    """
    __skip_module_autodoc__ = True
    
    #: Add a new value
    ADD = "add"
    
    #: Replace the value at the given path with a new value
    REPLACE = "replace"
    
    #: Remove the value at the given path
    REMOVE = "remove"


_Op: TypeAlias = EnumStr[Op]


# Private class used by BaseFiling for building filing metadata
class _Metadata:
    def __init__(self):  # attribute names with underscores are API keys
        self._filingStatus = None
        self._filingType = None
        self._individualCrdNumber = None
        self._dateOfBirth = None
        self._repAccess = None
        self._repCompletionStatus = None
        self._ignoreWarnings = None
        
    def set_filing_status(self, filing_status: Optional[str]) -> None:
        self._filingStatus = filing_status
        
    def set_filing_type(self, filing_type: Optional[str]) -> None:
        self._filingType = filing_type
        
    def set_individual_crd_number(self, individual_crd_number: Optional[int]) -> None:
        self._individualCrdNumber = individual_crd_number
        
    def set_date_of_birth(self, date_of_birth: Optional[str]) -> None:
        self._dateOfBirth = date_of_birth
        
    def set_rep_access(self, rep_access: Optional[dict[str, bool]]) -> None:
        self._repAccess = rep_access
        
    def set_rep_completion_status(self, rep_completion_status: Optional[str]) -> None:
        self._repCompletionStatus = rep_completion_status
        
    def set_ignore_warnings(self, ignore_warning: Optional[bool]) -> None:
        self._ignoreWarnings = ignore_warning


class BaseFiling(EnumConverter, ABC):
    """Abstract base class for filing objects"""
    
    # Attribute names with underscores are API keys
    def __init__(self, require_enums: bool=True):
        super().__init__(require_enums)
        self._metadata = _Metadata()
        self._filingData: Optional[dict] = None
        
    @property
    @abstractmethod
    def schema_url(self) -> str:
        raise NotImplementedError
    
    
    #######################################################################
    # FILING DATA
    
    def set_filing_data(self, filing_data: Optional[dict]) -> Self:
        """
        Set the filing data for the filing
        
        :param filing_data: The JSON object filing data.
        """
        self._filingData = filing_data
        return self
    
    def clear_filing_data(self) -> None:
        """Clear the filing data"""
        self._filingData = None
        
    def build(self) -> FilingDictType:
        if self._metadata._filingStatus is None:
            raise ValueError("Must set filing status")
        return {"filing": build_json_object(self)}


##############################################################################
# BASE FILING WITH OPERATIONS

class BaseFilingOps(BaseFiling):
    """
    Abstract base class for filings objects that support partial update
    operations and multiple modes for filing status
    """
    
    # Attribute names with underscores are API keys
    def __init__(self, require_enums: bool=True):
        super().__init__(require_enums)
        self._operations: Optional[list] = None
    
    
    #######################################################################
    # FILING STATUS
    
    FilingStatus = FilingStatus
    
    def set_filing_status(
        self,
        filing_status: Optional[_FilingStatus]
        ) -> Self:
        """
        Set the filing status for the filing
        
        :param filing_status: The filing status provided as an enum member
        """
        if filing_status is None:
            _filing_status = None
        else:
            _filing_status = self._convert(filing_status, self.FilingStatus)
        self._metadata.set_filing_status(_filing_status)
        return self
    
    def clear_filing_status(self) -> None:
        """Clear the filing status"""
        self._metadata.set_filing_status(None)
    
    
    #######################################################################
    # OPERATIONS
    
    Op = Op
    
    def add_operation(
        self,
        op: _Op,
        path: str | Iterable[str | tuple[str, Any]],
        value: Optional[Any]=None,
        ) -> Self:
        """
        Add instructions for updating the filing using a JSON operation. If
        both filing data and operations are provided in a single call,
        operations will be ignored.
        
        For more information, see the tutorial on :ref:`operations`.
        
        :param op: The action in the JSON operation provided as an enum member
        :param path: The location or traversal route within a JSON document
        :param value: The new value to place at the path endpoint. Required for
            :py:attr:`Op.ADD` and :py:attr:`Op.REPLACE` operations, and must be
            ``None`` for :py:attr:`Op.REMOVE`.
        """
        operation = {"op": self._convert(op, self.Op)}
        
        if not path:
            raise ValueError("The path must be non-empty")
        
        if isinstance(path, str):
            operation["path"] = path if path[0] == "/" else "/" + path
        else:
            _path = []
            for s in path:
                if isinstance(s, str):
                    _path.append(s)
                elif isinstance(s, Iterable):
                    if len(s) != 2:
                        raise ValueError(
                            "To select an object in an array, a path "
                            "element must be a 2-element (<key>, <value>) "
                            "iterable representing the property to select on."
                            )
                    _path.append(f"[{':'.join(map(str, s))}]")
                else:
                    _path.append(f"{s}")
            operation["path"] = "/" + "/".join(_path)
            
        if operation["op"] in ("add", "replace"):
            if value is None:
                raise ValueError(
                    "Must provide a value if operation is 'add' or 'replace'"
                    )
            operation["value"] = value
            
        elif value is not None:  # REMOVE operation
            raise ValueError("A value is not allowed if operation is 'remove'")
        
        if self._operations is None:
            self._operations = []
        self._operations.append(operation)
        return self
    
    def clear_operations(self) -> None:
        """Clear the operations"""
        self._operations = None


##############################################################################
# COMMON FILING FIELDS

def _set_filing_type(
    filing: BaseFiling,
    filing_type: Optional[EnumStr[E]],
    enum: type[E]
    ):
    if filing_type is None:
        _filing_type = None
    else:
        _filing_type = filing._convert(filing_type, enum)
    filing._metadata.set_filing_type(_filing_type)


def _set_individual_crd_number(
    filing: BaseFiling,
    individual_crd_number: Optional[int]
    ):
    """
    Set the Individual CRD Number for the filing
    
    :param individual_crd_number: The Individual CRD Number for a registered
        individual
    """
    if individual_crd_number is None:
        _individual_crd_number = None
    else:
        _individual_crd_number = int(individual_crd_number)
    filing._metadata.set_individual_crd_number(individual_crd_number)


def _set_date_of_birth(filing: BaseFiling, date_of_birth: Optional[date]):
    """
    Set the Date of Birth for the filing
    
    :param date_of_birth: The Date of Birth for an individual
    """
    if date_of_birth is None:
        _date_of_birth = None
    else:
        if (not isinstance(date_of_birth, date)
            or isinstance(date_of_birth, datetime)):
            _type_error("date_of_birth", date_of_birth, (date,))
        _date_of_birth = date_of_birth.isoformat()
    filing._metadata.set_date_of_birth(_date_of_birth)

