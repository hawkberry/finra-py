import unittest

from finra.filings.form_br import FormBR

from ..common import has_diff, no_duplicates
from .test_base_filing import _TestBaseFilingOps


class TestFormBR(_TestBaseFilingOps, unittest.TestCase):
    def setUp(self):
        self.filing = FormBR()
        self.filing.set_filing_status(self.filing.FilingStatus.SUBMITTED)
        self.filing.set_filing_type(self.filing.FilingType.INITIAL)
        self.metadata = {
            'filingStatus': 'submitted',
            'filingType': 'INITIAL',
            }
    
    
    #######################################################################
    # FILING TYPE
    
    @no_duplicates
    def test_set_wrong_filing_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.filings.form_br.FormBR.FilingType.INITIAL"
            ):
            self.filing.set_filing_type('INITIAL')


###########################################################################
# ENUMS REQUIRED

class TestFormBREnums(unittest.TestCase):
    
    @no_duplicates
    def test_enums_not_required(self):
        filing = FormBR()
        filing.set_require_enums(False)
        filing.set_filing_status('submitted')
        filing.set_filing_type('INITIAL')
        filing.add_operation("add", "path", "value")
        
        self.assertFalse(has_diff({'filing': {
            'metadata': {
                'filingStatus': 'submitted',
                'filingType': 'INITIAL',
                },
            'operations': [{'op': 'add', 'path': '/path', 'value': 'value'}],
            }}, filing.build()))

