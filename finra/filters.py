from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable, Optional, Self, TypeAlias
from zoneinfo import ZoneInfo

from ._utils import build_json_object, datetime_isoformat_ms
from .enum_converter import _add_require_enums_docs, E, EnumConverter, EnumStr
from .exceptions import _type_error


__all__ = ["Filter", "FiltersDictType"]


#: Type of object returned by :py:meth:`Filter.build`
FiltersDictType: TypeAlias = dict[str, list[dict[str, Any]]]


class CompareType(Enum):
    """
    Comparison operators used by :py:class:`Filter` to compare a field with a
    value. See :py:meth:`Filter.add_compare`.
    """
    __skip_module_autodoc__ = True
    
    GREATER = "GREATER"
    
    LESSER = "LESSER"
    
    EQUAL = "EQUAL"
    
    GTE = "GTE"
    
    LTE = "LTE"
    
    NOT_EQUAL = "NOT_EQUAL"
    
    BEGINS_WITH = "BEGINS_WITH"


_CompareType: TypeAlias = EnumStr[CompareType]


class Filter(EnumConverter):
    """
    Build a filter for advanced query selection. To see learn more about
    filters see the :ref:`filters` section of the Query API tutorial.
    
    :param enum: The enum type representing the field names for a dataset
    :type enum: :py:type:`EnumType`
    """
    
    def __init__(self, enum: type[E], *, require_enums: bool=True):
        super().__init__(require_enums)
        self.enum = enum
        self._compareFilters: Optional[list] = None
        self._dateRangeFilters: Optional[list] = None
        self._domainFilters: Optional[list] = None
        
    @staticmethod
    def _datetime_isoformat(dt: date | datetime) -> str:
        if isinstance(dt, datetime): # server expects America/New_York
            if dt.tzinfo is None:
                return datetime_isoformat_ms(dt, sep=" ")
            return datetime_isoformat_ms(
                dt.astimezone(ZoneInfo("America/New_York")), sep=" "
                )
        return dt.isoformat()
    
    CompareType = CompareType
    
    def add_compare(
        self,
        field: EnumStr[E],
        value: Any,
        compare_type: Optional[_CompareType]=None
        ) -> Self:
        """
        Set field value comparisons using standard operators. See
        :py:class:`CompareType` for available operator values.
        
        :param field: The field name provided as an enum member
        :type field: :py:type:`Enum` | :py:type:`str`
        :param value: The field value used for comparison
        :param compare_type: The comparison operator provided as an enum
            member. Default: :py:attr:`CompareType.EQUAL`.
        """
        if compare_type is None: # default to EQUAL
            compare_type = "EQUAL"
        else:
            compare_type = self._convert(compare_type, self.CompareType)
        if isinstance(value, date):
            value = self._datetime_isoformat(value)
        if self._compareFilters is None:
            self._compareFilters = []
        self._compareFilters.append({
            "fieldName": self._convert(field, self.enum),
            "fieldValue": value,
            "compareType": compare_type,
            })
        return self
    
    def clear_compare(self) -> None:
        """Clear the compare filters."""
        self._compareFilters = None
        
    def add_date_range(
        self,
        field: EnumStr[E],
        start_date: date | datetime,
        end_date: date | datetime
        ) -> Self:
        """
        Provide a date (or datetime) range for a date (or datetime) field.
        Start and end dates of the range are inclusive.
        
        :param field: The field name provided as an enum member
        :type field: :py:type:`Enum` | :py:type:`str`
        :param start_date: The start date of the date range
        :param end_date: The end date of the date range
        """
        if not isinstance(start_date, date):
            _type_error("start_date", start_date, (date, datetime))
        if not isinstance(end_date, date):
            _type_error("end_date", end_date, (date, datetime))
        if self._dateRangeFilters is None:
            self._dateRangeFilters = []
        self._dateRangeFilters.append({
            "fieldName": self._convert(field, self.enum),
            "startDate": self._datetime_isoformat(start_date),
            "endDate": self._datetime_isoformat(end_date),
            })
        return self
    
    def clear_date_range(self) -> None:
        """Clear the date range filters."""
        self._dateRangeFilters = None
        
    def add_domain(
        self,
        field: EnumStr[E],
        values: Any
        ) -> Self:
        """
        Provide a specific value, or iterable of values, for a field.
        
        :param field: The field name provided as an enum member
        :type field: :py:type:`Enum` | :py:type:`str`
        :param values: The field value or iterable of values to filter on
        """
        if isinstance(values, str) or not isinstance(values, Iterable):
            values = [values]
        else:
            values = list(set(values))
        _values = [
            self._datetime_isoformat(v)
            if isinstance(v, date) else v for v in values
            ]
        if self._domainFilters is None:
            self._domainFilters = []
        self._domainFilters.append({
            "fieldName": self._convert(field, self.enum),
            "values": _values,
            })
        return self
    
    def clear_domain(self) -> None:
        """Clear the domain filters."""
        self._domainFilters = None
        
    def build(self) -> FiltersDictType:
        """Build and return JSON object used as a filter in an API request."""
        return build_json_object(self)


_add_require_enums_docs(Filter)

