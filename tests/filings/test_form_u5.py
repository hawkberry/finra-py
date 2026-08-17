import unittest

from finra.filings.form_u5 import FormU5

from ..common import has_diff, no_duplicates
from .test_base_filing import (
    DATE_OF_BIRTH, DATE_OF_BIRTH_ISO, INDIVIDUAL_CRD_NUMBER,
    _TestBaseFilingOps, _TestU4U5,
    )


class TestFormU5(_TestBaseFilingOps, _TestU4U5, unittest.TestCase):
    def setUp(self):
        self.filing = FormU5()
        self.filing.set_filing_status(self.filing.FilingStatus.SUBMITTED)
        self.filing.set_filing_type(self.filing.FilingType.FULL)
        self.filing.set_individual_crd_number(INDIVIDUAL_CRD_NUMBER)
        self.filing.set_date_of_birth(DATE_OF_BIRTH)
        self.metadata = {
            'filingStatus': 'submitted',
            'filingType': 'FULL',
            'individualCrdNumber': INDIVIDUAL_CRD_NUMBER,
            'dateOfBirth': DATE_OF_BIRTH_ISO,
            }
    
    
    #######################################################################
    # FILING TYPE
    
    @no_duplicates
    def test_set_wrong_filing_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.filings.form_u5.FormU5.FilingType.FULL"
            ):
            self.filing.set_filing_type('FULL')


###########################################################################
# ENUMS REQUIRED

class TestFormU5Enums(unittest.TestCase):
    
    @no_duplicates
    def test_enums_not_required(self):
        filing = FormU5()
        filing.set_require_enums(False)
        filing.set_filing_status('submitted')
        filing.set_filing_type('FULL')
        filing.set_individual_crd_number(INDIVIDUAL_CRD_NUMBER)
        filing.set_date_of_birth(DATE_OF_BIRTH)
        filing.add_operation("add", "path", "value")
        
        self.assertFalse(has_diff({'filing': {
            'metadata': {
                'filingStatus': 'submitted',
                'filingType': 'FULL',
                'individualCrdNumber': INDIVIDUAL_CRD_NUMBER,
                'dateOfBirth': DATE_OF_BIRTH_ISO,
                },
            'operations': [{'op': 'add', 'path': '/path', 'value': 'value'}],
            }}, filing.build()))

