from enum import Enum
from typing import Optional, Self, TypeAlias

from ..enum_converter import _add_require_enums_docs, EnumStr
from .base_filing import (
    BaseFiling, FilingDictType, _set_filing_type, _set_individual_crd_number,
    )


__all__ = ["NonRegisteredFingerprint"]


class FilingType(Enum):
    """
    Used in a filing to set the filing type.
    See :py:meth:`NonRegisteredFingerprint.set_filing_type`.
    """
    __skip_module_autodoc__ = True
    
    INITIAL = "INITIAL"
    
    AMENDMENT = "AMENDMENT"


_FilingType: TypeAlias = EnumStr[FilingType]


class NonRegisteredFingerprint(BaseFiling):
    """
    Create a Non-Registered Fingerprint record to submit to FINRA.
    
    The `Composite Individual <https://developer.finra.org/
    docs#query_api-registration-composite_individual>`__
    dataset can be used as a reference for creating filings and amendments.
    
    This class can be used to:
    
      - wrap filing data with the correct metadata
      - validate filing data against the schema on the client-side, prior to
        submission
    
    This class cannot be used to:
    
      - build or pre-fill filing data directly
      - amend or update filing data via operations
    
    The filing status is always in ``submitted`` mode. Draft submissions are
    not accepted for this submission type, and server-side validation is not
    supported.
    
    Filings must adhere to the `Non-Registered Fingerprint schema
    <https://schemas.api.finra.org/FINRAApiPlatformNRFFiling.json>`__.
    
    The :py:class:`FilingType` must be set using
    :py:meth:`NonRegisteredFingerprint.set_filing_type`. For example, to amend
    a filing, set :py:attr:`FilingType.AMENDMENT`. Filing data must be set even
    for amendments, or it can have just the delta changes for an amendment.
    
    There are two ways to file a Non-Registered Fingerprint amendment:
    
      - by submitting the full filing data with changes
      - by submitting only the delta changes as filing data
    
    If an individual has an Individual CRD Number, it must be set using
    :py:meth:`NonRegisteredFingerprint.set_individual_crd_number`. If an
    initial filing is submitted for a new individual without an Individual CRD
    Number, a new Individual CRD Number is automatically created.
    
    See :py:meth:`BaseClient.non_registered_fingerprint_submission()
    <finra.base_client.BaseClient.non_registered_fingerprint_submission>`
    for details on the asynchronous submission process.
    
    Read more about the `Non-Registered Fingerprint
    <https://developer.finra.org/docs#submission_api-registration-nrf>`__
    filing in the official API documentation.
    """
    
    def __init__(self, *, require_enums: bool=True):
        super().__init__(require_enums)
        self._metadata.set_filing_status("submitted")
        
    @property
    def schema_url(self) -> str:
        """Non Registered Fingerprint schema URL"""
        return "https://schemas.api.finra.org/FINRAApiPlatformNRFFiling.json"
    
    FilingType = FilingType
    
    def set_filing_type(
        self,
        filing_type: Optional[_FilingType]
        ) -> Self:
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
        
    def build(self) -> FilingDictType:
        """
        Build and return JSON object for submitting a Non-Registered
        Fingerprint record from the provided data and metadata
        """
        if self._metadata._filingStatus != "submitted":
            raise ValueError(
                "Non-Registered Fingerprint only supports 'submitted' filing "
                "status"
                )
        
        if self._metadata._filingType is None:
            raise ValueError("Must set filing type")
        
        if (self._metadata._filingType != "INITIAL"
            and self._metadata._individualCrdNumber is None):
            raise ValueError(
                "Must set Individual CRD Number if filing type is not "
                "'INITIAL'"
                )
        if self._filingData is None:
            raise ValueError(
                "Filing data must be set even for amendments. Filing data "
                "can also have just the delta changes for amendments."
                )
        
        return super().build()

_add_require_enums_docs(NonRegisteredFingerprint)

