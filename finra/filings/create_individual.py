from ..enum_converter import _add_require_enums_docs
from .base_filing import BaseFiling, FilingDictType


__all__ = ["CreateIndividual"]


class CreateIndividual(BaseFiling):
    """
    Create the initial registration record of an individual to submit to FINRA,
    which will include the generation of an Individual CRD number.
    
    This class can be used to:
    
      - wrap filing data with the correct metadata
      - validate filing data against the schema on the client-side, prior to
        submission
    
    This class cannot be used to:
    
      - build or pre-fill filing data directly
      - amend or update filing data
    
    The filing status is always in ``submitted`` mode. Draft submissions are
    not accepted for this submission type, and server-side validation is not
    supported.
    
    Filings must adhere to the `Create Individual schema
    <https://schemas.api.finra.org/FINRAAPIPlatformCreateIndividual.json>`__.
    
    Full registration data must be provided, and it cannot be amended or
    updated.
    
    See :py:meth:`BaseClient.create_individual_submission()
    <finra.base_client.BaseClient.create_individual_submission>`
    for details on the synchronous submission process.
    
    Read more about the `Create Individual <https://developer.finra.org/
    docs#submission_api-registration-create_individual>`__
    filing in the official API documentation.
    """
    
    def __init__(self, *, require_enums: bool=True):
        super().__init__(require_enums)
        self._metadata.set_filing_status("submitted")
        
    @property
    def schema_url(self) -> str:
        """Create Individual schema URL"""
        return (
            "https://schemas.api.finra.org/"
            "FINRAAPIPlatformCreateIndividual.json"
            )
    
    def build(self) -> FilingDictType:
        """
        Build and return JSON object for submitting a Create Individual
        registration record from the provided data and metadata
        """
        if self._metadata._filingStatus != "submitted":
            raise ValueError(
                "Create Individual only supports 'submitted' filing status"
                )
        
        if self._filingData is None:
            raise ValueError("Must set filing data")
        
        return super().build()

_add_require_enums_docs(CreateIndividual)

