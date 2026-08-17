import json
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

import httpx

from finra import utils
from finra import _enums
from finra import _utils as time_utils

from .common import no_duplicates


DATE = date(2026, 1, 2)
DATETIME = datetime(2026, 1, 2, 3, 4, 5)
DATETIME_UTC = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
DATETIME_ET = datetime(2026, 1, 1, 22, 4, 5)
DATETIME_TRUNCATED = datetime(2026, 1, 2, 0, 0, 0)

DATE_ISO = '2026-01-02'
DATETIME_ISO = '2026-01-02T03:04:05.000Z'

DATE_OF_BIRTH = date(1969, 7, 20)
DATE_OF_BIRTH_ISO = '1969-07-20'


##############################################################################
# TIME

class TestTimeUtils(unittest.TestCase):

    @no_duplicates
    def test_date_isoformat_from_date(self):
        self.assertEqual(time_utils.date_isoformat(DATE), DATE_ISO)
        
    @no_duplicates
    def test_date_isoformat_from_datetime(self):
        self.assertEqual(time_utils.date_isoformat(DATETIME), DATE_ISO)
        
    @no_duplicates
    def test_date_isoformat_from_timezone_aware(self):
        dt = DATETIME.replace(tzinfo=ZoneInfo('America/New_York'))
        self.assertEqual(time_utils.date_isoformat(dt), DATE_ISO)
        
    @no_duplicates
    def test_datetime_isoformat_ms(self):
        self.assertEqual(
            time_utils.datetime_isoformat_ms(DATETIME, 'T', 'Z'), DATETIME_ISO
            )
        
    @no_duplicates
    def test_datetime_isoformat_ms_with_utc(self):
        self.assertEqual(
            time_utils.datetime_isoformat_ms(DATETIME_UTC, 'T', 'Z'),
            DATETIME_ISO
            )
        
    @no_duplicates
    def test_datetime_isoformat_ms_from_timezone_aware(self):
        dt = DATETIME.replace(tzinfo=ZoneInfo('America/New_York'))
        self.assertEqual(
            time_utils.datetime_isoformat_ms(dt, 'T', 'Z'), DATETIME_ISO
            )
        
    @no_duplicates
    def test_datetime_naive_from_date(self):
        self.assertEqual(time_utils.datetime_naive(DATE), DATETIME_TRUNCATED)
        
    @no_duplicates
    def test_datetime_naive_from_datetime(self):
        self.assertEqual(time_utils.datetime_naive(DATETIME), DATETIME)
        
    @no_duplicates
    def test_datetime_naive_from_timezone_aware_to_utc(self):
        self.assertEqual(time_utils.datetime_naive(DATETIME_UTC), DATETIME)
        
    @no_duplicates
    def test_datetime_naive_from_timezone_aware_across_dst(self):
        self.assertEqual(
            time_utils.datetime_naive(
                DATETIME_UTC, ZoneInfo('America/New_York')
                ),
            DATETIME_ET
            )
        
    @no_duplicates
    def test_lazy_log(self):
        data = json.dumps({'data': 1}, indent=4)
        lazy = time_utils.LazyLog(lambda: data)
        self.assertEqual(data, str(lazy))


##############################################################################
# HEADER

