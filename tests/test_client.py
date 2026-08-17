import asyncio
import datetime
import inspect
import json
import logging
import unittest
from enum import EnumType
from typing import Optional
from unittest.mock import patch, AsyncMock, MagicMock, Mock, ANY

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client, OAuth2Client

from finra import base_client
from finra.async_client import AsyncClient
from finra.client import Client
from finra.exceptions import MockException, QATestEnvException
from finra.filings.create_individual import CreateIndividual
from finra.filings.form_br import FormBR
from finra.filings.form_u4 import FormU4
from finra.filings.form_u5 import FormU5
from finra.filings.non_registered_fingerprint import NonRegisteredFingerprint
from finra.filters import Filter

from .common import no_duplicates, set_meth


# NOTE: To add new datasets for unittest, add the dataset configuration to the
#       appropriate config in the "CONFIGURATION FOR GENERIC QUERY API TESTS"
#       section below; or for non-generic tests, add them directly to the
#       appropriate test class below.


API_KEY = "APIKEY"
API_SECRET = "0x6D8723EF"
TOKEN_PATH = "test_token.json"
TOKEN_CREATED_TIMESTAMP = 1780445000
TOKEN_EXPIRES_AT = TOKEN_CREATED_TIMESTAMP + 10_000

DATE = datetime.date(2025, 1, 2)
DATE_MINUS_30_DAYS = DATE - datetime.timedelta(days=30) #
DATE_MINUS_31_DAYS = DATE - datetime.timedelta(days=31)
DATE_PLUS_1_DAY = DATE + datetime.timedelta(days=1)

DATE_ISO = "2025-01-02"
DATE_MINUS_30_DAYS_ISO = "2024-12-03"

SSN = "123-45-6789"

class MockDateTime(datetime.datetime):
    @classmethod
    def from_datetime(cls, d):
        return cls(d.year, d.month, d.day, d.hour, d.minute, d.second,
                   d.microsecond, tzinfo=d.tzinfo)
    
    @classmethod
    def now(cls, tzinfo):
        return DATETIME.replace(tzinfo=tzinfo)


DATETIME = MockDateTime(2025, 1, 2, 3, 4, 5, 678999)
NOW = int(DATETIME.timestamp())

DATETIME_MINUS_30_DAYS = MockDateTime.from_datetime(
    DATETIME - datetime.timedelta(days=30)
    )
DATETIME_MINUS_31_DAYS = MockDateTime.from_datetime(
    DATETIME - datetime.timedelta(days=31)
    )
DATETIME_MINUS_32_DAYS = MockDateTime.from_datetime(
    DATETIME - datetime.timedelta(days=32)
    )

DATETIME_ISO_MS = "2025-01-02T03:04:05.678"
DATETIME_ISO_MS_TZ = "2025-01-02T03:04:05.678Z"
DATETIME_MIDNIGHT_ISO = "2025-01-02T00:00:00.000Z" #
DATETIME_MINUS_30_DAYS_ISO = "2024-12-03T03:04:05.678Z"
DATETIME_MIDNIGHT_MINUS_30_DAYS_ISO = "2024-12-03T00:00:00.000Z"
DATETIME_MINUS_31_DAYS_ISO = "2024-12-02T03:04:05.678Z"
DATETIME_MIDNIGHT_MINUS_31_DAYS_ISO = "2024-12-02T00:00:00.000Z"


##############################################################################
# LOGGING

class TestLogging(unittest.TestCase):
    
    @no_duplicates
    def test_base_client_logging(self):
        logger = base_client.get_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "finra.base_client")


##############################################################################
# DOCS

class TestDocs(unittest.TestCase):
    
    @no_duplicates
    def test_add_params_docs_with_params(self):
        def f(): pass
        base_client._add_params_docs(
            f, "limit",
            limit_default=1, limit_sync_max=2, limit_async_max=3
            )
        self.assertTrue("2 for synchronous requests" in f.__doc__)
        self.assertTrue("3 for asynchronous requests" in f.__doc__)
        self.assertTrue("Default: 1." in f.__doc__)
        
        def g(): pass
        base_client._add_params_docs(
            g, "limit",
            limit_default=1, limit_sync_max=None, limit_async_max=None
            )
        self.assertFalse("2 for synchronous requests" in g.__doc__)
        self.assertFalse("3 for asynchronous requests" in g.__doc__)
        self.assertTrue("Default: 1." in g.__doc__)
        
    @no_duplicates
    def test_add_params_docs_bad_param(self):
        def f(): pass
        with self.assertRaisesRegex(
            ValueError, "Unknown parameters: 'unknown_parameter'"
            ):
            base_client._add_params_docs(f, "unknown_parameter")
        
    @no_duplicates
    def test_add_params_docs_fields_param_missing_enum(self):
        def f(): pass
        with self.assertRaisesRegex(ValueError, "Missing enum"):
            base_client._add_params_docs(f, "fields")
        
    @no_duplicates
    def test_add_params_docs_sort_fields_param_missing_enum(self):
        def f(): pass
        with self.assertRaisesRegex(ValueError, "Missing enum"):
            base_client._add_params_docs(f, "sort_fields")
        
    @no_duplicates
    def test_add_filing_params_docs_bad_filing_param(self):
        def f(): pass
        with self.assertRaisesRegex(
            ValueError, "Unknown parameters: 'unknown_parameter'"
            ):
            base_client._add_filing_params_docs(f, "unknown_parameter")
        
    @no_duplicates
    def test_add_filing_params_docs_filing_param_missing_cls(self):
        def f(): pass
        with self.assertRaisesRegex(
            ValueError, "Expected filing_cls and filing_name"
            ):
            base_client._add_filing_params_docs(f, "filing")


##############################################################################
# RESPONSES

# Sanity check for HTTPX responses
class TestResponse(unittest.TestCase):
    def setUp(self):
        self._request = httpx.Request("url", "GET")
        self._json = {"test": 1}
        
    def _test_response(self, status_code):
        r = httpx.Response(status_code, request=self._request, json=self._json)
        r.raise_for_status()
        return r
    
    @no_duplicates
    def test_response_status_200_success(self):
        r = self._test_response(200)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), self._json)
        self.assertEqual(r.text, '{"test":1}')
        
    @no_duplicates
    def test_response_status_200_no_content_json_decode_error(self):
        self._json = None
        r = self._test_response(200)
        self.assertEqual(r.status_code, 200)
        with self.assertRaises(json.JSONDecodeError):
            r.json()
        
    @no_duplicates
    def test_response_status_300_https_status_error(self):
        with self.assertRaises(httpx.HTTPStatusError):
            self._test_response(300) # set follow_redirects=True to not raise
        
    @no_duplicates
    def test_response_status_400_https_status_error(self):
        with self.assertRaises(httpx.HTTPStatusError):
            self._test_response(400)
        
    @no_duplicates
    def test_response_status_500_https_status_error(self):
        with self.assertRaises(httpx.HTTPStatusError):
            self._test_response(500)


##############################################################################
# NON-API METHODS

# Mixin base class for methods that do not make API calls
class _TestNonAPI:
    
    @no_duplicates
    def test_token_age(self):
        token_manager = MagicMock()
        token_manager.token_age = 123
        
        client = self.client_cls(
            API_KEY, self.mock_session, token_manager=token_manager
            )
        
        self.assertEqual(client.token_age, 123)
        
    @no_duplicates
    def test_token_age_no_token_manager(self):
        with self.assertRaisesRegex(ValueError, "Token Manager not set"):
            self.client.token_age
        
    @no_duplicates
    def test_token_expires_at(self):
        token_manager = MagicMock()
        token_manager.expires_at = 123
        
        client = self.client_cls(
            API_KEY, self.mock_session, token_manager=token_manager
            )
        
        self.assertEqual(client.token_expires_at, 123)
        
    @no_duplicates
    def test_token_expires_at_no_token_manager(self):
        with self.assertRaisesRegex(ValueError, "Token Manager not set"):
            self.client.token_expires_at
        
    @no_duplicates
    def test_token_expires_in(self):
        token_manager = MagicMock()
        token_manager.expires_in = 123
        
        client = self.client_cls(
            API_KEY, self.mock_session, token_manager=token_manager
            )
        
        self.assertEqual(client.token_expires_in, 123)
        
    @no_duplicates
    def test_token_expires_in_no_token_manager(self):
        with self.assertRaisesRegex(ValueError, "Token Manager not set"):
            self.client.token_expires_in
        
    @no_duplicates
    def test_set_timeout(self):
        timeout = 123.456
        
        self.client.set_timeout(timeout)
        
        self.assertEqual(self.client.get_timeout(), timeout)
        
    @no_duplicates
    def test_set_timeout_with_resource_session(self):
        timeout = 123.456
        
        self.client._set_resource_session()
        
        self.client.set_timeout(timeout)
        
        self.assertEqual(self.client._resource_session.timeout.read, timeout)
        
    @no_duplicates
    def test_set_default_accept_json_true(self):
        self.client.set_default_accept_json(True)
        
        self.assertEqual(
            self.client.get_default_accept_json(), "application/json"
            )
        
    @no_duplicates
    def test_set_default_accept_json_false(self):
        self.client.set_default_accept_json(False)
        
        self.assertEqual(
            self.client.get_default_accept_json(), "text/plain"
            )
        
    @no_duplicates
    def test_set_default_accept_json_none(self):
        self.client.set_default_accept_json(None)
        
        self.assertEqual(
            self.client.get_default_accept_json(), "*/*"
            )
        
    @no_duplicates
    def test_prepare_headers_none_none(self):
        headers = self.client._prepare_headers(None, None)
        self.assertEqual(headers, None)
        
    @no_duplicates
    def test_prepare_headers_true_none(self):
        headers = self.client._prepare_headers(True, None)
        self.assertEqual(headers, {"Accept": "application/json"})
        
    @no_duplicates
    def test_prepare_headers_false_none(self):
        headers = self.client._prepare_headers(False, None)
        self.assertEqual(headers, {"Accept": "text/plain"})
        
    @no_duplicates
    def test_prepare_headers_none_1(self):
        headers = self.client._prepare_headers(None, 1)
        self.assertEqual(headers, {"Data-Version": "1"})
        
    
    ##########################################################################
    # QUERY API
    
    @no_duplicates
    def test_verify_sorting_partitions(self):
        e = Client.ConsolidatedShortInterest
        filters = Filter(e).add_compare(e.SETTLEMENT_DATE, "some value")
        self.client._verify_sorting_partitions(e, [e.SETTLEMENT_DATE], filters)
        
    @no_duplicates
    def test_verify_sorting_partitions_from_json(self):
        e = Client.ConsolidatedShortInterest
        filters = {"compareFilters": [{
            "fieldName": "settlementDate",
            "fieldValue": "some value",
            "compareType": "EQUAL",
            }]}
        self.client._verify_sorting_partitions(e, [e.SETTLEMENT_DATE], filters)
        
    @no_duplicates
    def test_verify_sorting_partitions_no_filters(self):
        e = Client.ConsolidatedShortInterest
        with self.assertRaisesRegex(
            ValueError,
            "Using sort_fields with this dataset requires a compare filter "
            "with 'CompareType.EQUAL' for each of the following partition "
            "fields: ConsolidatedShortInterest.SETTLEMENT_DATE."
            ):
            self.client._verify_sorting_partitions(
                e, [e.SETTLEMENT_DATE], None
                )
        
    @no_duplicates
    def test_verify_sorting_partitions_no_compare_filters(self):
        e = Client.ConsolidatedShortInterest
        with self.assertRaisesRegex(
            ValueError,
            "Using sort_fields with this dataset requires a compare filter "
            "with 'CompareType.EQUAL' for each of the following partition "
            "fields: ConsolidatedShortInterest.SETTLEMENT_DATE."
            ):
            self.client._verify_sorting_partitions(
                e, [e.SETTLEMENT_DATE], {"notCompareFilters": []}
                )
        
    @no_duplicates
    def test_verify_sorting_partitions_missing_compare_filter(self):
        e = Client.ConsolidatedShortInterest
        filters = {"compareFilters": [{
            "fieldName": "some partition",
            "fieldValue": "some value",
            "compareType": "EQUAL",
            }]}
        with self.assertRaisesRegex(
            ValueError,
            "Using sort_fields with this dataset requires a compare filter "
            "with 'CompareType.EQUAL' for each of the following partition "
            "fields: ConsolidatedShortInterest.SETTLEMENT_DATE."
            ):
            self.client._verify_sorting_partitions(
                e, [e.SETTLEMENT_DATE], filters
                )
        
    @no_duplicates
    def test_verify_sorting_partitions_wrong_compare_type_value(self):
        e = Client.ConsolidatedShortInterest
        filters = {"compareFilters": [{
            "fieldName": "settlementDate",
            "fieldValue": "some value",
            "compareType": "GREATER",
            }]}
        with self.assertRaisesRegex(
            ValueError,
            "Using sort_fields with this dataset requires a compare filter "
            "with 'CompareType.EQUAL' for each of the following partition "
            "fields: ConsolidatedShortInterest.SETTLEMENT_DATE."
            ):
            self.client._verify_sorting_partitions(
                e, [e.SETTLEMENT_DATE], filters
                )
        
    @no_duplicates
    def test_verify_sorting_partitions_wrong_filter_type(self):
        e = Client.ConsolidatedShortInterest
        filters = {"compareFilters": [{
            "fieldName": "settlementDate",
            "fieldValue": "some value",
            "compareType": "EQUAL",
            }]}
        with self.assertRaisesRegex(
            TypeError, "filters must be a Filter object or dict"
            ):
            self.client._verify_sorting_partitions(
                e, [e.SETTLEMENT_DATE], [filters]
                )
        
    @no_duplicates
    def test_sort_fields_enum(self):
        e = Client.ConsolidatedShortInterest
        sort_fields = self.client._sort_fields(e.SETTLEMENT_DATE, e)
        self.assertEqual(sort_fields, ["settlementDate"])
        
    @no_duplicates
    def test_sort_fields_tuple(self):
        e = Client.ConsolidatedShortInterest
        sort_fields = self.client._sort_fields((-1, e.SETTLEMENT_DATE), e)
        self.assertEqual(sort_fields, ["-settlementDate"])
        
    @no_duplicates
    def test_sort_fields_iterable(self):
        e = Client.ConsolidatedShortInterest
        sort_fields = self.client._sort_fields(
            [(-1, e.SETTLEMENT_DATE), e.CHANGE_PERCENT, (1, e.SYMBOL)], e
            )
        self.assertEqual(
            sort_fields, ["-settlementDate", "changePercent", "symbolCode"]
            )
        
    @no_duplicates
    def test_sort_fields_wrong_tuple_len(self):
        with self.assertRaisesRegex(
            ValueError,
            "Received a bad tuple for sort_fields: "
            "\\('sort field', 'too', 'long'\\). "
            "A sort fields tuple must have exactly two elements. "
            "The first element must be a number 'n' to specify "
            "the sort direction, with n >= 0 for ascending "
            "order, or n < 0 for descending order. "
            "The second element must be set to the field to "
            "sort by, specified as an enum member, or a string if "
            "require_enums=False."
            ):
            self.client._sort_fields(("sort field", "too", "long"), None)
        
    @no_duplicates
    def test_sort_fields_wrong_sign_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "Received a bad tuple for sort_fields: \\('sort field', 1\\). "
            "A sort fields tuple must have exactly two elements. "
            "The first element must be a number 'n' to specify "
            "the sort direction, with n >= 0 for ascending "
            "order, or n < 0 for descending order. "
            "The second element must be set to the field to "
            "sort by, specified as an enum member, or a string if "
            "require_enums=False."
            ):
            self.client._sort_fields(("sort field", 1), None)
        
    @no_duplicates
    def test_sort_fields_wrong_field_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "Received a bad tuple for sort_fields: "
            "\\(1, \\['sort field'\\]\\). "
            "A sort fields tuple must have exactly two elements. "
            "The first element must be a number 'n' to specify "
            "the sort direction, with n >= 0 for ascending "
            "order, or n < 0 for descending order. "
            "The second element must be set to the field to "
            "sort by, specified as an enum member, or a string if "
            "require_enums=False."
            ):
            self.client._sort_fields((1, ["sort field"]), None)
        
    @no_duplicates
    def test_sort_fields_enums_not_required(self):
        self.client.set_require_enums(False)
        e = Client.ConsolidatedShortInterest
        sort_fields = self.client._sort_fields("settlementDate", e)
        self.assertEqual(sort_fields, ["settlementDate"])


