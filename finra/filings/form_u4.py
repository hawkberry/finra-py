from datetime import date
from enum import Enum
from typing import Optional, Self, TypeAlias

from ..enum_converter import _add_require_enums_docs, EnumStr
from .base_filing import (
    BaseFilingOps, FilingDictType, _set_filing_type,
    _set_individual_crd_number, _set_date_of_birth,
    )


__all__ = ["FormU4"]


class FilingType(Enum):
    """
    Used in a filing to set the filing type.
    See :py:meth:`FormU4.set_filing_type`.
    """
    __skip_module_autodoc__ = True
    
    #: Amendment
    AMENDMENT = "AMENDMENT"
    
    #: Concurrence
    CONCURRENCE = "CONCURRENCE"
    
    #: Conversion
    CONVERSION = "CONVERSION"
    
    #: Dual
    DUAL = "DUAL"
    
    #: Initial
    INITIAL = "INITIAL"
    
    #: Page 2 BD Amendment
    P2BDAMEND = "P2BDAMEND"
    
    #: Page 2 BD Initial
    P2BINITIAL = "P2BDINITIAL"
    
    #: Relicense All
    RELICENSE = "RELICENSE"
    
    #: Relicense CRD
    RELICENSEBD = "RELICENSEBD"
    
    #: Relicense IA
    RELICENSEIA = "RELICENSEIA"


_FilingType: TypeAlias = EnumStr[FilingType]


class RepAccessType(Enum):
    """
    Used to indicate whether or not rep access is required in FINPRO. See
    :py:meth:`FormU4.set_rep_access`.
    """
    __skip_module_autodoc__ = True
    
    PARTIAL = "partial"
    
    FULL = "full"
    
    NONE = "none"


_RepAccessType: TypeAlias = EnumStr[RepAccessType]


