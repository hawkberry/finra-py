import unittest

from finra.filings.create_individual import CreateIndividual

from ..common import has_diff, no_duplicates


class TestCreateIndividual(unittest.TestCase):
    def setUp(self):
        self.filing = CreateIndividual()
        self.metadata = {'filingStatus': 'submitted'}
        
    
    #######################################################################
    # FILING STATUS
    
    @no_duplicates
    def test_set_non_submitted_filing_status(self):
        self.filing._metadata.set_filing_status("draft") # directly on metadata
        with self.assertRaisesRegex(
            ValueError,
            "Create Individual only supports 'submitted' filing status"
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
        with self.assertRaisesRegex(ValueError, "Must set filing data"):
            self.filing.build()
    
    @no_duplicates
    def test_set_filing_data_none(self):
        self.filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'},
            }}, self.filing.build()))
        
        self.filing.set_filing_data(None) # same as clear
        with self.assertRaisesRegex(ValueError, "Must set filing data"):
            self.filing.build()


###########################################################################
# ENUMS REQUIRED

class TestCreateIndividualEnums(unittest.TestCase):
    
    @no_duplicates
    def test_enums_not_required(self):
        filing = CreateIndividual()
        filing.set_require_enums(False)
        filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': {'filingStatus': 'submitted'},
            'filingData': {'data': '1'},
            }}, filing.build()))