##############################################################################
# CONFIGURATION FOR GENERIC QUERY API TESTS

T = dict[str, tuple[str, str, Optional[EnumType], Optional[list[str]]]]

EQUITY: T = {
    "get_ats_block_summary": (
        "otcMarket", "blocksSummary",
        Client.ATSBlockSummary, ["MONTH_START_DATE"],
        ),
    "get_otc_block_summary": (
        "otcMarket", "otcBlocksSummary",
        Client.OTCBlockSummary, ["MONTH_START_DATE"],
        ),
    "get_consolidated_short_interest": (
        "otcMarket", "consolidatedShortInterest",
        Client.ConsolidatedShortInterest, ["SETTLEMENT_DATE"],
        ),
    "get_daily_short_sale_volume": (
        "otcMarket", "regShoDaily",
        Client.DailyShortSaleVolume, ["TRADE_REPORT_DATE"],
        ),
    "get_threshold_list": (
        "otcMarket", "thresholdList",
        Client.ThresholdList, ["TRADE_DATE"],
        ),
    "get_weekly_summary": (
        "otcMarket", "weeklySummary",
        Client.WeeklySummary, ["WEEK_START_DATE", "TIER_IDENTIFIER"],
        ),
    "get_monthly_summary": (
        "otcMarket", "monthlySummary",
        Client.MonthlySummary, ["MONTH_START_DATE", "TIER_IDENTIFIER"],
        ),
    "get_otc_daily_list": (
        "otcMarket", "otcDailyList",
        Client.OTCDailyList, ["CALENDAR_DAY"],
        ),
    }

EQUITY_NO_MOCK: T = {
    "get_weekly_summary_historic": (
        "otcMarket", "weeklySummaryHistoric",
        Client.WeeklySummary, ["WEEK_START_DATE", "TIER_IDENTIFIER"]
        ),
    }

FIXED_INCOME: T = {
    "get_agency_debt_market_breadth": (
        "fixedIncomeMarket", "agencyMarketBreadth",
        Client.AgencyDebtMarketBreadth, ["TRADE_REPORT_DATE"],
        ),
    "get_agency_debt_market_sentiment": (
        "fixedIncomeMarket", "agencyMarketSentiment",
        Client.AgencyDebtMarketSentiment, ["TRADE_REPORT_DATE"],
        ),
    "get_corporate_144a_debt_market_breadth": (
        "fixedIncomeMarket", "corporate144AMarketBreadth",
        Client.Corporate144ADebtMarketBreadth, ["TRADE_REPORT_DATE"],
        ),
    "get_corporate_144a_debt_market_sentiment": (
        "fixedIncomeMarket", "corporate144AMarketSentiment",
        Client.Corporate144ADebtMarketSentiment, ["TRADE_REPORT_DATE"],
        ),
    "get_corporate_and_agency_capped_volume": (
        "fixedIncomeMarket", "corporatesAndAgenciesCappedVolume",
        Client.CorporateAndAgencyCappedVolume, ["TRADE_REPORT_DATE"],
        ),
    "get_corporate_debt_market_breadth": (
        "fixedIncomeMarket", "corporateMarketBreadth",
        Client.CorporateDebtMarketBreadth, ["TRADE_REPORT_DATE"],
        ),
    "get_corporate_debt_market_sentiment": (
        "fixedIncomeMarket", "corporateMarketSentiment",
        Client.CorporateDebtMarketSentiment, ["TRADE_REPORT_DATE"],
        ),
    "get_securitized_products_capped_volume": (
        "fixedIncomeMarket", "securitizedProductsCappedVolume",
        Client.SecuritizedProductsCappedVolume, ["TRADE_REPORT_DATE"],
        ),
    "get_treasury_daily_aggregates": (
        "fixedIncomeMarket", "treasuryDailyAggregates",
        Client.TreasuryDailyAggregates, ["TRADE_DATE"],
        ),
    "get_treasury_monthly_aggregates": (
        "fixedIncomeMarket", "treasuryMonthlyAggregates",
        Client.TreasuryMonthlyAggregates, ["BEGINNING_OF_MONTH_DATE"],
        ),
    }

FIXED_INCOME_JSON_ONLY: T = {
    "get_agency_tba_pricing": (
        "fixedIncomeMarket", "agencyTBAPricing",
        Client.AgencyTBAPricing, [],
        ),
    "get_agency_cmo_pricing": (
        "fixedIncomeMarket", "agencyCMOPricing",
        Client.AgencyCMOPricing, [],
        ),
    "get_agency_mbs_trading_activity": (
        "fixedIncomeMarket", "agencyMBSTradingActivity",
        Client.AgencyMBSTradingActivity, [],
        ),
    "get_agency_mbs_arm_hybrid_pricing": (
        "fixedIncomeMarket", "agencyMBSArmHybridPricing",
        Client.AgencyMBSARMHybridPricing, [],
        ),
    "get_agency_mbs_pricing": (
        "fixedIncomeMarket", "agencyMBSPricing",
        Client.AgencyMBSPricing, [],
        ),
    "get_collateralized_obligations_pricing": (
        "fixedIncomeMarket", "collateralizedObligationPricing",
        Client.CollateralizedObligationsPricing, [],
        ),
    "get_daily_cmbs_pricing": (
        "fixedIncomeMarket", "dailyCMBSPricing",
        Client.DailyCMBSPricing, [],
        ),
    "get_non_agency_cmo_abs_pricing": (
        "fixedIncomeMarket", "nonAgencyCMOABSPricing",
        Client.NonAgencyCMOABSPricing, [],
        ),
    "get_non_agency_cmo_pricing": (
        "fixedIncomeMarket", "nonAgencyCMOVintagePricing",
        Client.NonAgencyCMOPricing, [],
        ),
    "get_securitized_products_errata": (
        "fixedIncomeMarket", "securitizedProductErrata",
        Client.SecuritizedProductsErrata, [],
        ),
    "get_securitized_products_trading_activity": (
        "fixedIncomeMarket", "securitizedProductTradingActivity",
        Client.SecuritizedProductsTradingActivity, [],
        ),
    "get_weekly_cmbs_pricing": (
        "fixedIncomeMarket", "weeklyCMBSPricing",
        Client.WeeklyCMBSPricing, [],
        ),
    }

FINRA: T = {
    "get_firm_registration_types": (
        "finra", "industrySnapshotFirmsByRegistrationType",
        Client.FirmsRegistrationTypes, ["REPORT_DATE"],
        ),
    }  # these methods also allow public credentials

FINRA_JSON_ONLY: T = {
    "get_finra_rulebook": (
        "finra", "finraRulebook",
        Client.FINRARulebook, ["RULE_NUMBER"],
        ),
    } # these methods also require firm credentials

FIRM: T = {
    "get_firm_customer_complaints": (
        "firm", "4530filings",
        Client.FirmCustomerComplaints, [],
        ),
    }

FIRM_WITH_ID: T = {
    "get_firm_disclosures": (
        "firm", "firmDisclosures",
        Client.FirmDisclosures, [],
        ),
    "get_firm_profile": (
        "firm", "firmProfile",
        Client.FirmProfile, [],
        ),
    "get_firm_registration_status_history": (
        "firm", "firmRegistrationStatusHistory",
        Client.FirmRegistrationStatusHistory, [],
        ),
    "get_firm_registrations": (
        "firm", "firmRegistrations",
        Client.FirmRegistrations, [],
        ),
    }

REGISTRATION: T = {
    "get_accounting": (
        "registration", "accounting", None, [],
        ),
    "get_branch_delta": (
        "registration", "branchDelta", None, [],
        ),
    "get_branch_list": (
        "registration", "branchList", None, [],
        ),
    "get_broker_dealer_firm_list": (
        "registration", "brokerDealerFirmList", None, [],
        ),
    "get_composite_branch": (
        "registration", "compositeBranch", None, [],
        ),
    "get_composite_individual": (
        "registration", "compositeIndividual", None, [],
        ),
    "get_individual_delta": (
        "registration", "individualDelta", None, [],
        ),
    "get_individual_pre_registration_search": (
        "registration", "preRegistrationIndividual",
        Client.IndividualPreRegistrationSearch, [],
        ),
    "get_individual_pre_registration_search_v2": (
        "registration", "preRegistrationIndividualv2", None, [],
        ),
    "get_individual_registration_validation": (
        "registration", "registrationValidationIndividual",
        Client.IndividualRegistrationValidation, [],
        ),
    "get_individual_registration_validation_details": (
        "registration", "individualRegistrationValidationDetails", None, [],
        ),
    "get_registered_individual_search": (
        "registration", "registeredIndividualSearch",
        Client.RegisteredIndividualSearch, [],
        ),
    "get_u4_form_prefill": (
        "registration", "u4FormPrefill", None, [],
        ),
    }

REGISTRATION_FINGERPRINT: T = {
    "get_individual_fingerprint": (
        "registration", "fingerprint", None, [],
        ),
    } # these methods use a different base URL and fingerprint credentials

REGISTRATION_QA_ONLY: T = {
    "get_altered_ssn_and_dob": (
        "registration", "alteredSSNandDOB", None, [],
        ),
    } # these methods are also no mock

REGISTRATION_NO_MOCK: T = {
    "get_composite_individual_seed": (
        "registration", "compositeIndividualSeed", None, [],
        ),
    }

REPORT_CARD_DETAILS: T = {
    "get_trace_agency_debt_details": (
        "reportcard", "traceAgencyDetail", None, [],
        ),
    "get_trace_treasuries_details": (
        "reportcard", "traceTreasuriesDetail", None, [],
        ),
    "get_trace_corporate_bonds_details": (
        "reportcard", "traceCorporateBondDetail", None, [],
        ),
    "get_trace_securitized_products_details": (
        "reportcard", "traceSecuritizedProductDetail", None, [],
        ),
    }

REPORT_CARD_SUMMARY: T = {
    "get_trace_agency_debt_summary": (
        "reportcard", "traceAgencySummary", None, [],
        ),
    "get_trace_treasuries_summary": (
        "reportcard", "traceTreasuriesSummary", None, [],
        ),
    "get_trace_corporate_bonds_summary": (
        "reportcard", "traceCorporateBondSummary", None, [],
        ),
    "get_trace_securitized_products_summary": (
        "reportcard", "traceSecuritizedProductSummary", None, [],
        ),
    }

JSON_RESPONSE_DATA_TYPE_ONLY: T = {}
JSON_RESPONSE_DATA_TYPE_ONLY.update(FINRA_JSON_ONLY)
JSON_RESPONSE_DATA_TYPE_ONLY.update(FIRM_WITH_ID)


##############################################################################
# GENERIC QUERY API TESTS

def _test_metadata(method, group, name, is_fingerprint, test_case):
    url = test_case.fingerprint_url if is_fingerprint else test_case.base_url
    url += f"/metadata/group/{group}/name/{name}"
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.METADATA,
        version=None
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=None, headers={"Accept": "application/json"}
        )


def _test_metadata_with_headers(
    method, group, name, is_fingerprint, test_case
    ):
    url = test_case.fingerprint_url if is_fingerprint else test_case.base_url
    url += f"/metadata/group/{group}/name/{name}"
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.METADATA,
        version=1
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=None,
        headers={"Accept": "application/json", "Data-Version": "1"}
        )


def _test_partitions(method, group, name, is_fingerprint, test_case):
    url = test_case.fingerprint_url if is_fingerprint else test_case.base_url
    url += f"/partitions/group/{group}/name/{name}"
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.PARTITIONS,
        version=None
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=None, headers={"Accept": "application/json"}
        )


def _test_partitions_with_headers(
    method, group, name, is_fingerprint, test_case
    ):
    url = test_case.fingerprint_url if is_fingerprint else test_case.base_url
    url += f"/partitions/group/{group}/name/{name}"
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.PARTITIONS,
        version=1
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=None,
        headers={"Accept": "application/json", "Data-Version": "1"}
        )


def _test_datasets(method, group, name, is_fingerprint, test_case):
    url = test_case.fingerprint_url if is_fingerprint else test_case.base_url
    url += "/datasets"
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATASETS
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url,
        params={
            "group": group,
            "name": name + "Mock" if test_case.mock else name
            },
        headers={"Accept": "application/json"}
        )


def _test_wrong_endpoint_type(method, test_case):
    with test_case.assertRaisesRegex(
        TypeError, "finra.base_client.BaseClient.Endpoint.DATA"
        ):
        getattr(test_case.client, method)(endpoint="DATA")


def _test_unknown_endpoint_value(method, test_case): # enums not required
    test_case.client.set_require_enums(False)
    with test_case.assertRaisesRegex(
        ValueError, "Unknown resource endpoint: 'bad endpoint'"
        ):
        getattr(test_case.client, method)(endpoint="bad endpoint")


def _test_get_data(method, group, name, test_case, headers=None):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)()
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params={}, headers=headers
        )


def _test_get_data_with_id(method, group, name, id, test_case, headers=None):
    if test_case.mock:
        name += "Mock"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(id)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        test_case.base_url + f"/data/group/{group}/name/{name}/id/{id}",
        params={}, headers=headers
        )


def _test_get_data_with_headers(method, group, name, test_case):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        accept_json=False,
        version=1,
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params={}, headers={"Accept": "text/plain", "Data-Version": "1"}
        )


def _test_get_data_with_headers_json_only(method, group, name, test_case):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(version=1)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params={}, headers={"Accept": "application/json", "Data-Version": "1"}
        )


def _test_get_data_with_text_params(method, group, name, enum, test_case):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA,
        delimiter="\x01",
        quote_values=False
        )
    
    params = {
        "delimiter": "\x01",
        "quoteValues": False,
        }
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=params, headers=None
        )


