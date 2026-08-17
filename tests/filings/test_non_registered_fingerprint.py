import unittest

from finra.filings.non_registered_fingerprint import NonRegisteredFingerprint

from ..common import has_diff, no_duplicates
from .test_base_filing import INDIVIDUAL_CRD_NUMBER


class TestNonRegisteredFingerprint(unittest.TestCase):
    def setUp(self):
        self.filing = NonRegisteredFingerprint()
        self.filing.set_filing_type(self.filing.FilingType.INITIAL)
        self.metadata = {
            'filingStatus': 'submitted',
            'filingType': 'INITIAL',
            }
    
    
    #######################################################################
    # FILING STATUS
    
    @no_duplicates
    def test_set_non_submitted_filing_status(self):
        self.filing._metadata.set_filing_status("draft") # directly on metadata
        with self.assertRaisesRegex(
            ValueError, (
                "Non-Registered Fingerprint only supports 'submitted' filing "
                "status"
                )
            ):
            self.filing.build()
    
    
    #######################################################################
    # FILING TYPE
    
    @no_duplicates
    def test_set_filing_type(self):
        self.filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'}, # filing data required
            }}, self.filing.build()))
        
        self.filing.clear_filing_type()
        with self.assertRaisesRegex(ValueError, "Must set filing type"):
            self.filing.build()
        
    @no_duplicates
    def test_set_filing_type_none(self):
        self.filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'}, # filing data required
            }}, self.filing.build()))
        
        self.filing.set_filing_type(None) # same as clear
        with self.assertRaisesRegex(ValueError, "Must set filing type"):
            self.filing.build()
        
    @no_duplicates
    def test_set_wrong_filing_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "finra.filings.non_registered_fingerprint." \
            "NonRegisteredFingerprint.FilingType.INITIAL"
            ):
            self.filing.set_filing_type('INITIAL')
    
    
    #######################################################################
    # INDIVIDUAL CRD NUMBER
    
    @no_duplicates
    def test_set_individual_crd_number(self):
        self.filing.set_filing_type(self.filing.FilingType.AMENDMENT)
        self.filing.set_individual_crd_number(INDIVIDUAL_CRD_NUMBER)
        self.filing.set_filing_data({'data': '1'})
        self.metadata.update({
            'filingType': 'AMENDMENT',
            'individualCrdNumber': INDIVIDUAL_CRD_NUMBER,
            })
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'},
            }}, self.filing.build()))
        
        self.filing.clear_individual_crd_number()
        with self.assertRaisesRegex(
            ValueError,
            "Must set Individual CRD Number if filing type is not 'INITIAL'"
            ):
            self.filing.build()
        
    @no_duplicates
    def test_set_individual_crd_number_none(self):
        self.filing.set_filing_type(self.filing.FilingType.AMENDMENT)
        self.filing.set_individual_crd_number(INDIVIDUAL_CRD_NUMBER)
        self.filing.set_filing_data({'data': '1'})
        self.metadata.update({
            'filingType': 'AMENDMENT',
            'individualCrdNumber': INDIVIDUAL_CRD_NUMBER,
            })
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'},
            }}, self.filing.build()))
        
        self.filing.set_individual_crd_number(None) # same as clear
        with self.assertRaisesRegex(
            ValueError,
            "Must set Individual CRD Number if filing type is not 'INITIAL'"
            ):
            self.filing.build()
    
    
    #######################################################################
    # FILING DATA
    
    @no_duplicates
    def test_set_filing_data(self):
        self.filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'},
            }}, self.filing.build()))
        
        self.filing.clear_filing_data()
        with self.assertRaisesRegex(
            ValueError,
            "Filing data must be set even for amendments. Filing data " \
            "can also have just the delta changes for amendments."
            ):
            self.filing.build()
    
    @no_duplicates
    def test_set_filing_data_none(self):
        self.filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'},
            }}, self.filing.build()))
        
        self.filing.set_filing_data(None) # same as clear
        with self.assertRaisesRegex(
            ValueError,
            "Filing data must be set even for amendments. Filing data " \
            "can also have just the delta changes for amendments."
            ):
            self.filing.build()


###########################################################################
# ENUMS REQUIRED

class TestNonRegisteredFingerprintEnums(unittest.TestCase):
    
    @no_duplicates
    def test_enums_not_required(self):
        filing = NonRegisteredFingerprint()
        filing.set_require_enums(False)
        filing.set_filing_type('INITIAL')
        filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': {
                'filingStatus': 'submitted',
                'filingType': 'INITIAL',
                },
            'filingData': {'data': '1'},
            }}, filing.build()))

