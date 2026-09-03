import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from finra.client import Client
from finra.filters import Filter

from .common import has_diff, no_duplicates


DATE = date(2026, 1, 2)
DATE_PLUS_1_DAY = date(2026, 1, 3)

DATE_ISO = '2026-01-02'
DATE_PLUS_1_DAY_ISO = '2026-01-03'

DATETIME_TRUNCATED = datetime(2026, 1, 2)
DATETIME_TRUNCATED_PLUS_1_DAY = datetime(2026, 1, 3)

DATETIME_TRUNCATED_ISO = '2026-01-02 00:00:00.000'
DATETIME_TRUNCATED_PLUS_1_DAY_ISO = '2026-01-03 00:00:00.000'
DATETIME_TRUNCATED_ISO_CONVERTED_TO_ET = '2026-01-01 19:00:00.000'


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.enum = Client.ConsolidatedShortInterest
        self.filter = Filter(self.enum)
        
    
    #######################################################################
    # Compare
    
    @no_duplicates
    def test_add_compare(self):
        self.filter.add_compare(self.enum.SETTLEMENT_DATE, DATE_ISO)
        self.assertFalse(has_diff({'compareFilters': [{
            'fieldName': 'settlementDate',
            'fieldValue': DATE_ISO,
            'compareType': 'EQUAL',
            }]}, self.filter.build()))
        
        self.filter.clear_compare()
        self.assertFalse(has_diff({}, self.filter.build()))
        
    @no_duplicates
    def test_add_compare_date_value(self):
        self.filter.add_compare(self.enum.SETTLEMENT_DATE, DATE)
        self.assertFalse(has_diff({'compareFilters': [{
            'fieldName': 'settlementDate',
            'fieldValue': DATE_ISO,
            'compareType': 'EQUAL',
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_compare_datetime_value_without_zoneinfo(self):
        self.filter.add_compare(self.enum.SETTLEMENT_DATE, DATETIME_TRUNCATED)
        self.assertFalse(has_diff({'compareFilters': [{
            'fieldName': 'settlementDate',
            'fieldValue': DATETIME_TRUNCATED_ISO,
            'compareType': 'EQUAL',
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_compare_datetime_value_with_zoneinfo(self):
        dt = DATETIME_TRUNCATED.replace(tzinfo=ZoneInfo('UTC'))
        self.filter.add_compare(self.enum.SETTLEMENT_DATE, dt)
        self.assertFalse(has_diff({'compareFilters': [{
            'fieldName': 'settlementDate',
            'fieldValue': DATETIME_TRUNCATED_ISO_CONVERTED_TO_ET,
            'compareType': 'EQUAL',
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_compare_with_compare_type(self):
        self.filter.add_compare(
            self.enum.SETTLEMENT_DATE,
            DATE_ISO,
            self.filter.CompareType.GREATER
            )
        self.assertFalse(has_diff({'compareFilters': [{
            'fieldName': 'settlementDate',
            'fieldValue': DATE_ISO,
            'compareType': 'GREATER',
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_compare_wrong_field_type(self):
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.ConsolidatedShortInterest."
                "SETTLEMENT_DATE"
                )
            ):
            self.filter.add_compare('settlementDate', DATE_ISO)
        
    @no_duplicates
    def test_add_compare_wrong_compare_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.filters.Filter.CompareType.EQUAL"
            ):
            self.filter.add_compare(
                self.enum.SETTLEMENT_DATE, DATE_ISO, 'EQUAL'
                )
        
    @no_duplicates
    def test_add_compare_enums_not_required(self):
        self.filter.set_require_enums(False)
        self.filter.add_compare('settlementDate', DATE_ISO, 'EQUAL')
        self.assertFalse(has_diff({'compareFilters': [{
            'fieldName': 'settlementDate',
            'fieldValue': DATE_ISO,
            'compareType': 'EQUAL',
            }]}, self.filter.build()))
        
        
    #######################################################################
    # Date Range
    
    @no_duplicates
    def test_add_date_range(self):
        self.filter.add_date_range(
            self.enum.SETTLEMENT_DATE, DATE, DATE_PLUS_1_DAY
            )
        self.filter.add_date_range(
            self.enum.SETTLEMENT_DATE, DATE, DATE_PLUS_1_DAY
            ) # add another filter
        
        date_range_filter = {
            'fieldName': 'settlementDate',
            'startDate': DATE_ISO,
            'endDate': DATE_PLUS_1_DAY_ISO,
            }
        self.assertFalse(has_diff(
            {'dateRangeFilters': [date_range_filter, date_range_filter]},
            self.filter.build()
            ))
        
        self.filter.clear_date_range()
        self.assertFalse(has_diff({}, self.filter.build()))
        
    @no_duplicates
    def test_add_date_range_datetime_value(self):
        self.filter.add_date_range(
            self.enum.SETTLEMENT_DATE,
            DATETIME_TRUNCATED,
            DATETIME_TRUNCATED_PLUS_1_DAY
            )
        self.assertFalse(has_diff({'dateRangeFilters': [{
            'fieldName': 'settlementDate',
            'startDate': DATETIME_TRUNCATED_ISO,
            'endDate': DATETIME_TRUNCATED_PLUS_1_DAY_ISO,
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_date_range_wrong_start_date_type(self):
        with self.assertRaisesRegex(
            TypeError, "datetime.date, datetime.datetime"
            ):
            self.filter.add_date_range(
                self.enum.SETTLEMENT_DATE, DATE_ISO, DATE_PLUS_1_DAY
                )
        
    @no_duplicates
    def test_add_date_range_wrong_end_date_type(self):
        with self.assertRaisesRegex(
            TypeError, "datetime.date, datetime.datetime"
            ):
            self.filter.add_date_range(
                self.enum.SETTLEMENT_DATE, DATE, DATE_PLUS_1_DAY_ISO
                )
        
    @no_duplicates
    def test_add_date_range_wrong_field_type(self):
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.ConsolidatedShortInterest."
                "SETTLEMENT_DATE"
                )
            ):
            self.filter.add_date_range('settlementDate', DATE, DATE_PLUS_1_DAY)
        
    @no_duplicates
    def test_add_date_range_enums_not_required(self):
        self.filter.set_require_enums(False)
        self.filter.add_date_range('settlementDate', DATE, DATE_PLUS_1_DAY)
        self.assertFalse(has_diff({'dateRangeFilters': [{
            'fieldName': 'settlementDate',
            'startDate': DATE_ISO,
            'endDate': DATE_PLUS_1_DAY_ISO,
            }]}, self.filter.build()))
        
    
    #######################################################################
    # Add Domain
    
    @no_duplicates
    def test_add_domain(self):
        self.filter.add_domain(self.enum.SETTLEMENT_DATE, DATE_ISO)
        self.filter.add_domain(self.enum.SETTLEMENT_DATE, DATE_ISO) # another
        
        domain_filter = {
            'fieldName': 'settlementDate',
            'values': [DATE_ISO],
            }
        self.assertFalse(has_diff(
            {'domainFilters': [domain_filter, domain_filter]},
            self.filter.build()
            ))
        
        self.filter.clear_domain()
        self.assertFalse(has_diff({}, self.filter.build()))
        
    @no_duplicates
    def test_add_domain_date_value(self):
        self.filter.add_domain(self.enum.SETTLEMENT_DATE, DATE)
        self.assertFalse(has_diff({'domainFilters': [{
            'fieldName': 'settlementDate',
            'values': [DATE_ISO],
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_domain_datetime_value(self):
        self.filter.add_domain(self.enum.SETTLEMENT_DATE, DATETIME_TRUNCATED)
        self.assertFalse(has_diff({'domainFilters': [{
            'fieldName': 'settlementDate',
            'values': [DATETIME_TRUNCATED_ISO],
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_domain_repeat_iterable(self):
        self.filter.add_domain(self.enum.SETTLEMENT_DATE, [DATE_ISO, DATE_ISO])
        self.assertFalse(has_diff({'domainFilters': [{
            'fieldName': 'settlementDate',
            'values': [DATE_ISO],
            }]}, self.filter.build()))
        
    @no_duplicates
    def test_add_domain_wrong_field_type(self):
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.ConsolidatedShortInterest."
                "SETTLEMENT_DATE"
                )
            ):
            self.filter.add_domain('settlementDate', DATE_ISO)
        
    @no_duplicates
    def test_add_domain_enums_not_required(self):
        self.filter.set_require_enums(False)
        self.filter.add_domain('settlementDate', DATE_ISO)
        self.assertFalse(has_diff({'domainFilters': [{
            'fieldName': 'settlementDate',
            'values': [DATE_ISO],
            }]}, self.filter.build()))
    

if __name__ == "__main__": # pragma: no cover
    unittest.main()