def _test_get_data_with_params(
    method, group, name, enum, partition_fields, test_case, headers=None
    ):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    if partition_fields: # requires POST
        sort_fields = None
    else:
        sort_fields = [((-1) ** i, f) for i, f in enumerate(enum)]
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA,
        fields=list(enum),
        filters=None,
        sort_fields=sort_fields,
        limit=100,
        offset=1,
        async_request=False
        )
    
    params = {
        "fields": ",".join([f.value for f in enum]),
        "limit": 100,
        "offset": 1,
        "async": False,
        }
    if sort_fields:
        params["sortFields"] = ",".join([
            "-" + f.value if s < 0 else f.value for s, f in sort_fields
            ])
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=params, headers=headers
        )


def _test_get_data_enums_not_required(
    method, group, name, test_case, headers=None
    ):
    test_case.client.set_require_enums(False)
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA.value
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params={}, headers=headers
        )


def _test_post_data(method, group, name, test_case, headers=None):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(filters={})
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json={}, headers=headers
        )

    
def _test_post_data_with_id(method, group, name, id, test_case, headers=None):
    if test_case.mock:
        name += "Mock"
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(id, filters={})
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        test_case.base_url + f"/data/group/{group}/name/{name}/id/{id}",
        json={}, headers=headers
        )


def _test_post_data_with_headers(method, group, name, test_case):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        filters={},
        accept_json=False,
        version=1
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json={}, headers={"Accept": "text/plain", "Data-Version": "1"}
        )


def _test_post_data_with_headers_json_only(method, group, name, test_case):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        filters={},
        version=1
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json={}, headers={"Accept": "application/json", "Data-Version": "1"}
        )


def _test_post_data_with_text_params(method, group, name, test_case):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA,
        filters={},
        delimiter="|",
        quote_values=True
        )
    
    params = {
        "delimiter": "|",
        "quoteValues": True,
        }
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json=params, headers=None
        )


def _test_post_data_with_params(
    method, group, name, enum, partition_fields, test_case, headers=None
    ):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    sort_fields = [((-1) ** i, f) for i, f in enumerate(enum)]
    filters = Filter(enum)
    for i, p in enumerate(partition_fields):
        filters.add_compare(enum[p], f"value {i}")
    
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA,
        fields=list(enum),
        filters=filters,
        sort_fields=sort_fields,
        limit=100,
        offset=1,
        async_request=True
        )
    
    params = {
        "fields": [f.value for f in enum],
        "sortFields": [
            "-" + f.value if s < 0 else f.value for s, f in sort_fields
            ],
        "limit": 100,
        "offset": 1,
        "async": True,
        }
    params.update(filters.build())
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json=params, headers=headers
        )


# No partition, no sort fields
def _test_post_data_with_params_no_partition(
    method, group, name, enum, test_case, headers=None
    ):
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    filters = Filter(enum)
    filters.add_compare(next(iter(enum.__members__.values())), "value")
    
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA,
        fields=list(enum),
        filters=filters,
        limit=100,
        offset=1,
        async_request=True
        )
    
    params = {
        "fields": [f.value for f in enum],
        "limit": 100,
        "offset": 1,
        "async": True,
        }
    params.update(filters.build())
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json=params, headers=headers
        )


def _test_post_data_enums_not_required(
    method, group, name, enum, partition_fields, test_case, headers=None
    ):
    test_case.client.set_require_enums(False)
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    
    fields = [f.value for f in enum]
    sort_fields = [((-1) ** i, f.value) for i, f in enumerate(enum)]
    filters = Filter(enum, require_enums=False)
    for i, p in enumerate(partition_fields):
        filters.add_compare(enum[p].value, f"value {i}")
    
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA.value,
        fields=fields,
        filters=filters,
        sort_fields=sort_fields
        )
    
    params = {
        "fields": fields,
        "sortFields": ["-" + f if s < 0 else f for s, f in sort_fields],
        }
    params.update(filters.build())
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json=params, headers=headers
        )


# No partition, no sort fields
def _test_post_data_enums_not_required_no_partition(
    method, group, name, enum, test_case, headers=None
    ):
    test_case.client.set_require_enums(False)
    url = test_case.base_url + f"/data/group/{group}/name/{name}"
    
    fields = [f.value for f in enum]
    filters = Filter(enum, require_enums=False)
    filters.add_compare(next(iter(enum.__members__.values())).value, "value")
    
    test_case.mock_session.post.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        endpoint=test_case.client.Endpoint.DATA.value,
        fields=fields,
        filters=filters
        )
    
    params = {
        "fields": fields,
        }
    params.update(filters.build())
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        json=params, headers=headers
        )


def _test_data_wrong_fields_type(method, enum, test_case):
    f = list(enum)[0]
    with test_case.assertRaisesRegex(
        TypeError, f"finra.base_client.BaseClient.{enum.__qualname__}.{f.name}"
        ):
        getattr(test_case.client, method)(fields=f.name)


def _test_data_wrong_sort_fields_type(
    method, enum, partition_fields, test_case
    ):
    f = list(enum)[0]
    filters = Filter(enum)
    for i, p in enumerate(partition_fields):
        filters.add_compare(enum[p], f"value {i}")
    with test_case.assertRaisesRegex(
        TypeError, f"finra.base_client.BaseClient.{enum.__qualname__}.{f.name}"
        ):
        getattr(test_case.client, method)(filters=filters, sort_fields=f.name)


def _test_data_fail_verify_sorting_partitions(
    method, enum, partition_fields, test_case
    ):
    enum_name = enum.__qualname__
    _partition_fields = [f"{enum_name}.{p}" for p in partition_fields]
    with test_case.assertRaisesRegex(
        ValueError,
        "Using sort_fields with this dataset requires a compare filter "
        "with 'CompareType.EQUAL' for each of the following partition "
        f"fields: {', '.join(_partition_fields)}."
        ):
        getattr(test_case.client, method)(sort_fields=["some field"])


def _test_data_wrong_filters_type(method, test_case):
    with test_case.assertRaisesRegex(
        TypeError, "filters must be a Filter object or dict"
        ):
        getattr(test_case.client, method)(filters=object())


# Generic TRACE datasets tests
def _test_trace_wrong_endpoint_type(method, test_case):
    with test_case.assertRaisesRegex(
        TypeError, "finra.base_client.BaseClient.Endpoint.DATA"
        ):
        getattr(test_case.client, method)(DATE, "ABCD", endpoint="DATA")


def _test_trace_unknown_endpoint_value(method, test_case): # enums not required
    test_case.client.set_require_enums(False)
    with test_case.assertRaisesRegex(
        ValueError, "Unknown resource endpoint: 'bad endpoint'"
        ):
        getattr(test_case.client, method)(
            DATE, "ABCD", endpoint="bad endpoint"
            )


def _test_trace_get_data(method, group, name, is_summary, test_case):
    if is_summary:
        url = test_case.base_url + f"/data/group/{group}/name/{name}"
    else:
        url = test_case.base_url + f"/v1/data/group/{group}/name/{name}"
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(DATE, "ABCD")
    
    params = {
        "period": DATE_ISO,
        "firmMarketIdentifier": "ABCD",
        }
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=params, headers={"Accept": "application/json"}
        )


def _test_trace_get_data_with_version(
    method, group, name, is_summary, test_case
    ):
    if is_summary:
        url = test_case.base_url + f"/data/group/{group}/name/{name}"
        headers = {"Accept": "application/json", "Data-Version": "2"}
    else:
        url = test_case.base_url + f"/v2/data/group/{group}/name/{name}"
        headers = {"Accept": "application/json"}
    
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(DATE, "ABCD", version=2)
    
    params = {
        "period": DATE_ISO,
        "firmMarketIdentifier": "ABCD",
        }
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url + "Mock" if test_case.mock else url,
        params=params, headers=headers
        )


def _test_trace_get_data_with_request_id(method, group, name, test_case):
    if test_case.mock:
        name += "Mock"
    
    url = test_case.base_url + f"/v1/data/group/{group}/name/{name}/123abc"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(request_id="123abc")
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url, params={}, headers={"Accept": "application/json"}
        )


def _test_trace_get_data_no_period(method, test_case):
    with test_case.assertRaisesRegex(
        ValueError,
        "When submitting a file request \\(request_id is None\\), "
        "TRACE Report Card methods require two arguments: "
        "period and firm_market_id."
        ):
        getattr(test_case.client, method)(firm_market_id="ABCD")


def _test_trace_get_data_no_firm_market_id(method, test_case):
    with test_case.assertRaisesRegex(
        ValueError,
        "When submitting a file request \\(request_id is None\\), "
        "TRACE Report Card methods require two arguments: "
        "period and firm_market_id."
        ):
        getattr(test_case.client, method)(DATE)


def _test_trace_get_data_wrong_period_type_datetime(method, test_case):
    with test_case.assertRaisesRegex(TypeError, "datetime.date"):
        getattr(test_case.client, method)(DATETIME, "ABCD")


def _test_trace_get_data_wrong_period_type_string(method, test_case):
    with test_case.assertRaisesRegex(TypeError, "datetime.date"):
        getattr(test_case.client, method)(DATE_ISO, "ABCD")


##############################################################################
# CONFIGURATION FOR GENERIC NOTIFICATION API TESTS

NOTIFICATION = {
    "get_finra_rulebook_notifications": (
        "finra", "finrarulebook",
        ),
    "get_draft_registration_filing_notifications": (
        "operation", "draftRegistrationFiling",
        ),
    }


##############################################################################
# GENERIC NOTIFICATION API TESTS

def _test_notification_get(method, group, name, test_case):
    url = test_case.base_url + \
          f"/notifications/group/{group}/event-type/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)()
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url, params={}, headers={"Accept": "application/json"}
        )


def _test_notification_get_with_version(method, group, name, test_case):
    url = test_case.base_url + \
          f"/notifications/group/{group}/event-type/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(version=1)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url, params={},
        headers={"Accept": "application/json", "Data-Version": "1"}
        )


def _test_notification_get_start_datetime(method, group, name, test_case):
    url = test_case.base_url + \
          f"/notifications/group/{group}/event-type/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(start_datetime=DATETIME)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url, params={"startDateTime": DATETIME_ISO_MS},
        headers={"Accept": "application/json"}
        )


def _test_notification_wrong_start_datetime_type(method, test_case):
    with test_case.assertRaisesRegex(
        TypeError, "datetime.date, datetime.datetime"
        ):
        getattr(test_case.client, method)(start_datetime=DATETIME_ISO_MS)


def _test_notification_get_end_datetime(method, group, name, test_case):
    url = test_case.base_url + \
          f"/notifications/group/{group}/event-type/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(end_datetime=DATETIME)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url, params={"endDateTime": DATETIME_ISO_MS},
        headers={"Accept": "application/json"}
        )


def _test_notification_wrong_end_datetime_type(method, test_case):
    with test_case.assertRaisesRegex(
        TypeError, "datetime.date, datetime.datetime"
        ):
        getattr(test_case.client, method)(end_datetime=DATETIME_ISO_MS)


def _test_notification_get_with_params(method, group, name, test_case):
    url = test_case.base_url + \
          f"/notifications/group/{group}/event-type/{name}"
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        limit=100,
        offset=1
        )
    
    params = {
        "limit": 100,
        "offset": 1,
        }
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        url, params=params, headers={"Accept": "application/json"}
        )


##############################################################################
# CONFIGURATION FOR GENERIC SUBMISSION API TESTS

# Callbacks to make filing objects
def _make_create_individual():
    filing = CreateIndividual()
    filing.set_filing_data({})
    return filing


def _make_form_br():
    filing = FormBR()
    filing.set_filing_status(FormBR.FilingStatus.SUBMITTED)
    filing.set_filing_type(FormBR.FilingType.INITIAL)
    filing.set_filing_data({
        'branch': {
            'identifyingInformation': {
                'branchCrdNumber': 12345,
                },
            },
        })
    return filing


def _make_form_u4():
    filing = FormU4()
    filing.set_filing_status(FormU4.FilingStatus.SUBMITTED)
    filing.set_filing_type(FormU4.FilingType.INITIAL)
    filing.set_individual_crd_number(1234567)
    filing.set_date_of_birth(DATE)
    filing.set_filing_data({})
    return filing


def _make_form_u5():
    filing = FormU5()
    filing.set_filing_status(FormU5.FilingStatus.SUBMITTED)
    filing.set_filing_type(FormU5.FilingType.FULL)
    filing.set_individual_crd_number(1234567)
    filing.set_date_of_birth(DATE)
    filing.set_filing_data({})
    return filing


def _make_nrf():
    filing = NonRegisteredFingerprint()
    filing.set_filing_type(NonRegisteredFingerprint.FilingType.INITIAL)
    filing.set_filing_data({})
    return filing


SUBMISSION = {
    "create_individual_submission": (
        "registration", "create-individual", _make_create_individual,
        ),
    "form_br_submission": (
        "registration", "br", _make_form_br,
        ),
    "form_u4_submission": (
        "registration", "u4", _make_form_u4,
        ),
    "form_u5_submission": (
        "registration", "u5", _make_form_u5,
        ),
    "non_registered_fingerprint_submission": (
        "registration", "nrf", _make_nrf,
        ),
    }


##############################################################################
# GENERIC SUBMISSION API TESTS

def _test_submission_get(method, group, name, test_case):
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)("requestId")
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        test_case.base_url + \
            f"/v1/submissions/filings/{group}/{name}/requestId",
        params=None, headers={"Accept": "application/json"}
        )


def _test_submission_get_with_version_2(method, group, name, test_case):
    test_case.mock_session.get.return_value = test_case.response
    
    result = getattr(test_case.client, method)("requestId", version=2)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.get.assert_called_once_with(
        test_case.base_url + \
            f"/v2/submissions/filings/{group}/{name}/requestId",
        params=None,
        headers={"Accept": "application/json"}
        )
    

def _test_submission_no_filing_no_request_id(method, test_case):
    with test_case.assertRaisesRegex(
        ValueError,
        "Must provide either: \\(1\\) the request_id to GET or "
        "DELETE a filing, \\(2\\) the filing \\(object or data\\) to "
        "POST filing data, or if supported \\(3\\) both the "
        "request_id and the filing \\(object or data\\) to update a "
        "filing. If put=True, the filing data will be replaced "
        "by the update data via a PUT, otherwise merge the "
        "filing data with the update data via a PATCH. "
        "Default behavior is put=False."
        ):
        getattr(test_case.client, method)()


def _test_submission_post_filing_obj(
    method, group, name, make_filing, test_case
    ):
    test_case.mock_session.post.return_value = test_case.response
    
    filing = make_filing()
    result = getattr(test_case.client, method)(filing=filing)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        test_case.base_url + f"/v1/submissions/filings/{group}/{name}",
        json=filing.build(), headers={"Accept": "application/json"}
        )


def _test_submission_post_filing_json(
    method, group, name, make_filing, test_case
    ):
    test_case.mock_session.post.return_value = test_case.response
    
    filing = make_filing().build()
    result = getattr(test_case.client, method)(filing=filing)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.post.assert_called_once_with(
        test_case.base_url + f"/v1/submissions/filings/{group}/{name}",
        json=filing, headers={"Accept": "application/json"}
        )


def _test_submission_post_missing_filing_data_ops(
    method, make_filing, test_case
    ):
    filing = make_filing()
    filing.clear_filing_data()
    filing.clear_operations()
    with test_case.assertRaisesRegex(
        ValueError,
        "Must set either Filing Data, or add at least one "
        "Operation on existing data."
        ):
        getattr(test_case.client, method)(filing=filing)