class TestHeaderUtils(unittest.TestCase):
    def setUp(self):
        self.headers = {
            'Content-Type': 'test content type',
            'FINRA-api-request-id': 'test FINRA api request id',
            'Record-Total': '12345',
            'Record-Limit': '123',
            'Record-Offset': '45',
            'Total-Records-On-Page': '23',
            'Record-Max-Limit': '1234',
            'Response-Payload-Max-Size': '10MB',
            'Location': 'https://check.status.url',
            }
        self.response = httpx.Response(200, headers=self.headers)
        
    @no_duplicates
    def test_extract_content_type(self):
        self.assertEqual(
            utils.extract_content_type(self.response),
            self.headers['Content-Type']
            )
        
    @no_duplicates
    def test_extract_finra_api_request_id(self):
        self.assertEqual(
            utils.extract_finra_api_request_id(self.response),
            self.headers['FINRA-api-request-id']
            )
        
    @no_duplicates
    def test_extract_record_total(self):
        self.assertEqual(
            utils.extract_record_total(self.response),
            int(self.headers['Record-Total'])
            )
        
    @no_duplicates
    def test_extract_record_total_none(self):
        del self.response.headers['Record-Total']
        self.assertEqual(
            utils.extract_record_total(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_total_empty_string(self):
        self.response.headers['Record-Total'] = ''
        self.assertEqual(
            utils.extract_record_total(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_limit(self):
        self.assertEqual(
            utils.extract_record_limit(self.response),
            int(self.headers['Record-Limit'])
            )
        
    @no_duplicates
    def test_extract_record_limit_none(self):
        del self.response.headers['Record-Limit']
        self.assertEqual(
            utils.extract_record_limit(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_limit_empty_string(self):
        self.response.headers['Record-Limit'] = ''
        self.assertEqual(
            utils.extract_record_limit(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_offset(self):
        self.assertEqual(
            utils.extract_record_offset(self.response),
            int(self.headers['Record-Offset'])
            )
        
    @no_duplicates
    def test_extract_record_offset_none(self):
        del self.response.headers['Record-Offset']
        self.assertEqual(
            utils.extract_record_offset(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_offset_empty_string(self):
        self.response.headers['Record-Offset'] = ''
        self.assertEqual(
            utils.extract_record_offset(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_total_records_on_page(self):
        self.assertEqual(
            utils.extract_total_records_on_page(self.response),
            int(self.headers['Total-Records-On-Page'])
            )
        
    @no_duplicates
    def test_extract_total_records_on_page_none(self):
        del self.response.headers['Total-Records-On-Page']
        self.assertEqual(
            utils.extract_total_records_on_page(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_total_records_on_page_empty_string(self):
        self.response.headers['Total-Records-On-Page'] = ''
        self.assertEqual(
            utils.extract_total_records_on_page(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_max_limit(self):
        self.assertEqual(
            utils.extract_record_max_limit(self.response),
            int(self.headers['Record-Max-Limit'])
            )
        
    @no_duplicates
    def test_extract_record_max_limit_none(self):
        del self.response.headers['Record-Max-Limit']
        self.assertEqual(
            utils.extract_record_max_limit(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_record_max_limit_empty_string(self):
        self.response.headers['Record-Max-Limit'] = ''
        self.assertEqual(
            utils.extract_record_max_limit(self.response),
            None
            )
        
    @no_duplicates
    def test_extract_response_payload_max_size(self):
        self.assertEqual(
            utils.extract_response_payload_max_size(self.response),
            self.headers['Response-Payload-Max-Size']
            )
        
    @no_duplicates
    def test_extract_location(self):
        self.assertEqual(
            utils.extract_location(self.response),
            self.headers['Location']
            )


##############################################################################
# ASYNCHRONOUS REQUEST

class TestAsyncRequestUtils(unittest.TestCase):
    def setUp(self):
        self.json = {
            'status': 'test status',
            'resultLink': 'https://result.link.url',
            'expires': '2026-01-02 03:04:05 UTC',
            'checkStatusLink': 'https://check.status.link.url',
            'requestId': 'test request id',
            'requestTimestamp': '2026-02-03 04:05:06 UTC',
            'errorMessages': ['error message'],
            }
        self.response = httpx.Response(200, json=self.json)
        
    @no_duplicates
    def test_extract_response_field_from_json(self):
        self.assertEqual(
            utils._extract_response_field(self.response.json(), 'status'),
            self.json['status']
            )
        
    @no_duplicates
    def test_extract_status(self):
        self.assertEqual(
            utils.extract_status(self.response),
            self.json['status']
            )
        
    @no_duplicates
    def test_extract_result_link(self):
        self.assertEqual(
            utils.extract_result_link(self.response),
            self.json['resultLink']
            )
        
    @no_duplicates
    def test_extract_expires(self):
        self.assertEqual(
            utils.extract_expires(self.response),
            DATETIME_UTC
            )
        
    @no_duplicates
    def test_extract_expires_none(self):
        json = self.response.json()
        del json['expires']
        self.assertEqual(
            utils.extract_expires(json),
            None
            )
        
    @no_duplicates
    def test_extract_check_status_link(self):
        self.assertEqual(
            utils.extract_check_status_link(self.response),
            self.json['checkStatusLink']
            )
        
    @no_duplicates
    def test_extract_request_id(self):
        self.assertEqual(
            utils.extract_request_id(self.response),
            self.json['requestId']
            )
        
    @no_duplicates
    def test_extract_request_timestamp(self):
        self.assertEqual(
            utils.extract_request_timestamp(self.response),
            self.json['requestTimestamp']
            )
        
    @no_duplicates
    def test_extract_error_messages(self):
        self.assertEqual(
            utils.extract_error_messages(self.response),
            self.json['errorMessages']
            )


##############################################################################
# SUBMISSION API REQUEST

class TestSubmissionRequestUtils(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            'filingStatus': 'test filing status',
            'filingId': 'test filing id',
            'filingType': 'test filing type',
            'resultStatus': 'test result status',
            'resultStatusDesc': {
                'message': 'test result status desc message',
                'errors': ['test error message'],
                'warnings': ['test warning message'],
                },
            'created': {'by': 'test user', 'on': DATETIME_ISO},
            'updated': {'by': 'test user', 'on': DATETIME_ISO},
            'submitted': {'by': 'test user', 'on': DATETIME_ISO},
            'branchId': '12345',
            'individualCrdNumber': '1234567',
            'dateOfBirth': DATE_OF_BIRTH_ISO,
            }
        self.filing_data = {'test': 'data'}
        self.json = {
            'id': 'test filing request id',
            'group': 'test filing group',
            'name': 'test filing name',
            'filing': {
                'metadata': self.metadata,
                'filingData': self.filing_data,
                }
            }
        self.response = httpx.Response(200, json=self.json)
        
    @no_duplicates
    def test_extract_filing_request_id(self):
        self.assertEqual(
            utils.extract_filing_request_id(self.response),
            self.json['id']
            )
        
    @no_duplicates
    def test_extract_filing_group(self):
        self.assertEqual(
            utils.extract_filing_group(self.response),
            self.json['group']
            )
        
    @no_duplicates
    def test_extract_filing_name(self):
        self.assertEqual(
            utils.extract_filing_name(self.response),
            self.json['name']
            )
        
    @no_duplicates
    def test_extract_filing_data(self):
        self.assertEqual(
            utils.extract_filing_data(self.response),
            self.filing_data
            )
        
    @no_duplicates
    def test_extract_filing_data_none(self):
        json = self.response.json()
        del json['filing']['filingData']
        self.assertEqual(
            utils.extract_filing_data(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_data_no_filing(self):
        json = self.response.json()
        del json['filing']
        self.assertEqual(
            utils.extract_filing_data(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_metadata(self):
        self.assertEqual(
            utils.extract_filing_metadata(self.response),
            self.metadata
            )
        
    @no_duplicates
    def test_extract_filing_metadata_none(self):
        json = self.response.json()
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_metadata(json),
            None
            )
        
    @no_duplicates
    def test_extract_metadata_no_filing(self):
        json = self.response.json()
        del json['filing']
        self.assertEqual(
            utils.extract_filing_metadata(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_status(self):
        self.assertEqual(
            utils.extract_filing_status(self.response),
            self.metadata['filingStatus']
            )
        
    @no_duplicates
    def test_extract_filing_status_none(self):
        json = self.response.json()
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_status(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_id(self):
        self.assertEqual(
            utils.extract_filing_id(self.response),
            self.metadata['filingId']
            )
        
    @no_duplicates
    def test_extract_filing_id_none(self):
        json = self.response.json()
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_id(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_type(self):
        self.assertEqual(
            utils.extract_filing_type(self.response),
            self.metadata['filingType']
            )
        
    @no_duplicates
    def test_extract_filing_type_none(self):
        json = self.response.json()
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_type(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_result_status(self):
        self.assertEqual(
            utils.extract_filing_result_status(self.response),
            self.metadata['resultStatus']
            )
        
    @no_duplicates
    def test_extract_filing_result_status_none(self):
        json = self.response.json()
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_result_status(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_result_status_desc(self):
        self.assertEqual(
            utils.extract_filing_result_status_desc(self.response),
            self.metadata['resultStatusDesc']
            )
        
    @no_duplicates
    def test_extract_filing_result_status_desc_none(self):
        json = self.response.json()
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_result_status_desc(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_created(self):
        created = self.metadata['created'].copy()
        created['on'] = DATETIME_UTC
        self.assertEqual(
            utils.extract_filing_created(self.response),
            created
            )
        
    @no_duplicates
    def test_extract_filing_created_none(self):
        json = self.response.json()
        del json['filing']['metadata']['created']
        self.assertEqual(
            utils.extract_filing_created(json),
            None
            )
        
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_created(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_updated(self):
        updated = self.metadata['updated'].copy()
        updated['on'] = DATETIME_UTC
        self.assertEqual(
            utils.extract_filing_updated(self.response),
            updated
            )
        
    @no_duplicates
    def test_extract_filing_updated_none(self):
        json = self.response.json()
        del json['filing']['metadata']['updated']
        self.assertEqual(
            utils.extract_filing_updated(json),
            None
            )
        
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_updated(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_submitted(self):
        submitted = self.metadata['submitted'].copy()
        submitted['on'] = DATETIME_UTC
        self.assertEqual(
            utils.extract_filing_submitted(self.response),
            submitted
            )
        
    @no_duplicates
    def test_extract_filing_submitted_none(self):
        json = self.response.json()
        del json['filing']['metadata']['submitted']
        self.assertEqual(
            utils.extract_filing_submitted(json),
            None
            )
        
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_submitted(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_individual_crd_number(self):
        self.assertEqual(
            utils.extract_filing_individual_crd_number(self.response),
            int(self.metadata['individualCrdNumber'])
            )
        
    @no_duplicates
    def test_extract_filing_individual_crd_number_none(self):
        json = self.response.json()
        del json['filing']['metadata']['individualCrdNumber']
        self.assertEqual(
            utils.extract_filing_individual_crd_number(json),
            None
            )
        
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_individual_crd_number(json),
            None
            )
        
    @no_duplicates
    def test_extract_filing_date_of_birth(self):
        self.assertEqual(
            utils.extract_filing_date_of_birth(self.response),
            DATE_OF_BIRTH
            )
        
    @no_duplicates
    def test_extract_filing_date_of_birth_none(self):
        json = self.response.json()
        del json['filing']['metadata']['dateOfBirth']
        self.assertEqual(
            utils.extract_filing_date_of_birth(json),
            None
            )
        
        del json['filing']['metadata']
        self.assertEqual(
            utils.extract_filing_date_of_birth(json),
            None
            )


##############################################################################
# RELABELING RESPONSE

class TestRelabelJSON(unittest.TestCase):
    def setUp(self):
        self.enum = _enums.FirmDisclosures
        
    @no_duplicates
    def test_expand_relabel_map_from_enum_type(self):
        labels = {
            'firmCrdNumber': 'FIRM_CRD_NUMBER',
            'disclosures': {
                'disclosureType': 'DISCLOSURE_TYPE',
                'occurrenceNumber': 'OCCURRENCE_NUMBER',
                'reportableFlag': 'REPORTABLE_FLAG',
                'disclosableFlag': 'DISCLOSABLE_FLAG',
                'archivedFlag': 'ARCHIVED_FLAG',
                'eventDate': 'EVENT_DATE',
                },
            'registrations': {
                'regulatorCode': 'REGULATOR_CODE',
                }
            } # order matches enum
        
        relabeler = utils.RelabelJSON(self.enum)
        
        self.assertEqual(relabeler.labels, labels)
        
    @no_duplicates
    def test_expand_relabel_map_from_mapping(self):
        labels = {
            'firmCrdNumber': 'TEST_LABEL',
            'disclosures': {
                'eventDate': 'TEST DATE',
                },
            }
        
        relabeler = utils.RelabelJSON(labels)
        
        self.assertEqual(relabeler.labels, labels)
        
    @no_duplicates
    def test_expand_relabel_map_from_mapping_wrong_key_type(self):
        labels = {1: 'wrong type'}
        with self.assertRaisesRegex(
            TypeError, "Relabel mapping can only have string-valued keys"
            ):
            utils.RelabelJSON(labels)
        
    @no_duplicates
    def test_order_labels(self):
        ordered = {
            'FIRM_CRD_NUMBER': None,
            'disclosures': {
                'DISCLOSURE_TYPE': None,
                'OCCURRENCE_NUMBER': None,
                'REPORTABLE_FLAG': None,
                'DISCLOSABLE_FLAG': None,
                'ARCHIVED_FLAG': None,
                'EVENT_DATE': None,
                },
            'registrations': {
                'REGULATOR_CODE': None,
                },
            }
        
        relabeler = utils.RelabelJSON(self.enum)
        
        self.assertEqual(relabeler.obj_labels, {})
        
        label_order = utils._order_labels(relabeler.labels, {}, {})
        
        self.assertEqual(label_order, ordered)
        self.assertEqual(list(label_order), list(ordered))
        self.assertEqual(
            list(label_order['disclosures']), list(ordered['disclosures'])
            )
        
    @no_duplicates
    def test_order_labels_with_obj_labels(self):
        obj_labels = {
            'registrations': 'REGISTRATIONS',
            'disclosures': 'DISCLOSURES',
            } # different order than labels order
        
        ordered = {
            'DISCLOSURES': {
                'DISCLOSURE_TYPE': None,
                'OCCURRENCE_NUMBER': None,
                'REPORTABLE_FLAG': None,
                'DISCLOSABLE_FLAG': None,
                'ARCHIVED_FLAG': None,
                'EVENT_DATE': None,
                },
            'REGISTRATIONS': {
                'REGULATOR_CODE': None,
                },
            'FIRM_CRD_NUMBER': None,
            } # labels (enum) order preserved
        
        relabeler = utils.RelabelJSON(self.enum, obj_labels)
        
        relabeler.labels['firmCrdNumber'] = \
            relabeler.labels.pop('firmCrdNumber') # move to end
        
        self.assertEqual(relabeler.obj_labels, obj_labels)
        
        label_order = utils._order_labels(relabeler.labels, obj_labels, {})
        
        self.assertEqual(label_order, ordered)
        self.assertEqual(list(label_order), list(ordered))
        self.assertEqual(
            list(label_order['DISCLOSURES']), list(ordered['DISCLOSURES'])
            )
        
    def _assert_response_label_order(self, r, event_date):
        for d in r:
            keys = list(d.keys())
            self.assertEqual(
                keys,
                ['FIRM_CRD_NUMBER', 'disclosures', 'registrations']
                ) # keep order of labels sub-mappings even though no obj_labels
            for r in d['disclosures']:
                keys = list(r.keys())
                self.assertEqual(
                    keys,
                    ['DISCLOSURE_TYPE', 'OCCURRENCE_NUMBER', 'REPORTABLE_FLAG',
                     'DISCLOSABLE_FLAG', 'ARCHIVED_FLAG', event_date]
                    )
            for r in d['registrations']:
                keys = list(r.keys())
                self.assertEqual(keys, ['REGULATOR_CODE'])
        
    @no_duplicates
    def test_relabel_from_response(self):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        
        relabeler = utils.RelabelJSON(self.enum)
        r = relabeler(httpx.Response(200, json=response_json))
        self._assert_response_label_order(r, 'EVENT_DATE')
        
    @no_duplicates
    def test_relabel_from_json(self):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        
        relabeler = utils.RelabelJSON(self.enum)
        r = relabeler(response_json)
        self._assert_response_label_order(r, 'EVENT_DATE')
        
    @no_duplicates
    def test_relabel_with_missing_labels(self):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        
        labels = {
            e.value: name for name, e in self.enum.__members__.items()
            if not e.value.endswith('eventDate')
            }
        
        relabeler = utils.RelabelJSON(labels)
        r = relabeler(response_json)
        self._assert_response_label_order(r, 'eventDate')
        
    @no_duplicates
    def test_relabel_with_missing_fields(self):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        
        for r in response_json:
            del r['disclosures'] # remove field from response
        
        relabeler = utils.RelabelJSON(self.enum)
        relabeler(response_json) # no exceptions
        
    @no_duplicates
    @patch('finra.utils._order_labels')
    def test_relabel_from_response_keep_label_order_false(self, order_labels):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        
        relabeler = utils.RelabelJSON(self.enum, keep_label_order=False)
        relabeler(httpx.Response(200, json=response_json))
        order_labels.assert_not_called()
        
    @no_duplicates
    def test_relabel_from_response_with_obj_labels(self):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        
        obj_labels = {
            'registrations': 'REGISTRATIONS',
            'disclosures': 'DISCLOSURES',
            } # different order than labels order
        
        relabeler = utils.RelabelJSON(self.enum, obj_labels)
        r = relabeler(httpx.Response(200, json=response_json))
        
        for d in r: # object fields follow labels ordering, not obj labels
            keys = list(d.keys())
            self.assertEqual(
                keys,
                ['FIRM_CRD_NUMBER', 'DISCLOSURES', 'REGISTRATIONS']
                ) # labels (enum) order preserved
        
    @no_duplicates
    def test_wrong_response_data_type(self):
        with open('tests/testdata/firm_disclosures_response.json', 'r') as f:
            response_json = json.load(f)
        response_json[0]['disclosures'] = \
            tuple(response_json[0]['disclosures']) # type not allowed
        
        relabeler = utils.RelabelJSON(self.enum)
        
        with self.assertRaisesRegex(
            TypeError,
            "Type 'tuple' not supported. Expected: "
            "None, str, int, float, bool, dict, or list"
            ):
            relabeler(response_json)
        
    @no_duplicates
    def test_wrong_label_type(self):
        with self.assertRaisesRegex(
            TypeError,
            "Relabel mapping can only have string values, or dictionaries "
            "for nested mappings."
            ):
            utils.RelabelJSON({'label': ['bad_value_type']})
        
    # Response labels can be repeated, labels are replaced before object labels
    @no_duplicates
    def test_response_with_repeated_labels_no_collision(self):
        response_json = {
            'test_label': 'test value',
            'test_group': [{'test_label': []}],
            }
        
        labels = {
            'test_label': 'TEST_LABEL', # repeated key in obj labels mapping
            }
        obj_labels = {
            'test_group': 'TEST_GROUP_LABEL',
            'test_label': 'TEST_OBJ_LABEL', # repeated response label
            }
        
        relabeler = utils.RelabelJSON(labels, obj_labels)
        r = relabeler(response_json)
        
        self.assertTrue('TEST_LABEL' in r)
        self.assertTrue('TEST_GROUP_LABEL' in r)
        self.assertTrue('TEST_OBJ_LABEL' in r['TEST_GROUP_LABEL'][0])
        
    @no_duplicates
    def test_labels_mapping_with_repeated_labels_no_collision(self):
        response_json = {
            'test_label': 'test value',
            'test_group': [{'test_label_2': []}],
            }
        
        labels = {
            'test_label': 'TEST_LABEL', # repeated value in obj labels mapping
            }
        obj_labels = {
            'test_group': 'TEST_GROUP_LABEL',
            'test_label_2': 'TEST_LABEL', # repeated labels mapping values
            }
        
        relabeler = utils.RelabelJSON(labels, obj_labels)
        r = relabeler(response_json)
        
        self.assertTrue('TEST_LABEL' in r)
        self.assertTrue('TEST_GROUP_LABEL' in r)
        self.assertTrue('TEST_LABEL' in r['TEST_GROUP_LABEL'][0])
        
    @no_duplicates
    def test_relabeled_objs_without_relabeled_fields_placed_at_end(self):
        response_json = {
            'test_group_2': [],
            'test_label': 'test value',
            'test_group': [{
                'first_label': 'first value',
                'test_label': [],
                }],
            }
        
        labels = {
            'test_group.first_label': 'FIRST_LABEL', # group is first
            'test_label': 'TEST_LABEL',
            } # order defines relabeling order
        obj_labels = {
            'test_group_2': 'TEST_NO_FIELDS_RELABELED', # placed at the end
            'test_label': 'TEST_LABEL',
            'test_group': 'TEST_GROUP_LABEL',
            }
        
        relabeler = utils.RelabelJSON(labels, obj_labels)
        r = relabeler(response_json)
        
        self.assertEqual(
            list(r),
            ['TEST_GROUP_LABEL', 'TEST_LABEL', 'TEST_NO_FIELDS_RELABELED']
            )

