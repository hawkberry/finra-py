import unittest

from finra.filings.form_u4 import FormU4

from ..common import has_diff, no_duplicates
from .test_base_filing import (
    DATE_OF_BIRTH, DATE_OF_BIRTH_ISO, INDIVIDUAL_CRD_NUMBER,
    _TestBaseFilingOps, _TestU4U5,
    )


class TestFormU4(_TestBaseFilingOps, _TestU4U5, unittest.TestCase):
    def setUp(self):
        self.filing = FormU4()
        self.filing.set_filing_status(self.filing.FilingStatus.SUBMITTED)
        self.filing.set_filing_type(self.filing.FilingType.INITIAL)
        self.filing.set_individual_crd_number(INDIVIDUAL_CRD_NUMBER)
        self.filing.set_date_of_birth(DATE_OF_BIRTH)
        self.metadata = {
            'filingStatus': 'submitted',
            'filingType': 'INITIAL',
            'individualCrdNumber': INDIVIDUAL_CRD_NUMBER,
            'dateOfBirth': DATE_OF_BIRTH_ISO,
            }
    
    
    #######################################################################
    # FILING TYPE
    
    @no_duplicates
    def test_set_wrong_filing_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.filings.form_u4.FormU4.FilingType.INITIAL"
            ):
            self.filing.set_filing_type('INITIAL')
    
    
    #######################################################################
    # REP ACCESS
    
    @no_duplicates
    def test_set_rep_access(self):
        self.filing.set_rep_access(
            self.filing.RepAccessType.PARTIAL,
            False, True, False, True, False, True, False
            )
        self.metadata['repAccess'] = {
            'accessType': 'partial',
            'individualInformation': False,
            'employmentInformation': True,
            'registrationRequests': False,
            'dualRegistration': True,
            'examsInformation': False,
            'professionalDesignations': True,
            'disclosures': False,
            }
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_rep_access()
        del self.metadata['repAccess']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
    
    @no_duplicates
    def test_set_rep_access_with_optional_params(self):
        self.filing.set_rep_access(
            self.filing.RepAccessType.PARTIAL,
            False, True, False, True, False, True, False, True, False, True
            )
        self.metadata['repAccess'] = {
            'accessType': 'partial',
            'individualInformation': False,
            'employmentInformation': True,
            'registrationRequests': False,
            'dualRegistration': True,
            'examsInformation': False,
            'professionalDesignations': True,
            'disclosures': False,
            'eSignature': True,
            'signatures': False,
            'editNotification': True,
            }
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_rep_access()
        del self.metadata['repAccess']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
    @no_duplicates
    def test_set_rep_access_none(self):
        self.filing.set_rep_access(
            self.filing.RepAccessType.PARTIAL,
            False, True, False, True, False, True, False
            )
        self.metadata['repAccess'] = {
            'accessType': 'partial',
            'individualInformation': False,
            'employmentInformation': True,
            'registrationRequests': False,
            'dualRegistration': True,
            'examsInformation': False,
            'professionalDesignations': True,
            'disclosures': False,
            }
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_rep_access(None) # same as clear
        del self.metadata['repAccess']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
    @no_duplicates
    def test_set_wrong_rep_access_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.filings.form_u4.FormU4.RepAccessType.PARTIAL"
            ):
            self.filing.set_rep_access('partial')
        
    
    #######################################################################
    # REP COMPLETION STATUS
    
    @no_duplicates
    def test_set_rep_completion_status(self):
        self.filing.set_rep_completion_status(True)
        self.metadata['repCompletionStatus'] = 'E_SIGN_AVAILABLE'
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_rep_completion_status()
        del self.metadata['repCompletionStatus']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
    @no_duplicates
    def test_set_rep_completion_status_false(self):
        self.filing.set_rep_completion_status(True)
        self.metadata['repCompletionStatus'] = 'E_SIGN_AVAILABLE'
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_rep_completion_status(False)
        self.metadata['repCompletionStatus'] = 'NOT_AVAILABLE'
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_rep_completion_status(None) # same as clear
        del self.metadata['repCompletionStatus']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))


###########################################################################
# ENUMS REQUIRED

class TestFormU4Enums(unittest.TestCase):
    
    @no_duplicates
    def test_enums_not_required(self):
        filing = FormU4()
        filing.set_require_enums(False)
        filing.set_filing_status('submitted')
        filing.set_filing_type('INITIAL')
        filing.set_individual_crd_number(INDIVIDUAL_CRD_NUMBER)
        filing.set_date_of_birth(DATE_OF_BIRTH)
        filing.set_rep_access('partial')
        filing.add_operation("add", "path", "value")
        
        self.assertFalse(has_diff({'filing': {
            'metadata': {
                'filingStatus': 'submitted',
                'filingType': 'INITIAL',
                'individualCrdNumber': INDIVIDUAL_CRD_NUMBER,
                'dateOfBirth': DATE_OF_BIRTH_ISO,
                'repAccess': {
                    'accessType': 'partial',
                    'individualInformation': False,
                    'employmentInformation': False,
                    'registrationRequests': False,
                    'dualRegistration': False,
                    'examsInformation': False,
                    'professionalDesignations': False,
                    'disclosures': False,
                    },
                },
            'operations': [{'op': 'add', 'path': '/path', 'value': 'value'}],
            }}, filing.build()))