def _test_submission_delete(method, group, name, test_case):
    test_case.mock_session.delete.return_value = test_case.response
    
    result = getattr(test_case.client, method)("requestId", delete=True)
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.delete.assert_called_once_with(
        test_case.base_url + \
            f"/v1/submissions/filings/{group}/{name}/requestId",
        headers={"Accept": "application/json"}
        )


def _test_submission_delete_with_filing(method, group, name, test_case):
    with test_case.assertRaisesRegex(
        ValueError, "Filing must be None to delete. Just pass the request_id."
        ):
        getattr(test_case.client, method)(filing={}, delete=True)


def _test_submission_patch_filing(method, group, name, test_case):
    test_case.mock_session.patch.return_value = test_case.response
    
    result = getattr(test_case.client, method)("requestId", filing={})
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.patch.assert_called_once_with(
        test_case.base_url + \
            f"/v1/submissions/filings/{group}/{name}/requestId",
        json={}, headers={"Accept": "application/json"}
        )


def _test_submission_put_filing(method, group, name, test_case):
    test_case.mock_session.put.return_value = test_case.response
    
    result = getattr(test_case.client, method)(
        "requestId", filing={}, put=True
        )
    
    test_case.assertEqual(result, test_case.response)
    test_case.mock_session.put.assert_called_once_with(
        test_case.base_url + \
            f"/v1/submissions/filings/{group}/{name}/requestId",
        json={}, headers={"Accept": "application/json"}
        )


def _test_submission_validate_filing_obj(
    method, group, name, make_filing, test_case
    ):
    with patch("finra.base_client.Validator") as validator:
        validator.return_value = validator
        
        test_case.mock_session.post.return_value = test_case.response
        
        filing = make_filing()
        result = getattr(test_case.client, method)(
            filing=filing, validate=True
            )
        
        data = filing.build()
        
        test_case.assertEqual(result, test_case.response)
        test_case.mock_session.post.assert_called_once_with(
            test_case.base_url + f"/v1/submissions/filings/{group}/{name}",
            json=data, headers={"Accept": "application/json"}
            )
        
        validator.assert_called_once_with(test_case.client, filing.schema_url)
        validator.validate.assert_called_once_with(data)


def _test_submission_validate_filing_json(method, group, name, test_case):
    with patch("finra.base_client.Validator") as validator:
        validator.return_value = validator
        
        test_case.mock_session.post.return_value = test_case.response
        
        schema_url = "Schema URL"
        result = getattr(test_case.client, method)(
            filing={},
            validate=True,
            schema_url=schema_url
            )
        
        test_case.assertEqual(result, test_case.response)
        test_case.mock_session.post.assert_called_once_with(
            test_case.base_url + f"/v1/submissions/filings/{group}/{name}",
            json={}, headers={"Accept": "application/json"}
            )
        
        validator.assert_called_once_with(test_case.client, schema_url)
        validator.validate.assert_called_once_with({})


def _test_submission_validate_filing_obj_with_schema_url(
    method, group, name, make_filing, test_case
    ):
    with patch("finra.base_client.Validator") as validator:
        validator.return_value = validator
        
        test_case.mock_session.post.return_value = test_case.response
        
        filing = make_filing()
        schema_url = "Schema URL"
        result = getattr(test_case.client, method)(
            filing=filing,
            validate=True,
            schema_url=schema_url
            )
        
        data = filing.build()
        
        test_case.assertEqual(result, test_case.response)
        test_case.mock_session.post.assert_called_once_with(
            test_case.base_url + f"/v1/submissions/filings/{group}/{name}",
            json=data, headers={"Accept": "application/json"}
            )
        
        validator.assert_called_once_with(test_case.client, schema_url)
        validator.validate.assert_called_once_with(data)


def _test_submission_validate_filing_json_no_schema_url(method, group, name,
                                                        test_case):
    with test_case.assertRaisesRegex(
        ValueError,
        "A non-empty schema_url must be provided if filing "
        "object does not subclass BaseFiling."
        ):
        getattr(test_case.client, method)(filing={}, validate=True)


# AsyncClient only
def _test_submission_validate_wrong_session_type(method, test_case):
    with test_case.assertRaisesRegex(
        TypeError,
        "Client-side filing validation is not currently "
        "supported for AsyncClient. Either set validate=False "
        "when doing submission requests using the AsyncClient "
        "class, or use the synchronous Client class to do "
        "client-side validation during submission requests."
        ):
        getattr(test_case.client, method)(filing={}, validate=True)


# Generic no mock fail test
def _test_no_mock(method, test_case):
    with test_case.assertRaisesRegex(
        MockException,
        "This method does not have a Mock endpoint. To use "
        "this method set mock=False when creating the client, "
        "and use non-Mock API credentials."
        ):
        getattr(test_case.client, method)()


# Generic no QA test environment fail test
def _test_not_qa_env(method, test_case):
    with test_case.assertRaisesRegex(
        QATestEnvException,
        "This endpoint is only available in the QA Test "
        "Environment. To use this method set "
        "test_environment=True when creating the client, "
        "and use QA Test Environment credentials."
        ):
        getattr(test_case.client, method)()


##############################################################################
# API METHODS

