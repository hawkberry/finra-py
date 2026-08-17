from datetime import date
from enum import Enum
from typing import Optional, Self, TypeAlias

from ..enum_converter import _add_require_enums_docs, EnumStr
from .base_filing import (
    BaseFilingOps, FilingDictType, _set_filing_type,
    _set_individual_crd_number, _set_date_of_birth,
    )


__all__ = ["FormU5"]


class FilingType(Enum):
    """
    Used in a filing to set the filing type.
    See :py:meth:`FormU5.set_filing_type`.
    """
    __skip_module_autodoc__ = True
    
    FULL = "FULL"
    
    AMENDMENT = "AMENDMENT"
    
    PARTIAL = "PARTIAL"


_FilingType: TypeAlias = EnumStr[FilingType]


class FormU5(BaseFilingOps):
    """
    Form U5 is the Uniform Termination Notice for Securities Industry
    Registration.
    
    This class can be used to:
    
      - wrap filing data with the correct metadata
      - build operations to amend or update filing data
      - validate filing data against the schema on the client-side, prior to
        submission
    
    This class cannot be used to:
    
      - build or pre-fill filing data directly
    
    Filings can be made in ``draft``, ``submitted``, or ``validate`` mode, by
    providing a member of :py:class:`FilingStatus
    <finra.filings.base_filing.BaseFilingOps.FilingStatus>` to
    :py:meth:`FormU5.set_filing_status()
    <finra.filings.base_filing.BaseFilingOps.set_filing_status>`.
    
    Filings must adhere to the `U5 schema
    <https://schemas.api.finra.org/FINRAApiPlatformU5Filing.json>`__. Setting
    :py:attr:`FilingStatus.VALIDATE
    <finra.filings.base_filing.BaseFilingOps.FilingStatus.VALIDATE>` with
    :py:meth:`FormU5.set_filing_status()
    <finra.filings.base_filing.BaseFilingOps.set_filing_status>`
    triggers a completeness check on the server-side, and provides
    success or error details via a subsequent request.
    
    Filings require setting a :py:class:`FilingType` using
    :py:meth:`FormU5.set_filing_type`. For example, to amend a filing, set
    :py:attr:`FilingType.AMENDMENT`. The ``individual_crd_number`` and
    ``date_of_birth`` are required for all submissions, and can be set using
    :py:meth:`FormU5.set_individual_crd_number` and
    :py:meth:`FormU5.set_date_of_birth`, respectively.
    
    There are two ways to file a Form U5 amendment:
    
      - by submitting the full U5 filing data with changes
      - by submitting operations
    
    To set the filing data, use :py:meth:`FormU5.set_filing_data()
    <finra.filings.base_filing.BaseFiling.set_filing_data>`. To amend or
    update filing data with an operation, use :py:meth:`FormU5.add_operation()
    <finra.filings.base_filing.BaseFilingOps.add_operation>`.
    If both filing data and operations are provided in a single call,
    operations will be ignored.
    
    See :py:meth:`BaseClient.form_U5_submission()
    <finra.base_client.BaseClient.form_u5_submission>`
    for details on the asynchronous submission process.
    
    Read more about the `Form U5
    <https://developer.finra.org/docs#submission_api-registration-u5>`__
    filing in the official API documentation.
    """
    
    @property
    def schema_url(self) -> str:
        """Form U5 schema URL"""
        return "https://schemas.api.finra.org/FINRAApiPlatformU5Filing.json"
    
    FilingType = FilingType
    
    def set_filing_type(self, filing_type: Optional[_FilingType]) -> Self:
        """
        Set the filing type for the filing
        
        :param filing_type: The filing type provided as an enum member
        """
        _set_filing_type(self, filing_type, self.FilingType)
        return self
    
    def clear_filing_type(self) -> None:
        """Clear the filing type"""
        self._metadata.set_filing_type(None)
        
    def set_individual_crd_number(
        self,
        individual_crd_number: Optional[int]
        ) -> Self:
        _set_individual_crd_number(self, individual_crd_number)
        return self
    
    set_individual_crd_number.__doc__ = _set_individual_crd_number.__doc__
    
    def clear_individual_crd_number(self) -> None:
        """Clear the Individual CRD Number"""
        self._metadata.set_individual_crd_number(None)
        
    def set_date_of_birth(self, date_of_birth: Optional[date]) -> Self:
        _set_date_of_birth(self, date_of_birth)
        return self
    
    set_date_of_birth.__doc__ = _set_date_of_birth.__doc__
    
    def clear_date_of_birth(self) -> None:
        """Clear the Date of Birth"""
        self._metadata.set_date_of_birth(None)
        
    def set_ignore_warnings(self, ignore_warning: bool) -> Self:
        """
        :param ignore_warning: Bypass the server-side warning(s) when filing
            POST submissions
        """
        self._metadata.set_ignore_warnings(True if ignore_warning else None)
        return self
    
    def clear_ignore_warnings(self) -> None:
        """Clear the ignore warnings setting"""
        self._metadata.set_ignore_warnings(None)
        
    def build(self) -> FilingDictType:
        """
        Build and return JSON object for submitting a Form U5 filing from the
        provided data and metadata
        """
        if self._metadata._filingType is None:
            raise ValueError("Must set filing type")
        
        if self._metadata._individualCrdNumber is None:
            raise ValueError("Must set Individual CRD Number")
        
        if self._metadata._dateOfBirth is None:
            raise ValueError("Must set Date of Birth")
        
        return super().build()

_add_require_enums_docs(FormU5)

