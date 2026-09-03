from enum import Enum
from typing import Optional, Self, TypeAlias

from ..enum_converter import _add_require_enums_docs, EnumStr
from .base_filing import BaseFilingOps, FilingDictType, _set_filing_type


__all__ = ["FormBR"]


class FilingType(Enum):
    """
    Used in a filing to set the filing type.
    See :py:meth:`FormBR.set_filing_type`.
    """
    __skip_module_autodoc__ = True
    
    INITIAL = "INITIAL"
    
    AMENDMENT = "AMENDMENT"
    
    CLOSURE = "CLOSURE"
    
    WITHDRAW = "WITHDRAW"
    
    CLOSUREWITHDRAW = "CLOSUREWITHDRAW"


_FilingType: TypeAlias = EnumStr[FilingType]


class FormBR(BaseFilingOps):
    """
    Form BR is used to register a branch office with FINRA, the New York
    Stock Exchange (NYSE), and States that require branch registration.
    
    The `Composite Branch
    <https://developer.finra.org/
    docs#query_api-registration-composite_branch>`__ dataset provides branch
    registration data that can used to populate Form BR fields when submitting
    a filing.
    
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
    :py:meth:`FormBR.set_filing_status()
    <finra.filings.base_filing.BaseFilingOps.set_filing_status>`.
    
    Filings must adhere to the `BR schema
    <https://schemas.api.finra.org/FINRAApiPlatformBRFiling.json>`__. Setting
    :py:attr:`FilingStatus.VALIDATE
    <finra.filings.base_filing.BaseFilingOps.FilingStatus.VALIDATE>` with
    :py:meth:`FormBR.set_filing_status()
    <finra.filings.base_filing.BaseFilingOps.set_filing_status>`
    triggers a completeness check on the server-side, and provides
    success or error details via a subsequent request.
    
    Filings require setting a :py:class:`FilingType` using
    :py:meth:`FormBR.set_filing_type`. For example, to amend a filing,
    set :py:attr:`FilingType.AMENDMENT`.
    
    There are two ways to file a Form BR amendment:
    
      - by submitting the full BR filing data with changes
      - by submitting operations
    
    To set the filing data, use :py:meth:`FormBR.set_filing_data()
    <finra.filings.base_filing.BaseFiling.set_filing_data>`. To amend or
    update filing data with an operation, use :py:meth:`FormBR.add_operation()
    <finra.filings.base_filing.BaseFilingOps.add_operation>`.
    If both filing data and operations are provided in a single call,
    operations will be ignored.
    
    See :py:meth:`BaseClient.form_br_submission()
    <finra.base_client.BaseClient.form_br_submission>`
    for details on the asynchronous submission process.
    
    Read more about the `Form BR
    <https://developer.finra.org/docs#submission_api-registration-br>`__
    filing in the official API documentation.
    """
    
    @property
    def schema_url(self) -> str:
        """Form BR schema URL"""
        return "https://schemas.api.finra.org/FINRAApiPlatformBRFiling.json"
    
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
        
    def build(self) -> FilingDictType:
        """
        Build and return JSON object for submitting a Form BR filing from the
        provided data and metadata
        """
        if self._metadata._filingType is None:
            raise ValueError("Must set filing type")
        
        return super().build()

_add_require_enums_docs(FormBR)