# Mixin base class for methods that make API calls & support Mock, QA Test Env
class _TestAPI:
    
    
    ##########################################################################
    # ASYNC REQUEST METHODS
    
    @no_duplicates
    def test_get_async_request_status(self):
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_async_request_status("check status link")
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            "check status link", params=None,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_async_result(self):
        self.client._resource_session = self.mock_cls()
        self.client._resource_session.get.return_value = self.response
        
        result = self.client.get_async_result("result link")
        
        self.assertEqual(result, self.response)
        self.client._resource_session.get.assert_called_once_with(
            "result link", params=None, headers=None
            )
    
    
    ##########################################################################
    # DATASETS
    
    @no_duplicates
    def test_get_datasets(self):
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_datasets()
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            self.base_url + "/datasets", params={},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_datasets_with_params(self):
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_datasets(
            group=Client.Groups.EQUITY,
            name=Client.EquityGroup.ATS_BLOCK_SUMMARY
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            self.base_url + "/datasets",
            params={"group": "otcMarket", "name": "blocksSummary"},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_datasets_wrong_group_type(self):
        with self.assertRaisesRegex(
            TypeError, "finra.base_client.BaseClient.Groups.EQUITY"
            ):
            self.client.get_datasets(group="EQUITY")
        
    @no_duplicates
    def test_get_datasets_wrong_name_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "finra.base_client.BaseClient.EquityGroup.ATS_BLOCK_SUMMARY"
            ):
            self.client.get_datasets(name="ATS_BLOCK_SUMMARY")
        
    @no_duplicates
    def test_get_datasets_wrong_name_type_no_suggestions(self):
        with self.assertRaisesRegex(
            TypeError,
            "Expected type\\(s\\): finra.base_client.BaseClient.EquityGroup, "
            "finra.base_client.BaseClient.FixedIncomeGroup, "
            "finra.base_client.BaseClient.FINRAGroup, "
            "finra.base_client.BaseClient.FirmGroup, "
            "finra.base_client.BaseClient.RegistrationGroup, "
            "finra.base_client.BaseClient.ReportCardGroup. "
            "Got type 'str'. "
            "\\(Initialize with require_enums=False to disable this check\\)"
            ):
            self.client.get_datasets(name="NAME_IS_NOT_EVEN_CLOSE")
        
    @no_duplicates
    def test_get_datasets_enums_not_required(self):
        self.client.set_require_enums(False)
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_datasets(
            group="otcMarket", name="blocksSummary"
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            self.base_url + "/datasets",
            params={"group": "otcMarket", "name": "blocksSummary"},
            headers={"Accept": "application/json"}
            )
        
    # Test for logging error in _log_wrapper, using get_datasets
    @no_duplicates
    @patch("logging.error")
    def test_logging_error(self, logging_error):
        class TestLoggingError(Exception):
            pass
        
        self.mock_session.get.side_effect = TestLoggingError()
        
        with self.assertRaises(TestLoggingError):
            self.client.get_datasets()
        
        logging_error.assert_called_once_with(
            "%s: %s", ANY, "GET", exc_info=True
            )
        
    # Test for non-debug logging branches, no requests counted
    @no_duplicates
    def test_logging_info_doesnt_count_requests(self):
        logger = base_client.get_logger()
        logger.setLevel("INFO")
        
        self.assertFalse(logger.level <= logging.DEBUG)
        
        request_count = next(base_client._REQUEST_COUNTER)
        
        self.client.get_datasets()
        
        self.assertEqual(next(base_client._REQUEST_COUNTER), request_count + 1)
    
    
    ##########################################################################
    # REGISTRATION - ACCOUNTING
    
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data(self):
        url = self.base_url + "/data/group/registration/name/accounting"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_accounting()
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDate": DATE_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_with_headers(self):
        url = self.base_url + "/data/group/registration/name/accounting"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_accounting(version=1)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDate": DATE_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_start_datetime(self):
        url = self.base_url + "/data/group/registration/name/accounting"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_accounting(start_date=DATETIME_MINUS_30_DAYS)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDate": DATE_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_wrong_start_date_type(self):
        with self.assertRaisesRegex(TypeError, "MockDateTime"):
            self.client.get_accounting(start_date=DATE_ISO)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_bad_start_date_value(self):
        with self.assertRaisesRegex(
            ValueError,
            "start_date cannot be more than 30 days prior to today's date"
            ):
            self.client.get_accounting(start_date=DATE_MINUS_31_DAYS)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_end_datetime(self):
        url = self.base_url + "/data/group/registration/name/accounting"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_accounting(end_date=DATETIME)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDate": DATE_MINUS_30_DAYS_ISO, "endDate": DATE_ISO},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_wrong_end_date_type(self):
        with self.assertRaisesRegex(TypeError, "MockDateTime"):
            self.client.get_accounting(end_date=DATE_ISO)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_bad_end_date_value(self):
        with self.assertRaisesRegex(
            ValueError, "end_date cannot be in the future"
            ):
            self.client.get_accounting(end_date=DATE_PLUS_1_DAY)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_accounting_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + "/data/group/registration/name/accounting"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_accounting(
            endpoint=Client.Endpoint.DATA.value
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDate": DATE_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - BRANCH DELTA
    
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data(self):
        url = self.base_url + "/data/group/registration/name/branchDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_branch_delta()
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MIDNIGHT_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_with_headers(self):
        url = self.base_url + "/data/group/registration/name/branchDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_branch_delta(version=1)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MIDNIGHT_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_start_datetime(self):
        url = self.base_url + "/data/group/registration/name/branchDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_branch_delta(
            start_datetime=DATETIME_MINUS_30_DAYS
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_wrong_start_datetime_type(self):
        with self.assertRaisesRegex(TypeError, "MockDateTime"):
            self.client.get_branch_delta(start_datetime=DATETIME_ISO_MS_TZ)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_bad_start_datetime_value(self):
        with self.assertRaisesRegex(
            ValueError,
            "start_datetime cannot be more than 30 days prior to today's date"
            ):
            self.client.get_branch_delta(start_datetime=DATETIME_MINUS_31_DAYS)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_end_datetime(self):
        url = self.base_url + "/data/group/registration/name/branchDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_branch_delta(end_datetime=DATETIME)
        
        params = params={
            "startDateTime": DATETIME_MIDNIGHT_MINUS_30_DAYS_ISO,
            "endDateTime": DATETIME_ISO_MS_TZ,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_wrong_end_datetime_type(self):
        with self.assertRaisesRegex(TypeError, "MockDateTime"):
            self.client.get_branch_delta(end_datetime=DATETIME_ISO_MS_TZ)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_branch_delta_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + "/data/group/registration/name/branchDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_branch_delta(
            endpoint=Client.Endpoint.DATA.value
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MIDNIGHT_MINUS_30_DAYS_ISO},
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - BROKER DEALER FIRM LIST
    
    @no_duplicates
    def test_get_broker_dealer_firm_list_data_with_params(self):
        url = self.base_url + \
            "/data/group/registration/name/brokerDealerFirmList"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_broker_dealer_firm_list(
            limit=100,
            offset=1
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"limit": 100, "offset": 1},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_broker_dealer_firm_list_data_with_firm_crd_number(self):
        url = self.base_url + \
            "/data/group/registration/name/brokerDealerFirmList"
        self.mock_session.get.return_value = self.response
        
        firm_crd_number = 1234567
        result = self.client.get_broker_dealer_firm_list(firm_crd_number)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"firmCrdNumber": firm_crd_number},
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - COMPOSITE BRANCH
    
    @no_duplicates
    def test_get_composite_branch_data(self):
        url = self.base_url + "/data/group/registration/name/compositeBranch"
        self.mock_session.get.return_value = self.response
        
        branch_crd_number = 12345
        result = self.client.get_composite_branch(branch_crd_number)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"branchCrdNumber": branch_crd_number},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_branch_data_with_headers(self):
        url = self.base_url + "/data/group/registration/name/compositeBranch"
        self.mock_session.get.return_value = self.response
        
        branch_crd_number = 12345
        result = self.client.get_composite_branch(
            branch_crd_number,
            version=1
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"branchCrdNumber": branch_crd_number},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_composite_branch_data_no_branch_crd_number(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Composite Branch requires the first argument to be the "
            "branch_crd_number."
            ):
            self.client.get_composite_branch()
        
    @no_duplicates
    def test_get_composite_branch_data_with_sections(self):
        url = self.base_url + "/data/group/registration/name/compositeBranch"
        self.mock_session.get.return_value = self.response
        
        e = Client.CompositeBranchSections
        
        branch_crd_number = 12345
        result = self.client.get_composite_branch(
            branch_crd_number,
            sections=[e.REGISTRATIONS, e.DEFICIENCIES]
            )
        
        params = {
            "branchCrdNumber": branch_crd_number,
            "sections": "registrations,deficiencies",
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_branch_data_wrong_sections_type(self):
        e = Client.CompositeBranchSections
        with self.assertRaisesRegex(
            TypeError, "finra.base_client.BaseClient.CompositeBranchSections"
            ):
            self.client.get_composite_branch(
                12345,
                sections=e.REGISTRATIONS.value
                )
        
    @no_duplicates
    def test_get_composite_branch_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + "/data/group/registration/name/compositeBranch"
        self.mock_session.get.return_value = self.response
        
        e = Client.CompositeBranchSections
        
        branch_crd_number = 12345
        result = self.client.get_composite_branch(
            branch_crd_number,
            sections=[e.REGISTRATIONS.value, e.DEFICIENCIES.value],
            endpoint=Client.Endpoint.DATA.value
            )
        
        params = {
            "branchCrdNumber": branch_crd_number,
            "sections": "registrations,deficiencies",
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
    
    
    ##########################################################################
    # REGISTRATION - COMPOSITE INDIVIDUAL
    
    @no_duplicates
    def test_get_composite_individual_data(self):
        url = self.base_url + \
              "/data/group/registration/name/compositeIndividual"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1234567
        result = self.client.get_composite_individual(individual_crd_number)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"individualCrdNumber": individual_crd_number},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_individual_data_with_headers(self):
        url = self.base_url + \
              "/data/group/registration/name/compositeIndividual"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1234567
        result = self.client.get_composite_individual(
            individual_crd_number,
            version=1
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"individualCrdNumber": individual_crd_number},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_composite_individual_data_no_individual_crd_number(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Composite Individual requires the first argument to be the "
            "individual_crd_number."
            ):
            self.client.get_composite_individual()
        
    @no_duplicates
    def test_get_composite_individual_data_with_sections(self):
        url = self.base_url + \
              "/data/group/registration/name/compositeIndividual"
        self.mock_session.get.return_value = self.response
        
        e = Client.CompositeIndividualSections
        
        individual_crd_number = 1234567
        result = self.client.get_composite_individual(
            individual_crd_number,
            sections=[e.INDIVIDUAL, e.OCCURRENCES]
            )
        
        params = {
            "individualCrdNumber": individual_crd_number,
            "sections": "individual,occurrences",
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_individual_data_wrong_sections_type(self):
        e = Client.CompositeIndividualSections
        with self.assertRaisesRegex(
            TypeError,
            "finra.base_client.BaseClient.CompositeIndividualSections"
            ):
            self.client.get_composite_individual(
                12345,
                sections=e.INDIVIDUAL.value
                )
        
    @no_duplicates
    def test_get_composite_individual_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + \
              "/data/group/registration/name/compositeIndividual"
        self.mock_session.get.return_value = self.response
        
        e = Client.CompositeIndividualSections
        
        individual_crd_number = 1234567
        result = self.client.get_composite_individual(
            individual_crd_number,
            sections=[e.INDIVIDUAL.value, e.OCCURRENCES.value],
            endpoint=Client.Endpoint.DATA.value
            )
        
        params = {
            "individualCrdNumber": individual_crd_number,
            "sections": "individual,occurrences",
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - INDIVIDUAL DELTA
    
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data(self):
        url = self.base_url + "/data/group/registration/name/individualDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_individual_delta()
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MIDNIGHT_MINUS_31_DAYS_ISO},
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_with_headers(self):
        url = self.base_url + "/data/group/registration/name/individualDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_individual_delta(version=1)
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MIDNIGHT_MINUS_31_DAYS_ISO},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_with_params_version_2(self):
        url = self.base_url + "/data/group/registration/name/individualDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_individual_delta(
            limit=100,
            offset=1
            )
        
        params = {
            "startDateTime": DATETIME_MIDNIGHT_MINUS_31_DAYS_ISO,
            "limit": 100,
            "offset": 1,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_pagination_error_version_1(self):
        with self.assertRaisesRegex(
            ValueError,
            "Pagination keywords 'limit' and 'offset' are not "
            "supported for API Version 1"
            ):
            self.client.get_individual_delta(limit=100, version=1)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_start_datetime(self):
        url = self.base_url + "/data/group/registration/name/individualDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_individual_delta(
            start_datetime=DATETIME_MINUS_31_DAYS
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MINUS_31_DAYS_ISO},
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_wrong_start_datetime_type(self):
        with self.assertRaisesRegex(TypeError, "MockDateTime"):
            self.client.get_individual_delta(start_datetime=DATETIME_ISO_MS_TZ)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_bad_start_datetime_value(self):
        with self.assertRaisesRegex(
            ValueError,
            "start_datetime cannot be more than 31 days prior to today's date"
            ):
            self.client.get_individual_delta(
                start_datetime=DATETIME_MINUS_32_DAYS
                )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_end_datetime(self):
        url = self.base_url + "/data/group/registration/name/individualDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_individual_delta(end_datetime=DATETIME)
        
        params = params={
            "startDateTime": DATETIME_MIDNIGHT_MINUS_31_DAYS_ISO,
            "endDateTime": DATETIME_ISO_MS_TZ
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_wrong_end_datetime_type(self):
        with self.assertRaisesRegex(TypeError, "MockDateTime"):
            self.client.get_individual_delta(end_datetime=DATETIME_ISO_MS_TZ)
        
    @no_duplicates
    @patch("finra.base_client.datetime", MockDateTime)
    def test_get_individual_delta_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + "/data/group/registration/name/individualDelta"
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_individual_delta(
            endpoint=Client.Endpoint.DATA.value
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params={"startDateTime": DATETIME_MIDNIGHT_MINUS_31_DAYS_ISO},
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    
    ##########################################################################
    # REGISTRATION - INDIVIDUAL FINGERPRINT
    
    @no_duplicates
    def test_get_individual_fingerprint_data(self):
        url = self.fingerprint_url + \
              "/data/group/registration/name/fingerprint"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1234567
        result = self.client.get_individual_fingerprint(
            individual_crd_number,
            DATE
            )
        
        params = {
            "individualCrdNumber": individual_crd_number,
            "DOB": DATE_ISO,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_fingerprint_data_with_headers(self):
        url = self.fingerprint_url + \
              "/data/group/registration/name/fingerprint"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1234567
        result = self.client.get_individual_fingerprint(
            individual_crd_number,
            DATE,
            version=1
            )
        
        params = {
            "individualCrdNumber": individual_crd_number,
            "DOB": DATE_ISO,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_individual_fingerprint_data_no_individual_crd_number(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Fingerprint requires two arguments: "
            "individual_crd_number and date_of_birth."
            ):
            self.client.get_individual_fingerprint(date_of_birth=DATE)
        
    @no_duplicates
    def test_get_individual_fingerprint_data_no_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Fingerprint requires two arguments: "
            "individual_crd_number and date_of_birth."
            ):
            self.client.get_individual_fingerprint(1234567)
        
    @no_duplicates
    def test_get_individual_fingerprint_data_wrong_date_of_birth_type_datetime(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_individual_fingerprint(1234567, DATETIME)
        
    @no_duplicates
    def test_get_individual_fingerprint_data_wrong_date_of_birth_type_string(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_individual_fingerprint(1234567, DATE_ISO)
        
    @no_duplicates
    def test_get_individual_fingerprint_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.fingerprint_url + \
              "/data/group/registration/name/fingerprint"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1234567
        result = self.client.get_individual_fingerprint(
            individual_crd_number,
            date_of_birth=DATE,
            endpoint=Client.Endpoint.DATA.value
            )
        
        params = {
            "individualCrdNumber": individual_crd_number,
            "DOB": DATE_ISO,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url + "Mock" if self.mock else url,
            params=params,
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - INDIVIDUAL PRE-REGISTRATION SEARCH
    
    @no_duplicates
    def test_get_individual_pre_registration_search_data_with_ssn(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividual"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_individual_pre_registration_search(
            DATE,
            ssn=SSN
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "ssn",
             "fieldValue": SSN,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_with_last_name(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividual"
        self.mock_session.post.return_value = self.response
        
        last_name = "Smith"
        result = self.client.get_individual_pre_registration_search(
            DATE,
            last_name=last_name
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "lastName",
             "fieldValue": last_name,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_with_first_name(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividual"
        self.mock_session.post.return_value = self.response
        
        first_name = "John"
        result = self.client.get_individual_pre_registration_search(
            DATE,
            first_name=first_name
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "firstName",
             "fieldValue": first_name,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_with_headers(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividual"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_individual_pre_registration_search(
            DATE,
            ssn=SSN,
            version=1
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "ssn",
             "fieldValue": SSN,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_with_params(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividual"
        self.mock_session.post.return_value = self.response
        
        e = Client.IndividualPreRegistrationSearch
        
        fields = list(e)
        sort_fields = [((-1) ** i, f) for i, f in enumerate(e)]
        
        result = self.client.get_individual_pre_registration_search(
            DATE,
            ssn=SSN,
            fields=fields,
            sort_fields=sort_fields,
            limit=100,
            offset=1,
            async_request=False
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "fields": [f.value for f in fields],
            "sortFields": [
                "-" + f.value if s < 0 else f.value for s, f in sort_fields
                ],
            "limit": 100,
            "offset": 1,
            "async": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_only_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Pre-Registration Search requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "\\(2\\) last_name, or \\(3\\) first_name."
            ):
            self.client.get_individual_pre_registration_search(DATE)
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_no_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Pre-Registration Search requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "\\(2\\) last_name, or \\(3\\) first_name."
            ):
            self.client.get_individual_pre_registration_search(ssn=SSN)
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_wrong_date_of_birth_type_datetime(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_individual_pre_registration_search(
                DATETIME,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_wrong_date_of_birth_type_string(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_individual_pre_registration_search(
                DATE_ISO,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_wrong_fields_type(self):
        e = Client.IndividualPreRegistrationSearch
        f = next(iter(e))
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.IndividualPreRegistrationSearch."
                f"{f.name}"
                )
            ):
            self.client.get_individual_pre_registration_search(
                DATE,
                ssn=SSN,
                fields=f.name
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_wrong_sort_fields_type(self):
        e = Client.IndividualPreRegistrationSearch
        with self.assertRaisesRegex(
            TypeError,
            "finra.base_client.BaseClient.IndividualPreRegistrationSearch"
            ):
            self.client.get_individual_pre_registration_search(
                DATE,
                ssn=SSN,
                sort_fields=e.FIRST_NAME.value
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividual"
        self.mock_session.post.return_value = self.response
        
        e = Client.IndividualPreRegistrationSearch
        
        fields = [f.value for f in e]
        sort_fields = [((-1) ** i, f.value) for i, f in enumerate(e)]
        
        result = self.client.get_individual_pre_registration_search(
            DATE, ssn=SSN,
            endpoint=Client.Endpoint.DATA.value,
            fields=fields,
            sort_fields=sort_fields
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "fields": fields,
            "sortFields": ["-" + f if s < 0 else f for s, f in sort_fields],
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - INDIVIDUAL PRE-REGISTRATION SEARCH, VERSION 2
    
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_with_ssn(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividualv2"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_individual_pre_registration_search_v2(
            DATE,
            ssn=SSN
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "async": True,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_with_individual_crd_number(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividualv2"
        self.mock_session.post.return_value = self.response
        
        individual_crd_number = SSN
        result = self.client.get_individual_pre_registration_search_v2(
            DATE,
            individual_crd_number=individual_crd_number
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "individualCrdNumber",
                 "fieldValue": individual_crd_number,
                 "compareType": "EQUAL"},
                ],
            "async": True,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
    
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_with_headers(self):
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividualv2"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_individual_pre_registration_search_v2(
            DATE,
            ssn=SSN,
            version=1
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "async": True,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_only_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Pre-Registration Search V2 requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "or \\(2\\) individual_crd_number."
            ):
            self.client.get_individual_pre_registration_search_v2(DATE)
        
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_no_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Pre-Registration Search V2 requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "or \\(2\\) individual_crd_number."
            ):
            self.client.get_individual_pre_registration_search_v2(
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_wrong_date_of_birth_type_datetime(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_individual_pre_registration_search_v2(
                DATETIME,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_wrong_date_of_birth_type_string(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_individual_pre_registration_search_v2(
                DATE_ISO,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_individual_pre_registration_search_v2_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + \
              "/data/group/registration/name/preRegistrationIndividualv2"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_individual_pre_registration_search_v2(
            DATE,
            ssn=SSN,
            endpoint=Client.Endpoint.DATA.value,
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "async": True,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - INDIVIDUAL REGISTRATION VALIDATION
    
    @no_duplicates
    def test_get_individual_registration_validation_data(self):
        url = self.base_url + \
              "/data/group/registration/name/registrationValidationIndividual"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation(
            individual_crd_number
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            f"{url}/id/{individual_crd_number}",
            params={},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_registration_validation_data_with_params(self):
        url = self.base_url + \
              "/data/group/registration/name/registrationValidationIndividual"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        e = Client.IndividualRegistrationValidation
        
        fields = list(e)
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation(
            individual_crd_number,
            fields=fields,
            async_request=False
            )
        
        params = {
            "fields": ",".join([
                f.value for f in Client.IndividualRegistrationValidation
                ]),
            "async": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            f"{url}/id/{individual_crd_number}",
            params=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_individual_registration_validation_data_with_headers(self):
        url = self.base_url + \
              "/data/group/registration/name/registrationValidationIndividual"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation(
            individual_crd_number,
            version=1
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            f"{url}/id/{individual_crd_number}",
            params={},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_individual_registration_validation_data_no_individual_crd_number(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Registration Validation requires the first "
            "argument to be the individual_crd_number."
            ):
            self.client.get_individual_registration_validation()
        
    @no_duplicates
    def test_get_individual_registration_validation_data_wrong_fields_type(self):
        f = list(Client.IndividualRegistrationValidation)[0]
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.IndividualRegistrationValidation."
                f"{f.name}"
                )
            ):
            self.client.get_individual_registration_validation(
                1235467, fields=f.name
                )
        
    @no_duplicates
    def test_get_individual_registration_validation_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + \
              "/data/group/registration/name/registrationValidationIndividual"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        fields = [f.value for f in Client.IndividualRegistrationValidation]
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation(
            individual_crd_number,
            endpoint=Client.Endpoint.DATA.value,
            fields=fields
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            f"{url}/id/{individual_crd_number}",
            params={"fields": ",".join(fields)},
            headers={"Accept": "application/json"}
            )
        
    
    ##########################################################################
    # REGISTRATION - INDIVIDUAL REGISTRATION VALIDATION DETAILS
    
    @no_duplicates
    def test_get_individual_registration_validation_details_data_version_1(self):
        url = self.base_url + \
              "/data/group/registration/name/individualRegistrationValidationDetails"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation_details(
            individual_crd_number,
            version=1
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            f"{url}/id/{individual_crd_number}",
            params={},
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_individual_registration_validation_details_data_version_2(self):
        url = self.base_url + \
              "/data/group/registration/name/individualRegistrationValidationDetails"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation_details(
            individual_crd_number
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url,
            params={"individualCrdNumber": individual_crd_number},
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    def test_get_individual_registration_validation_details_data_with_params(self):
        url = self.base_url + \
              "/data/group/registration/name/individualRegistrationValidationDetails"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation_details(
            individual_crd_number,
            async_request=False
            )
        
        params = {
            "individualCrdNumber": individual_crd_number,
            "async": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url,
            params=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    def test_get_individual_registration_validation_details_data_no_individual_crd_number(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Individual Registration Validation Details requires "
            "the first argument to be the individual_crd_number."
            ):
            self.client.get_individual_registration_validation_details()
        
    @no_duplicates
    def test_get_individual_registration_validation_details_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + \
              "/data/group/registration/name/individualRegistrationValidationDetails"
        if self.mock:
            url += "Mock"
        self.mock_session.get.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_individual_registration_validation_details(
            individual_crd_number,
            endpoint=Client.Endpoint.DATA.value
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            url,
            params={"individualCrdNumber": individual_crd_number},
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    
    ##########################################################################
    # REGISTRATION - REGISTERED INDIVIDUAL SEARCH
    
    @no_duplicates
    def test_get_registered_individual_search_data_with_ssn(self):
        url = self.base_url + \
              "/data/group/registration/name/registeredIndividualSearch"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_registered_individual_search(
            DATE,
            ssn=SSN
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "ssn",
             "fieldValue": SSN,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    def test_get_registered_individual_search_data_with_last_name(self):
        url = self.base_url + \
              "/data/group/registration/name/registeredIndividualSearch"
        self.mock_session.post.return_value = self.response
        
        last_name = "Smith"
        result = self.client.get_registered_individual_search(
            DATE,
            last_name=last_name
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "lastName",
             "fieldValue": last_name,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    def test_get_registered_individual_search_data_with_first_name(self):
        url = self.base_url + \
              "/data/group/registration/name/registeredIndividualSearch"
        self.mock_session.post.return_value = self.response
        
        first_name = "John"
        result = self.client.get_registered_individual_search(
            DATE,
            first_name=first_name
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "firstName",
             "fieldValue": first_name,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    def test_get_registered_individual_search_data_with_headers(self):
        url = self.base_url + \
              "/data/group/registration/name/registeredIndividualSearch"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_registered_individual_search(
            DATE,
            ssn=SSN,
            version=1
            )
        
        params = {"compareFilters": [
            {"fieldName": "dateOfBirth",
             "fieldValue": datetime.datetime.combine(
                 DATE, datetime.datetime.min.time()
                 ).strftime("%m-%d"),
             "compareType": "EQUAL"},
            {"fieldName": "ssn",
             "fieldValue": SSN,
             "compareType": "EQUAL"},
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_registered_individual_search_data_with_params(self):
        url = self.base_url + \
              "/data/group/registration/name/registeredIndividualSearch"
        self.mock_session.post.return_value = self.response

        e = Client.RegisteredIndividualSearch
        
        fields = list(e)
        sort_fields = [((-1) ** i, f) for i, f in enumerate(e)]
        
        result = self.client.get_registered_individual_search(
            DATE,
            ssn=SSN,
            fields=fields,
            sort_fields=sort_fields,
            limit=100,
            offset=1,
            async_request=False
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "fields": [f.value for f in fields],
            "sortFields": [
                "-" + f.value if s < 0 else f.value for s, f in sort_fields
                ],
            "limit": 100,
            "offset": 1,
            "async": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    @no_duplicates
    def test_get_registered_individual_search_data_only_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Registered Individual Search requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "\\(2\\) last_name, or \\(3\\) first_name."
            ):
            self.client.get_registered_individual_search(DATE)
        
    @no_duplicates
    def test_get_registered_individual_search_data_no_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Registered Individual Search requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "\\(2\\) last_name, or \\(3\\) first_name."
            ):
            self.client.get_registered_individual_search(
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_registered_individual_search_data_wrong_date_of_birth_type_datetime(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_registered_individual_search(
                DATETIME,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_registered_individual_search_data_wrong_date_of_birth_type_string(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_registered_individual_search(
                DATE_ISO,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_registered_individual_search_data_wrong_fields_type(self):
        e = Client.RegisteredIndividualSearch
        f = next(iter(e))
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.RegisteredIndividualSearch."
                f"{f.name}"
                )
            ):
            self.client.get_registered_individual_search(
                DATE,
                ssn=SSN,
                fields=f.name
                )
        
    @no_duplicates
    def test_get_registered_individual_search_data_wrong_sort_fields_type(self):
        e = Client.RegisteredIndividualSearch
        with self.assertRaisesRegex(
            TypeError,
            "finra.base_client.BaseClient.RegisteredIndividualSearch"
            ):
            self.client.get_registered_individual_search(
                DATE,
                ssn=SSN,
                sort_fields=e.FIRST_NAME.value
                )
        
    @no_duplicates
    def test_get_registered_individual_search_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + \
              "/data/group/registration/name/registeredIndividualSearch"
        self.mock_session.post.return_value = self.response
        
        e = Client.RegisteredIndividualSearch
        
        fields = [f.value for f in e]
        sort_fields = [((-1) ** i, f.value) for i, f in enumerate(e)]
        
        result = self.client.get_registered_individual_search(
            DATE,
            ssn=SSN,
            endpoint=Client.Endpoint.DATA.value,
            fields=fields,
            sort_fields=sort_fields
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            "fields": fields,
            "sortFields": ["-" + f if s < 0 else f for s, f in sort_fields],
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "2"}
            )
        
    
    ##########################################################################
    # REGISTRATION - U4 FORM PREFILL
    
    @no_duplicates
    def test_get_u4_form_prefill_data_with_ssn(self):
        url = self.base_url + "/data/group/registration/name/u4FormPrefill"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_u4_form_prefill(
            DATE,
            ssn=SSN
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_u4_form_prefill_data_with_individual_crd_number(self):
        url = self.base_url + "/data/group/registration/name/u4FormPrefill"
        self.mock_session.post.return_value = self.response
        
        individual_crd_number = 1234567
        result = self.client.get_u4_form_prefill(
            DATE,
            individual_crd_number=individual_crd_number
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "individualCrdNumber",
                 "fieldValue": individual_crd_number,
                 "compareType": "EQUAL"},
                ],
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )
    
    @no_duplicates
    def test_get_u4_form_prefill_data_with_headers(self):
        url = self.base_url + "/data/group/registration/name/u4FormPrefill"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_u4_form_prefill(
            DATE,
            ssn=SSN,
            version=1
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_u4_form_prefill_data_only_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "U4 Form Prefill requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "or \\(2\\) individual_crd_number."
            ):
            self.client.get_u4_form_prefill(DATE)
        
    @no_duplicates
    def test_get_u4_form_prefill_data_no_date_of_birth(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "U4 Form Prefill requires the "
            "date_of_birth is provided \\(with an accurate month and "
            "day\\), and at least one of the following: \\(1\\) ssn "
            "\\(required if individual has a Social Security Number\\), "
            "or \\(2\\) individual_crd_number."
            ):
            self.client.get_u4_form_prefill(
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_u4_form_prefill_data_wrong_date_of_birth_type_datetime(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_u4_form_prefill(
                DATETIME,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_u4_form_prefill_data_wrong_date_of_birth_type_string(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            self.client.get_u4_form_prefill(
                DATE_ISO,
                ssn=SSN
                )
        
    @no_duplicates
    def test_get_u4_form_prefill_data_enums_not_required(self):
        self.client.set_require_enums(False)
        url = self.base_url + "/data/group/registration/name/u4FormPrefill"
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_u4_form_prefill(
            DATE,
            ssn=SSN,
            endpoint=Client.Endpoint.DATA.value,
            )
        
        params = {
            "compareFilters": [
                {"fieldName": "dateOfBirth",
                 "fieldValue": datetime.datetime.combine(
                     DATE, datetime.datetime.min.time()
                     ).strftime("%m-%d"),
                 "compareType": "EQUAL"},
                {"fieldName": "ssn",
                 "fieldValue": SSN,
                 "compareType": "EQUAL"},
                ],
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            url + "Mock" if self.mock else url,
            json=params,
            headers={"Accept": "application/json"}
            )

def _set_test_api_methods():
    
    # Set non-data endpoint methods for each dataset
    for method, (group, name, enum, partition_fields) in (
        EQUITY | FIXED_INCOME | FIXED_INCOME_JSON_ONLY | FINRA | FIRM |
        JSON_RESPONSE_DATA_TYPE_ONLY | REGISTRATION
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_metadata",
                 _test_metadata, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_metadata_with_headers",
                 _test_metadata_with_headers, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_partitions",
                 _test_partitions, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_partitions_with_headers",
                 _test_partitions_with_headers, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_datasets",
                 _test_datasets, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_wrong_endpoint_type",
                 _test_wrong_endpoint_type, method)
        
        set_meth(_TestAPI, f"test_{method}_unknown_endpoint_value",
                 _test_unknown_endpoint_value, method)
    
    # Fingerprint datasets use a different URL for all endpoints
    for method, (group, name, enum, partition_fields) in (
        REGISTRATION_FINGERPRINT
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_metadata",
                 _test_metadata, method, group, name, True)
        
        set_meth(_TestAPI, f"test_{method}_metadata_with_headers",
                 _test_metadata_with_headers, method, group, name, True)
        
        set_meth(_TestAPI, f"test_{method}_partitions",
                 _test_partitions, method, group, name, True)
        
        set_meth(_TestAPI, f"test_{method}_partitions_with_headers",
                 _test_partitions_with_headers, method, group, name, True)
        
        set_meth(_TestAPI, f"test_{method}_datasets",
                 _test_datasets, method, group, name, True)
        
        set_meth(_TestAPI, f"test_{method}_wrong_endpoint_type",
                 _test_wrong_endpoint_type, method)
        
        set_meth(_TestAPI, f"test_{method}_unknown_endpoint_value",
                 _test_unknown_endpoint_value, method)
        
    # Set data query methods for each dataset
    for method, (group, name, enum, partition_fields) in (
        EQUITY | FIXED_INCOME | FINRA | FIRM
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_get_data",
                 _test_get_data, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_headers",
                 _test_get_data_with_headers, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_text_params",
                 _test_get_data_with_text_params, method, group, name, enum)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_params",
                 _test_get_data_with_params, method, group, name, enum,
                 partition_fields)
        
        set_meth(_TestAPI, f"test_{method}_post_data",
                 _test_post_data, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_headers",
                 _test_post_data_with_headers, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_text_params",
                 _test_post_data_with_text_params, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_params",
                 _test_post_data_with_params, method, group, name, enum,
                 partition_fields)
        
        set_meth(_TestAPI, f"test_{method}_post_data_enums_not_required",
                 _test_post_data_enums_not_required, method, group, name, enum,
                 partition_fields)
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_fields_type",
                 _test_data_wrong_fields_type, method, enum)
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_sort_fields_type",
                 _test_data_wrong_sort_fields_type, method, enum,
                 partition_fields)
        
        if partition_fields:
            set_meth(_TestAPI,
                     f"test_{method}_data_fail_verify_sorting_partitions",
                     _test_data_fail_verify_sorting_partitions, method, enum,
                     partition_fields)
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_filters_type",
                 _test_data_wrong_filters_type, method)
        
    # Set data query methods for each dataset
    for method, (group, name, enum, partition_fields) in (
        FIXED_INCOME_JSON_ONLY
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_post_data",
                 _test_post_data, method, group, name,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_headers",
                 _test_post_data_with_headers_json_only, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_params",
                 _test_post_data_with_params_no_partition,
                 method, group, name, enum,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI,
                 f"test_{method}_post_data_enums_not_required",
                 _test_post_data_enums_not_required_no_partition,
                 method, group, name, enum,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_fields_type",
                 _test_data_wrong_fields_type, method, enum)
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_filters_type",
                 _test_data_wrong_filters_type, method)
        
    # Set methods that only support json response data type
    for method, (group, name, enum, partition_fields) in (
        JSON_RESPONSE_DATA_TYPE_ONLY
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_get_data",
                 _test_get_data, method, group, name,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_headers",
                 _test_get_data_with_headers_json_only, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_params",
                 _test_get_data_with_params, method, group, name, enum,
                 partition_fields, headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_post_data",
                 _test_post_data, method, group, name,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_headers",
                 _test_post_data_with_headers_json_only, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_params",
                 _test_post_data_with_params, method, group, name, enum,
                 partition_fields, headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_post_data_enums_not_required",
                 _test_post_data_enums_not_required, method, group, name, enum,
                 partition_fields, headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_fields_type",
                 _test_data_wrong_fields_type, method, enum)
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_sort_fields_type",
                 _test_data_wrong_sort_fields_type, method, enum,
                 partition_fields)
        
        if partition_fields:
            set_meth(_TestAPI,
                     f"test_{method}_data_fail_verify_sorting_partitions",
                     _test_data_fail_verify_sorting_partitions, method, enum,
                     partition_fields)
        
        set_meth(_TestAPI, f"test_{method}_data_wrong_filters_type",
                 _test_data_wrong_filters_type, method)
        
    # Set methods for single record query support - json response type only
    for method, (group, name, enum, partition_fields) in FIRM_WITH_ID.items():
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_id",
                 _test_get_data_with_id, method, group, name, 1234567,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_post_data_with_id",
                 _test_post_data_with_id, method, group, name, 1234567,
                 headers={"Accept": "application/json"})
        
    # Set data query methods for registration datasets
    for method in (
        "get_branch_list",
        "get_broker_dealer_firm_list",
        ):
        group, name, enum, partition_fields = REGISTRATION[method]
        
        set_meth(_TestAPI, f"test_{method}_data",
                 _test_get_data, method, group, name,
                 headers={"Accept": "application/json"})
        
        set_meth(_TestAPI, f"test_{method}_data_with_headers",
                 _test_get_data_with_headers_json_only, method, group, name)
        
        set_meth(_TestAPI, f"test_{method}_data_enums_not_required",
                 _test_get_data_enums_not_required, method, group, name,
                 headers={"Accept": "application/json"})
        
    # Set methods for TRACE report cards
    for method, (group, name, enum, partition_fields) in (
        REPORT_CARD_DETAILS
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_get_data",
                 _test_trace_get_data, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_version",
                 _test_trace_get_data_with_version, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_request_id",
                 _test_trace_get_data_with_request_id, method, group, name)
        
    for method, (group, name, enum, partition_fields) in (
        REPORT_CARD_SUMMARY
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_datasets",
                 _test_datasets, method, group, name, False)
        
        set_meth(_TestAPI, f"test_{method}_wrong_endpoint_type",
                 _test_trace_wrong_endpoint_type, method)
        
        set_meth(_TestAPI, f"test_{method}_unknown_endpoint_value",
                 _test_trace_unknown_endpoint_value, method)
        
        set_meth(_TestAPI, f"test_{method}_get_data",
                 _test_trace_get_data, method, group, name, True)
        
        set_meth(_TestAPI, f"test_{method}_get_data_with_version",
                 _test_trace_get_data_with_version, method, group, name, True)
        
    for method, (group, name, enum, partition_fields) in (
        REPORT_CARD_DETAILS | REPORT_CARD_SUMMARY
        ).items():
        
        set_meth(_TestAPI, f"test_{method}_get_data_no_period",
                 _test_trace_get_data_no_period, method)
        
        set_meth(_TestAPI, f"test_{method}_get_data_no_firm_market_id",
                 _test_trace_get_data_no_firm_market_id, method)
        
        set_meth(_TestAPI,
                 f"test_{method}_get_data_wrong_period_type_datetime",
                 _test_trace_get_data_wrong_period_type_datetime, method)
        
        set_meth(_TestAPI, f"test_{method}_get_data_wrong_period_type_string",
                 _test_trace_get_data_wrong_period_type_string, method)

_set_test_api_methods()


##############################################################################
# API METHODS WITHOUT MOCK SUPPORT

# Mixin class for success tests for query datasets that don't support Mock API
class _NoMockQuerySupport:
    
    
    ##########################################################################
    # EQUITY GROUP
    
    @no_duplicates
    def test_get_weekly_summary_historic_week_start_date(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(DATE)
        
        params = {"compareFilters": [{
            "fieldName": "weekStartDate",
            "fieldValue": DATE_ISO,
            "compareType": "EQUAL",
            }]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_wrong_week_start_date_type(self):
        with self.assertRaisesRegex(
            TypeError, "datetime.date, datetime.datetime"
            ):
            self.client.get_weekly_summary_historic(DATE_ISO)
        
    @no_duplicates
    def test_get_weekly_summary_historic_historical_week(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(
            historical_week=DATE
            )
        
        params = {"compareFilters": [{
            "fieldName": "historicalWeek",
            "fieldValue": DATE_ISO,
            "compareType": "EQUAL",
            }]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_wrong_historical_week_type(self):
        with self.assertRaisesRegex(
            TypeError, "datetime.date, datetime.datetime"
            ):
            self.client.get_weekly_summary_historic(historical_week=DATE_ISO)
        
    @no_duplicates
    def test_get_weekly_summary_historic_historical_month_datetime(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(
            historical_month=DATETIME
            )
        
        params = {"compareFilters": [{
            "fieldName": "historicalMonth",
            "fieldValue": DATETIME_ISO_MS[:7],
            "compareType": "EQUAL",
            }]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_historical_month_date(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(historical_month=DATE)
        
        params = {"compareFilters": [{
            "fieldName": "historicalMonth",
            "fieldValue": DATE_ISO[:7],
            "compareType": "EQUAL",
            }]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_wrong_historical_month_type(self):
        with self.assertRaisesRegex(
            TypeError, "datetime.date, datetime.datetime"
            ):
            self.client.get_weekly_summary_historic(
                historical_month=DATE_ISO
                )
        
    @no_duplicates
    def test_get_weekly_summary_historic_no_date(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, EXACTLY one "
            "of the following must be provided as a datetime.date: "
            "'week_start_date', 'historical_week', or 'historical_month'."
            ):
            self.client.get_weekly_summary_historic()
        
    @no_duplicates
    def test_get_weekly_summary_historic_data_with_tier_identifier(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(
            week_start_date=DATE,
            tier_identifier="tier id"
            )
        
        params = {"compareFilters": [
            {"fieldName": "weekStartDate", "fieldValue": DATE_ISO,
             "compareType": "EQUAL"},
            {"fieldName": "tierIdentifier", "fieldValue": "TIER ID",
             "compareType": "EQUAL"}
            ]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_wrong_tier_identifier_type(self):
        with self.assertRaisesRegex(TypeError, "builtins.str"):
            self.client.get_weekly_summary_historic(
                week_start_date=DATE,
                tier_identifier=Client.WeeklySummary.TIER_IDENTIFIER
                )
        
    @no_duplicates
    def test_get_weekly_summary_historic_data_with_headers(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(
            week_start_date=DATE,
            accept_json=False,
            version=1
            )
        
        params = {"compareFilters": [{
            "fieldName": "weekStartDate",
            "fieldValue": DATE_ISO,
            "compareType": "EQUAL",
            }]}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers={"Accept": "text/plain", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_data_with_text_params(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_weekly_summary_historic(
            week_start_date=DATE,
            delimiter="|",
            quote_values=False
            )
        
        params = {
            "compareFilters": [{
                "fieldName": "weekStartDate",
                "fieldValue": DATE_ISO,
                "compareType": "EQUAL",
                }],
            "delimiter": "|",
            "quoteValues": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_data_with_params(self):
        self.mock_session.post.return_value = self.response
        
        e = Client.WeeklySummary
        
        fields = list(e)
        
        result = self.client.get_weekly_summary_historic(
            week_start_date=DATE,
            fields=fields,
            limit=100,
            offset=1,
            async_request=False
            )
        
        params = {
            "compareFilters": [{
                "fieldName": "weekStartDate",
                "fieldValue": DATE_ISO,
                "compareType": "EQUAL",
                }],
            "fields": [f.value for f in e],
            "limit": 100,
            "offset": 1,
            "async": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_data_enums_not_required(self):
        self.client.set_require_enums(False)
        self.mock_session.post.return_value = self.response
        
        e = Client.WeeklySummary
        
        fields = [f.value for f in e]
        
        result = self.client.get_weekly_summary_historic(
            week_start_date=DATE,
            endpoint=Client.Endpoint.DATA.value,
            fields=fields,
            limit=100,
            offset=1,
            async_request=False
            )
        
        params = {
            "compareFilters": [{
                "fieldName": "weekStartDate",
                "fieldValue": DATE_ISO,
                "compareType": "EQUAL",
                }],
            "fields": fields,
            "limit": 100,
            "offset": 1,
            "async": False,
            }
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/otcMarket/name/weeklySummaryHistoric",
            json=params, headers=None
            )
        
    @no_duplicates
    def test_get_weekly_summary_historic_wrong_fields_type(self):
        e = Client.WeeklySummary
        f = next(iter(e))
        with self.assertRaisesRegex(
            TypeError, f"finra.base_client.BaseClient.WeeklySummary.{f.name}"
            ):
            self.client.get_weekly_summary_historic(DATE, fields=f.name)
        
    @no_duplicates
    def test_get_weekly_summary_historic_wrong_fields_enum_type(self):
        e = Client.WeeklySummary
        wrong_enum = Client.MonthlySummary.TIER_IDENTIFIER
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.WeeklySummary."
                f"{e.TIER_IDENTIFIER.name}"
                )
            ):
            self.client.get_weekly_summary_historic(DATE, fields=wrong_enum)
        
    
    ##########################################################################
    # REGISTRATION GROUP
    
    @no_duplicates
    def test_get_composite_individual_seed_get_data_with_version(self):
        self.mock_session.get.return_value = self.response
        
        result = self.client.get_composite_individual_seed(
            "requestId",
            version=2
            )
        
        self.assertEqual(result, self.response)
        self.mock_session.get.assert_called_once_with(
            self.base_url + "/v2" + \
            "/data/group/registration/name/compositeIndividualSeed/requestId",
            params={},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_individual_seed_get_data_no_sections_support(self):
        with self.assertRaisesRegex(
            ValueError, "Sections are not supported when checking status link"
            ):
            self.client.get_composite_individual_seed(
                "requestId", sections="Section"
                )
        
    @no_duplicates
    def test_get_composite_individual_seed_post_data(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_composite_individual_seed()
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/v1" + \
            "/data/group/registration/name/compositeIndividualSeed",
            json={}, headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_individual_seed_post_data_with_version(self):
        self.mock_session.post.return_value = self.response
        
        result = self.client.get_composite_individual_seed(version=2)
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/v2" + \
            "/data/group/registration/name/compositeIndividualSeed",
            json={},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_individual_seed_post_data_with_sections(self):
        self.mock_session.post.return_value = self.response
        
        e = Client.CompositeIndividualSections
        
        sections = list(e)
        
        result = self.client.get_composite_individual_seed(sections=sections)
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/v1" + \
            "/data/group/registration/name/compositeIndividualSeed",
            json={"sections": [s.value for s in sections]},
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_composite_individual_seed_post_data_wrong_sections_type(self):
        e = Client.CompositeIndividualSections
        f = next(iter(e))
        with self.assertRaisesRegex(
            TypeError, (
                "finra.base_client.BaseClient.CompositeIndividualSections."
                f"{f.name}"
                )
            ):
            self.client.get_composite_individual_seed(sections=f.name)

def _set_no_mock_query_support_methods():
    for method, (group, name, enum, partition_fields) in (
        EQUITY_NO_MOCK
        ).items():
        
        set_meth(_NoMockQuerySupport, f"test_{method}_metadata",
                 _test_metadata, method, group, name, False)
        
        set_meth(_NoMockQuerySupport, f"test_{method}_metadata_with_headers",
                 _test_metadata_with_headers, method, group, name, False)
        
        set_meth(_NoMockQuerySupport, f"test_{method}_partitions",
                 _test_partitions, method, group, name, False)
        
        set_meth(_NoMockQuerySupport, f"test_{method}_partitions_with_headers",
                 _test_partitions_with_headers, method, group, name, False)
        
        set_meth(_NoMockQuerySupport, f"test_{method}_datasets",
                 _test_datasets, method, group, name, False)
        
        set_meth(_NoMockQuerySupport, f"test_{method}_wrong_endpoint_type",
                 _test_wrong_endpoint_type, method)
        
        set_meth(_NoMockQuerySupport, f"test_{method}_unknown_endpoint_value",
                 _test_unknown_endpoint_value, method)

_set_no_mock_query_support_methods()


# Mixin class for fail tests for query datasets that don't support Mock API
class _MockQueryFail:
    pass

def _set_mock_query_fail_methods():
    for method in (EQUITY_NO_MOCK | REGISTRATION_NO_MOCK):
        set_meth(_MockQueryFail, f"test_{method}_no_mock",
                 _test_no_mock, method)

_set_mock_query_fail_methods()


##############################################################################
# NOTIFICATION API SUPPORT

# Mixin class for success tests on notification datasets
class _NotificationSupport:
    pass

def set_notification_support_methods():
    for method, (group, name) in NOTIFICATION.items():
        set_meth(_NotificationSupport, f"test_{method}",
                 _test_notification_get, method, group, name)
        
        set_meth(_NotificationSupport, f"test_{method}_with_version",
                 _test_notification_get_with_version, method, group, name)
        
        set_meth(_NotificationSupport, f"test_{method}_start_datetime",
                 _test_notification_get_start_datetime, method, group, name)
        
        set_meth(_NotificationSupport,
                 f"test_{method}_wrong_start_datetime_type",
                 _test_notification_wrong_start_datetime_type, method)
        
        set_meth(_NotificationSupport, f"test_{method}_end_datetime",
                 _test_notification_get_end_datetime, method, group, name)
        
        set_meth(_NotificationSupport,
                 f"test_{method}_wrong_end_datetime_type",
                 _test_notification_wrong_end_datetime_type, method)
        
        set_meth(_NotificationSupport, f"test_{method}_with_params",
                 _test_notification_get_with_params, method, group, name)

set_notification_support_methods()


# Mixin class for fail tests on notification datasets
class _MockNotificationFail:
    pass

def _set_mock_notification_fail_methods():
    for method in NOTIFICATION:
        set_meth(_MockNotificationFail, f"test_{method}_no_mock",
                 _test_no_mock, method)

_set_mock_notification_fail_methods()


##############################################################################
# SUBMISSION API SUPPORT

# Mixin class for success tests on submission filings
class _SubmissionSupport:
    
    
    ##########################################################################
    # NO UPDATE SUPPORT - MESSAGES ARE UNIQUE TO FILING
    
    @no_duplicates
    def test_create_individual_submission_filing_and_request_id_fail(self):
        with self.assertRaisesRegex(
            ValueError,
            "CreateIndividual does not support updates. Filing data "
            "can only be submitted. Provide either the request_id "
            "returned by a submission to retrieve the data again, or "
            "provide the CreateIndividual filing object \\(or data\\) to "
            "submit."
            ):
            self.client.create_individual_submission("requestID", filing={})
        
    @no_duplicates
    def test_non_registered_fingerprint_submission_filing_and_request_id_fail(self):
        with self.assertRaisesRegex(
            ValueError,
            "NonRegisteredFingerprint does not support updates. "
            "Filing data must be sent even for amendments. Filing data "
            "can also have just the delta changes for amendments. "
            "Provide either the request_id returned by a submission to "
            "retrieve the data, or provide the NonRegisteredFingerprint "
            "filing object \\(or data\\) to submit."
            ):
            self.client.non_registered_fingerprint_submission(
                "requestID", filing={}
                )

def _set_submission_support_methods():
    updatable = (
        "form_br_submission", "form_u4_submission", "form_u5_submission",
        )
    for method, (group, name, make_filing) in SUBMISSION.items():
        
        set_meth(_SubmissionSupport, f"test_{method}_get",
                 _test_submission_get, method, group, name)
        
        set_meth(_SubmissionSupport,
                 f"test_{method}_get_with_version_2",
                 _test_submission_get_with_version_2, method, group, name)
        
        set_meth(_SubmissionSupport,
                 f"test_{method}_no_filing_no_request_id",
                 _test_submission_no_filing_no_request_id, method)
        
        set_meth(_SubmissionSupport,
                 f"test_{method}_post_filing_obj",
                 _test_submission_post_filing_obj, method, group, name,
                 make_filing)
        
        set_meth(_SubmissionSupport, f"test_{method}_post_filing_json",
                 _test_submission_post_filing_json, method, group, name,
                 make_filing)
        
        # Filings that allow partial updates
        if method in updatable:
            
            set_meth(_SubmissionSupport,
                     f"test_{method}_post_missing_filing_data_ops",
                     _test_submission_post_missing_filing_data_ops, method,
                     make_filing)
            
            set_meth(_SubmissionSupport, f"test_{method}_delete",
                     _test_submission_delete, method, group, name)
            
            set_meth(_SubmissionSupport,
                     f"test_{method}_delete_with_filing",
                     _test_submission_delete_with_filing, method, group, name)
            
            set_meth(_SubmissionSupport, f"test_{method}_patch_filing",
                     _test_submission_patch_filing, method, group, name)
            
            set_meth(_SubmissionSupport, f"test_{method}_put_filing",
                     _test_submission_put_filing, method, group, name)

_set_submission_support_methods()


# Mixin class for fail tests on submission filings
class _MockSubmissionFail:
    pass

def _set_mock_submission_fail_methods():
    for method in SUBMISSION:
        set_meth(_MockSubmissionFail, f"test_{method}_no_mock",
                 _test_no_mock, method)

_set_mock_submission_fail_methods()


# Mixin class for client-only submission tests
class _SubmissionSupportClientOnly:
    pass

def _set_submission_support_client_only_methods():
    for method, (group, name, make_filing) in SUBMISSION.items():
        set_meth(_SubmissionSupportClientOnly,
                 f"test_{method}_validate_filing_obj",
                 _test_submission_validate_filing_obj, method, group, name,
                 make_filing
                 )
        
        set_meth(_SubmissionSupportClientOnly,
                 f"test_{method}_validate_filing_json",
                 _test_submission_validate_filing_json, method, group, name)
        
        set_meth(_SubmissionSupportClientOnly,
                 f"test_{method}_validate_filing_obj_with_schema_url",
                 _test_submission_validate_filing_obj_with_schema_url, method,
                 group, name, make_filing)
        
        set_meth(_SubmissionSupportClientOnly,
                 f"test_{method}_validate_filing_json_no_schema_url",
                 _test_submission_validate_filing_json_no_schema_url, method,
                 group, name)

_set_submission_support_client_only_methods()


# Mixin class for async-client-only submission tests
class _SubmissionSupportAsyncClientOnly:
    pass

def _set_submission_support_async_client_only_methods():
    for method in SUBMISSION:
        set_meth(_SubmissionSupportAsyncClientOnly,
                 f"test_{method}_validate_wrong_session_type",
                 _test_submission_validate_wrong_session_type, method)

_set_submission_support_async_client_only_methods()


##############################################################################
# QA TEST ENVIRONMENT SUPPORT

# Mixin class for success tests for QA Env only datasets
class _QAEnvOnly:
    
    
    ##########################################################################
    # REGISTRATION GROUP
    
    @no_duplicates
    def test_get_altered_ssn_and_dob_data(self):
        self.mock_session.post.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_altered_ssn_and_dob(individual_crd_number)
        
        params = {"metaData": {
            "individualCrdNumbers": [individual_crd_number],
            }}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/registration/name/alteredSSNandDOB",
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_altered_ssn_and_dob_data_multiple_individual_crd_numbers(self):
        self.mock_session.post.return_value = self.response
        
        individual_crd_numbers = [1235467, 8901234]
        result = self.client.get_altered_ssn_and_dob(*individual_crd_numbers)
        
        params = {"metaData": {
            "individualCrdNumbers": individual_crd_numbers,
            }}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/registration/name/alteredSSNandDOB",
            json=params,
            headers={"Accept": "application/json"}
            )
        
    @no_duplicates
    def test_get_altered_ssn_and_dob_data_with_headers(self):
        self.mock_session.post.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_altered_ssn_and_dob(
            individual_crd_number,
            version=1
            )
        
        params = {"metaData": {
            "individualCrdNumbers": [individual_crd_number],
            }}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/registration/name/alteredSSNandDOB",
            json=params,
            headers={"Accept": "application/json", "Data-Version": "1"}
            )
        
    @no_duplicates
    def test_get_altered_ssn_and_dob_data_no_individual_crd_number(self):
        with self.assertRaisesRegex(
            ValueError,
            "When querying the DATA resource endpoint, "
            "Altered SSN and DOB requires one or more "
            "individual_crd_numbers."
            ):
            self.client.get_altered_ssn_and_dob()
        
    @no_duplicates
    def test_get_altered_ssn_and_dob_data_too_many_individual_crd_numbers(self):
        individual_crd_numbers = [1235467, 8901234] * 13 # 26 > 25 numbers
        with self.assertRaisesRegex(
            ValueError,
            "Too many Individual CRD Numbers for request. "
            "Supports up to 25 per call."
            ):
            self.client.get_altered_ssn_and_dob(*individual_crd_numbers)
        
    @no_duplicates
    def test_get_altered_ssn_and_dob_data_enums_not_required(self):
        self.client.set_require_enums(False)
        self.mock_session.post.return_value = self.response
        
        individual_crd_number = 1235467
        result = self.client.get_altered_ssn_and_dob(
            individual_crd_number,
            endpoint=Client.Endpoint.DATA.value
            )
        
        params = {"metaData": {
            "individualCrdNumbers": [individual_crd_number],
            }}
        
        self.assertEqual(result, self.response)
        self.mock_session.post.assert_called_once_with(
            self.base_url + "/data/group/registration/name/alteredSSNandDOB",
            json=params,
            headers={"Accept": "application/json"}
            )

def _set_qa_env_only_methods():
    for method, (group, name, enum, partition_fields) in (
        REGISTRATION_QA_ONLY
        ).items():
        
        set_meth(_QAEnvOnly, f"test_{method}_metadata",
                 _test_metadata, method, group, name, False)
        
        set_meth(_QAEnvOnly, f"test_{method}_metadata_with_headers",
                 _test_metadata_with_headers, method, group, name, False)
        
        set_meth(_QAEnvOnly, f"test_{method}_partitions",
                 _test_partitions, method, group, name, False)
        
        set_meth(_QAEnvOnly, f"test_{method}_partitions_with_headers",
                 _test_partitions_with_headers, method, group, name, False)
        
        set_meth(_QAEnvOnly, f"test_{method}_datasets",
                 _test_datasets, method, group, name, False)
        
        set_meth(_QAEnvOnly, f"test_{method}_wrong_endpoint_type",
                 _test_wrong_endpoint_type, method)
        
        set_meth(_QAEnvOnly, f"test_{method}_unknown_endpoint_value",
                 _test_unknown_endpoint_value, method)

_set_qa_env_only_methods()


# Mixin class for environment fail test for QA Env only datasets, wrong env
class _QAEnvFail:
    pass

def set_qa_env_fail():
    for method in REGISTRATION_QA_ONLY:
        set_meth(_QAEnvFail, f"test_{method}_not_qa_env",
                 _test_not_qa_env, method)

set_qa_env_fail()


# Mixin class for mock fail test for QA Env datasets without mock support
class _QAEnvMockFail:
    pass

def set_qa_env_mock_fail():
    for method in REGISTRATION_QA_ONLY:
        set_meth(_QAEnvMockFail, f"test_{method}_no_mock",
                 _test_no_mock, method)

set_qa_env_mock_fail()


##############################################################################
# ENVIRONMENT

# Mixin subclass for testing production environment
class _TestProd(_TestAPI, _NoMockQuerySupport, _NotificationSupport,
                _SubmissionSupport, _QAEnvFail):
    mock = False # FINRA Mock API
    test_environment = False # FINRA QA Test Environment
    base_url = "https://api.finra.org"
    fingerprint_url = "https://fingerprints.finra.org"
    
    @no_duplicates
    def test_base_url(self):
        self.assertEqual(self.client.base_url, self.base_url)
        
    @no_duplicates
    def test_mock(self):
        self.assertFalse(self.client.mock)
        
    @no_duplicates
    def test_test_environment(self):
        self.assertFalse(self.client.test_environment)
    

# Mixin subclass for testing production Mock API
class _TestMock(_TestAPI, _MockQueryFail, _MockNotificationFail,
                _MockSubmissionFail, _QAEnvFail):
    mock = True # FINRA Mock API
    test_environment = False # FINRA QA Test Environment
    base_url = "https://api.finra.org"
    fingerprint_url = "https://fingerprints.finra.org"
    
    @no_duplicates
    def test_base_url(self):
        self.assertEqual(self.client.base_url, self.base_url)
        
    @no_duplicates
    def test_mock(self):
        self.assertTrue(self.client.mock)
        
    @no_duplicates
    def test_test_environment(self):
        self.assertFalse(self.client.test_environment)


# Mixin subclass for testing QA Test Environment
class _TestQAEnv(_TestAPI, _NoMockQuerySupport, _NotificationSupport,
                 _SubmissionSupport, _QAEnvOnly):
    mock = False # FINRA Mock API
    test_environment = True # FINRA QA Test Environment
    base_url = "https://api-int.qa.finra.org"
    fingerprint_url = "https://fingerprints-qaint.finrafp.qa.finra.org"
    
    @no_duplicates
    def test_base_url(self):
        self.assertEqual(self.client.base_url, self.base_url)
        
    @no_duplicates
    def test_mock(self):
        self.assertFalse(self.client.mock)
        
    @no_duplicates
    def test_test_environment(self):
        self.assertTrue(self.client.test_environment)


# Mixin subclass for testing QA Test Environment with Mock datasets
class _TestQAEnvMock(_TestAPI, _MockQueryFail, _NotificationSupport,
                     _SubmissionSupport, _QAEnvMockFail):
    mock = True # FINRA Mock API
    test_environment = True # FINRA QA Test Environment
    base_url = "https://api-int.qa.finra.org"
    fingerprint_url = "https://fingerprints-qaint.finrafp.qa.finra.org"
    
    @no_duplicates
    def test_base_url(self):
        self.assertEqual(self.client.base_url, self.base_url)
        
    @no_duplicates
    def test_mock(self):
        self.assertTrue(self.client.mock)
        
    @no_duplicates
    def test_test_environment(self):
        self.assertTrue(self.client.test_environment)


##############################################################################
# TEST CLIENT BASE

# Mixin class for testing functionality common to both Client & AsyncClient
class _TestClientBase:
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patch_register_redactions = \
            patch("finra.base_client.register_redactions")
        cls.patch_register_redactions_from_response = \
            patch("finra.base_client.register_redactions_from_response")
        
        cls.mock_register_redactions = cls.patch_register_redactions.start()
        cls.mock_register_redactions_from_response = \
            cls.patch_register_redactions_from_response.start()
        
    @classmethod
    def tearDownClass(cls):
        cls.patch_register_redactions_from_response.stop()
        cls.patch_register_redactions.stop()
        super().tearDownClass()
        
    def setUp(self):
        super().setUp()
        self.mock_session = self.mock_cls(spec=self.session_cls)
        self.mock_session.headers = {}
        
        self.response = httpx.Response(200)
        
        self.client = self.client_cls(
            API_KEY,
            self.mock_session,
            mock=self.mock,
            test_environment=self.test_environment
            )
        
        # Set logging level to DEBUG to force evaluation of all messages
        base_client.get_logger().setLevel("DEBUG")
        
    def _test_set_resource_session(self, httpx_client):
        self.client._session = httpx_client
        
        self.assertEqual(getattr(self.client, "_resource_session", None), None)
        
        self.client._set_resource_session()
        
        self.assertEqual(
            self.client._resource_session.__class__, httpx_client.__class__
            )
        self.assertEqual(
            self.client._resource_session.timeout, httpx_client.timeout
            )
        
    @no_duplicates
    @patch("time.time", Mock(return_value=NOW))
    def test_refresh_token(self):
        new_token = {"new_token": "1"}
        self.mock_session.fetch_token = self.mock_cls(return_value=new_token)
        
        token_manager = MagicMock()
        
        client = self.client_cls(
            API_KEY, self.mock_session, token_manager=token_manager
            )
        
        client.refresh_token()
        
        self.mock_session.fetch_token.assert_called_once()
        
        session_call = self.mock_register_redactions.mock_calls[-1]
        self.assertEqual(session_call[1], (new_token,))
        
        self.assertEqual(token_manager.created_timestamp, NOW)
        token_manager.update_token.assert_called_once_with(new_token)
        
    @no_duplicates
    def test_refresh_token_no_token_manager(self):
        self.mock_session.fetch_token = self.mock_cls(return_value="token")
        with self.assertRaisesRegex(ValueError, "Token Manager not set"):
            self.client.refresh_token()


##############################################################################
# CLIENT TEST CASES

# Mixin for testing synchronous Client
class _TestClient:
    mock_cls = MagicMock
    client_cls = Client
    session_cls = OAuth2Client


# The test cases for synchronous Client
class TestClient(
    _TestNonAPI, _TestProd, _SubmissionSupportClientOnly,
    _TestClient, _TestClientBase, unittest.TestCase
    ):
    
    @no_duplicates
    def test_schema_registry(self):
        self.assertEqual(self.client.schema_registry, {})
        
    @no_duplicates
    def test_set_resource_session(self):
        self._test_set_resource_session(httpx.Client())
        
    @no_duplicates
    @patch("httpx.Client")
    def test_get_async_result_no_resource_session(self, httpx_client):
        httpx_client.return_value = httpx_client
        httpx_client.get.return_value = self.response
        
        result = self.client.get_async_result("result link")
        
        self.assertEqual(result, self.response)
        httpx_client.get.assert_called_once_with(
            "result link", params=None, headers=None
            )
        
    @no_duplicates
    def test_close(self):
        self.client.close()
        
        self.mock_session.close.assert_called_once()
        
    @no_duplicates
    def test_close_resource_session(self):
        self.client._resource_session = self.mock_session
        
        self.client.close()
        
        self.assertEqual(len(self.mock_session.mock_calls), 2)
        
    @no_duplicates
    def test_client_context(self):
        with self.client_cls(
            API_KEY,
            self.mock_session,
            mock=self.mock,
            test_environment=self.test_environment
            ):
            pass
        
        self.mock_session.close.assert_called_once()
        
    @no_duplicates
    def test_wrong_session_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "Unknown session type AsyncOAuth2Client, expected a subclass of "
            "authlib.integrations.httpx_client.OAuth2Client"
            ):
            self.client_cls(API_KEY, AsyncOAuth2Client())


class TestClientMock(
    _TestMock, _TestClient, _TestClientBase, unittest.TestCase
    ):
    pass


class TestClientQAEnv(
    _TestQAEnv, _SubmissionSupportClientOnly,
    _TestClient, _TestClientBase, unittest.TestCase
    ):
    pass


class TestClientQAEnvMock(
    _TestQAEnvMock, _SubmissionSupportClientOnly,
    _TestClient, _TestClientBase, unittest.TestCase
    ):
    pass


##############################################################################
# ASYNC CLIENT TEST CASES

# Re-synchronizes every async function on a given object.
# NOTE: Every method runs on a new loop
class AsyncResync:
    class _AsyncResyncMethod:
        def __init__(self, func):
            self.func = func
            
        def __call__(self, *args, **kwargs):
            coroutine = self.func(*args, **kwargs)
            loop = asyncio.new_event_loop()
            try:
                out = loop.run_until_complete(coroutine)
            finally:
                loop.close()
            return out
        
    def __getattr__(self, attr, *not_callable_attrs):
        out = super().__getattribute__(attr)
        if inspect.iscoroutinefunction(out) and \
           attr not in self.not_callable_attrs:
            return self._AsyncResyncMethod(out)
        return out
    
    __getattribute__ = __getattr__


# Proxies the underlying class, replacing coroutine methods with an
# auto-executing one. Also allows a set of non-callable attributes to be set.
class ResyncProxy:
    def __init__(self, cls, *not_callable_attrs):
        self.cls = cls
        self.cls.not_callable_attrs = not_callable_attrs
        
    # Forces a mixin of the underlying class and the AsyncResync class
    def __call__(self, *args, **kwargs):
        class DynamicResync(AsyncResync, self.cls):
            pass
        
        return DynamicResync(*args, **kwargs)


# Mixin for testing asynchronous AsyncClient
class _TestAsyncClient(_TestClientBase):
    mock_cls = AsyncMock
    client_cls = ResyncProxy(AsyncClient, "_session", "_resource_session")
    session_cls = AsyncOAuth2Client


# The test cases for asynchronous AsyncClient
class TestAsyncClient(
    _TestNonAPI, _TestProd, _SubmissionSupportAsyncClientOnly,
    _TestAsyncClient, _TestClientBase, unittest.TestCase
    ):
    
    @no_duplicates
    def test_set_resource_session(self):
        self._test_set_resource_session(httpx.AsyncClient())
        
    @no_duplicates
    @patch("httpx.AsyncClient", new_callable=Mock)
    def test_get_async_result_no_resource_session(self, httpx_client):
        httpx_client.return_value = httpx_client
        
        mock = AsyncMock()
        mock.return_value = self.response
        
        httpx_client.get = mock
        
        result = self.client.get_async_result("result link")
        
        self.assertEqual(result, self.response)
        httpx_client.get.assert_called_once_with(
            "result link", params=None, headers=None
            )
        
    @no_duplicates
    def test_close(self):
        self.client.close()
        
        self.mock_session.aclose.assert_called_once()
        
    @no_duplicates
    def test_close_resource_session(self):
        self.client._resource_session = self.mock_session
        
        self.client.close()
        
        self.assertEqual(len(self.mock_session.aclose.mock_calls), 2)
        
    @no_duplicates
    def test_client_context(self):
        async def _test_context():
            async with AsyncClient(
                API_KEY,
                self.mock_session,
                mock=self.mock,
                test_environment=self.test_environment
                ):
                pass
        
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_test_context())
        loop.close()
        
        self.mock_session.aclose.assert_called_once()
        
    @no_duplicates
    def test_wrong_session_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "Unknown session type OAuth2Client, expected a subclass of "
            "authlib.integrations.httpx_client.AsyncOAuth2Client"
            ):
            self.client_cls(API_KEY, OAuth2Client())


class TestAsyncClientMock(
    _TestMock, _TestAsyncClient, _TestClientBase, unittest.TestCase
    ):
    pass


class TestAsyncClientQAEnv(
    _TestQAEnv, _SubmissionSupportAsyncClientOnly,
    _TestAsyncClient, _TestClientBase, unittest.TestCase
    ):
    pass


class TestAsyncClientQAEnvMock(
    _TestQAEnvMock, _SubmissionSupportAsyncClientOnly,
    _TestAsyncClient, _TestClientBase, unittest.TestCase
    ):
    pass