class FormU4(BaseFilingOps):
    """
    Form U4 is used to register representatives of broker-dealers and
    investment advisers with the applicable jurisdictions and/or SROs.
    
    The :py:meth:`BaseClient.get_u4_form_prefill()
    <finra.base_client.BaseClient.get_u4_form_prefill>` dataset provides
    individual registration data that can be used to populate Form U4 fields
    when submitting a filing with :py:attr:`FilingType.INITIAL`. The dataset's
    response has the same format as the Form U4 initial filing.
    
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
    :py:meth:`FormU4.set_filing_status()
    <finra.filings.base_filing.BaseFilingOps.set_filing_status>`.
    
    Filings must adhere to the `U4 schema
    <https://schemas.api.finra.org/FINRAApiPlatformU4Filing.json>`__. Setting
    :py:attr:`FilingStatus.VALIDATE
    <finra.filings.base_filing.BaseFilingOps.FilingStatus.VALIDATE>` with
    :py:meth:`FormU4.set_filing_status()
    <finra.filings.base_filing.BaseFilingOps.set_filing_status>`
    triggers a completeness check on the server-side, and provides
    success or error details via a subsequent request.
    
    Filings require setting a :py:class:`FilingType` using
    :py:meth:`FormU4.set_filing_type`. For example, to amend a filing, set
    :py:attr:`FilingType.AMENDMENT`. The ``individual_crd_number`` and
    ``date_of_birth`` are required for all submissions, and can be set using
    :py:meth:`FormU4.set_individual_crd_number` and
    :py:meth:`FormU4.set_date_of_birth`, respectively.
    
    There are two ways to file a Form U4 amendment:
    
      - by submitting the full U4 filing data with changes
      - by submitting operations
    
    To set the filing data, use :py:meth:`FormU4.set_filing_data()
    <finra.filings.base_filing.BaseFiling.set_filing_data>`. To amend or
    update filing data with an operation, use :py:meth:`FormU4.add_operation()
    <finra.filings.base_filing.BaseFilingOps.add_operation>`.
    If both filing data and operations are provided in a single call,
    operations will be ignored.
    
    Form U4 submission supports Rep Edit and Rep Signature via FINRPO. If a U4
    requires Rep Edit or Rep Signature, it must be sent in a draft mode and the
    final submission must be made via the `FINRA Gateway
    <https://gateway.finra.org/>`__.
    
    See :py:meth:`BaseClient.form_u4_submission()
    <finra.base_client.BaseClient.form_u4_submission>`
    for details on the asynchronous submission process.
    
    Read more about the `Form U4
    <https://developer.finra.org/docs#submission_api-registration-u4>`__
    filing in the official API documentation.
    """
    
    @property
    def schema_url(self) -> str:
        """Form U4 schema URL"""
        return "https://schemas.api.finra.org/FINRAApiPlatformU4Filing.json"
    
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
    
    RepAccessType = RepAccessType
    
    def set_rep_access(
        self,
        rep_access_type: Optional[_RepAccessType],
        individual_information: bool=False,
        employment_information: bool=False,
        registration_requests: bool=False,
        dual_registration: bool=False,
        exams_information: bool=False,
        professional_designations: bool=False,
        disclosures: bool=False,
        e_signature: Optional[bool]=None,
        signatures: Optional[bool]=None,
        edit_notification: Optional[bool]=None
        ) -> Self:
        """
        This setting indicates whether or not rep access is required in FINPRO.
        Take care to appropriately configure access for the following sections,
        by setting a section value to True. The default for all sections is
        False.
        
        :param rep_access_type: The type of rep access required in FINPRO
            provided as an enum member
        :param individual_information: Required setting
        :param employment_information: Required setting
        :param registration_requests: Required setting
        :param dual_registration: Required setting
        :param exams_information: Required setting
        :param professional_designations: Required setting
        :param disclosures: Required setting
        :param e_signature: Setting this to ``True`` enables the E-signature
            workflow. This is only applicable when Rep Edit and E-signature
            need to be combined or when both must be obtained from the Rep at
            the same time.
        :param signatures: Setting to ``True`` gives the Rep access to edit the
            signatures section of the form. This is only applicable when Rep
            Edit and E-signature need to be combined, or when both must be
            obtained from the Rep at the same time.
        :param edit_notification: Setting to ``True`` enables notification that
            gets sent to Rep when Rep Access is enabled
        """
        if rep_access_type is None:
            self._metadata.set_rep_access(None)
        else:
            rep_access = {
                "accessType": self._convert(
                    rep_access_type, self.RepAccessType
                    ),
                "individualInformation": individual_information,
                "employmentInformation": employment_information,
                "registrationRequests": registration_requests,
                "dualRegistration": dual_registration,
                "examsInformation": exams_information,
                "professionalDesignations": professional_designations,
                "disclosures": disclosures,
                }
            if e_signature is not None:
                rep_access["eSignature"] = e_signature
            if signatures is not None:
                rep_access["signatures"] = signatures
            if edit_notification is not None:
                rep_access["editNotification"] = edit_notification
            self._metadata.set_rep_access(rep_access)
        return self
    
    def clear_rep_access(self) -> None:
        """Clear the rep access setting"""
        self._metadata.set_rep_access(None)
        
    def set_rep_completion_status(
        self,
        e_sign_available: Optional[bool]
        ) -> Self:
        """
        Set the rep completion status for the filing indicating whether to make
        E-signature available for individual Rep via the FINPRO UI
        
        :param e_sign_available: ``True`` to make E-signature available,
            ``False`` to make E-signature unavailable, or ``None`` to clear the
            rep completion status for this submission
        """
        if e_sign_available is None:
            self._metadata.set_rep_completion_status(None)
        else:
            self._metadata.set_rep_completion_status(
                "E_SIGN_AVAILABLE" if e_sign_available else "NOT_AVAILABLE"
                )
        return self
    
    def clear_rep_completion_status(self) -> None:
        """Clear the rep completion status setting"""
        self._metadata.set_rep_completion_status(None)
        
    def set_ignore_warnings(self, ignore_warning: Optional[bool]) -> Self:
        """
        :param ignore_warning: Suppress server-side warning(s) about submitting
            potentially sensitive information when filing POST submissions
        """
        self._metadata.set_ignore_warnings(True if ignore_warning else None)
        return self
    
    def clear_ignore_warnings(self) -> None:
        """Clear the ignore warnings setting"""
        self._metadata.set_ignore_warnings(None)
        
    def build(self) -> FilingDictType:
        """
        Build and return JSON object for submitting a Form U4 filing from the
        provided data and metadata
        """
        if self._metadata._filingType is None:
            raise ValueError("Must set filing type")
        
        if self._metadata._individualCrdNumber is None:
            raise ValueError("Must set Individual CRD Number")
        
        if self._metadata._dateOfBirth is None:
            raise ValueError("Must set Date of Birth")
        
        return super().build()

_add_require_enums_docs(FormU4)

