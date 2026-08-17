from datetime import date, datetime

from ..common import has_diff, no_duplicates


DATE_OF_BIRTH = date(1969, 7, 20)

DATE_OF_BIRTH_ISO = '1969-07-20'

DATETIME = datetime(1969, 7, 20, 1, 2, 3)

INDIVIDUAL_CRD_NUMBER = 1234567


##############################################################################
# BASE FILING WITH OPERATIONS

# Mixin for testing filings with partial update operations and filing status
class _TestBaseFilingOps:
    
    
    #######################################################################
    # FILING TYPE
    
    @no_duplicates
    def test_set_filing_type(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_filing_type()
        with self.assertRaisesRegex(ValueError, "Must set filing type"):
            self.filing.build()
        
    @no_duplicates
    def test_set_filing_type_none(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_filing_type(None) # same as clear
        with self.assertRaisesRegex(ValueError, "Must set filing type"):
            self.filing.build()
    
    
    #######################################################################
    # FILING STATUS
    
    @no_duplicates
    def test_set_filing_status(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_filing_status()
        del self.metadata['filingStatus']
        with self.assertRaisesRegex(ValueError, "Must set filing status"):
            self.filing.build()
        
    @no_duplicates
    def test_set_filing_status_none(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_filing_status(None) # same as clear
        del self.metadata['filingStatus']
        with self.assertRaisesRegex(ValueError, "Must set filing status"):
            self.filing.build()
        
    @no_duplicates
    def test_set_wrong_filing_status_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "finra.filings.base_filing.BaseFilingOps.FilingStatus.SUBMITTED"
            ):
            self.filing.set_filing_status("submitted")
    
    
    #######################################################################
    # OPERATIONS
    
    @no_duplicates
    def test_add_operation(self):
        self.filing.add_operation(self.filing.Op.ADD, "path", "value")
        self.filing.add_operation(self.filing.Op.REPLACE, "path2", "value2")
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'operations': [
                {'op': 'add', 'path': '/path', 'value': 'value'},
                {'op': 'replace', 'path': '/path2', 'value': 'value2'},
                ],
            }}, self.filing.build()))
        
        self.filing.clear_operations()
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
    @no_duplicates
    def test_add_wrong_operation_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.filings.base_filing.BaseFilingOps.Op.ADD"
            ):
            self.filing.add_operation("add", "path", "value")
        
    @no_duplicates
    def test_add_operation_empty_path(self):
        with self.assertRaisesRegex(ValueError, "The path must be non-empty"):
            self.filing.add_operation(self.filing.Op.ADD, "", "value")
        
    @no_duplicates
    def test_add_operation_path_iterable(self):
        self.filing.add_operation(
            self.filing.Op.ADD,
            ["path", "to", ("collection", "element"), 1],
            "value"
            )
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'operations': [{
                'op': 'add',
                'path': '/path/to/[collection:element]/1',
                'value': 'value',
                }],
            }}, self.filing.build()))
        
    @no_duplicates
    def test_add_operation_bad_path_iterable(self):
        with self.assertRaisesRegex(
            ValueError,
            "To select an object in an array, a path " \
            "element must be a 2-element \\(<key>, <value>\\) " \
            "iterable representing the property to select."
            ): # escaped syntax for regex
            self.filing.add_operation(
                self.filing.Op.ADD,
                ["path", "to", ("bad collection id",)],
                "value"
                )
        
    @no_duplicates
    def test_replace_operation_missing_value(self):
        with self.assertRaisesRegex(
            ValueError,
            "Must provide a value if operation is 'add' or 'replace'"
            ):
            self.filing.add_operation(self.filing.Op.REPLACE, "path")
        
    @no_duplicates
    def test_remove_operation(self):
        self.filing.add_operation(self.filing.Op.REMOVE, "path")
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'operations': [{
                'op': 'remove',
                'path': '/path',
                }],
            }}, self.filing.build()))
        
    @no_duplicates
    def test_remove_operation_with_value(self):
        with self.assertRaisesRegex(
            ValueError, "A value is not allowed if operation is 'remove'"
            ):
            self.filing.add_operation(self.filing.Op.REMOVE, "path", "value")
    
    
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
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
    
    @no_duplicates
    def test_set_filing_data_none(self):
        self.filing.set_filing_data({'data': '1'})
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            'filingData': {'data': '1'},
            }}, self.filing.build()))
        
        self.filing.set_filing_data(None) # same as clear
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))


##############################################################################
# U4 / U5 TESTS

# Mixin for testing filings with individual CRD number, date of birth
class _TestU4U5:
    
    
    #######################################################################
    # INDIVIDUAL CRD NUMBER
    
    @no_duplicates
    def test_set_individual_crd_number(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_individual_crd_number()
        with self.assertRaisesRegex(
            ValueError, "Must set Individual CRD Number"
            ):
            self.filing.build()
        
    @no_duplicates
    def test_set_individual_crd_number_none(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_individual_crd_number(None) # same as clear
        with self.assertRaisesRegex(
            ValueError, "Must set Individual CRD Number"
            ):
            self.filing.build()
    
    
    #######################################################################
    # DATE OF BIRTH
    
    @no_duplicates
    def test_set_date_of_birth(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_date_of_birth()
        with self.assertRaisesRegex(ValueError, "Must set Date of Birth"):
            self.filing.build()
    
    @no_duplicates
    def test_set_date_of_birth_none(self):
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_date_of_birth(None) # same as clear
        with self.assertRaisesRegex(ValueError, "Must set Date of Birth"):
            self.filing.build()
        
    @no_duplicates
    def test_set_wrong_date_of_birth_type_string(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.filing.set_date_of_birth(DATE_OF_BIRTH_ISO)
        
    @no_duplicates
    def test_set_wrong_date_of_birth_type_datetime(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.filing.set_date_of_birth(DATETIME)
    
    
    #######################################################################
    # IGNORE WARNINGS
    
    @no_duplicates
    def test_set_ignore_warnings(self):
        self.filing.set_ignore_warnings(True)
        self.metadata['ignoreWarnings'] = True
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.clear_ignore_warnings()
        del self.metadata['ignoreWarnings']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
    @no_duplicates
    def test_set_ignore_warnings_false(self):
        self.filing.set_ignore_warnings(True)
        self.metadata['ignoreWarnings'] = True
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))
        
        self.filing.set_ignore_warnings(False) # same as clear
        del self.metadata['ignoreWarnings']
        self.assertFalse(has_diff({'filing': {
            'metadata': self.metadata,
            }}, self.filing.build()))

