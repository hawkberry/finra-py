"""Utilities to simplify handling ``httpx.Response`` objects"""

from __future__ import annotations
from datetime import date, datetime, timezone
from enum import Enum, EnumType
from typing import Any, Iterable, Optional, TypeAlias, Union, cast

from httpx import Response


__all__ = [
    'LabelsMapType',
    'RelabelJSON',
    'extract_check_status_link',
    'extract_content_type',
    'extract_error_messages',
    'extract_expires',
    'extract_expires_isoformat',
    'extract_filing_created',
    'extract_filing_data',
    'extract_filing_date_of_birth',
    'extract_filing_group',
    'extract_filing_id',
    'extract_filing_individual_crd_number',
    'extract_filing_metadata',
    'extract_filing_name',
    'extract_filing_request_id',
    'extract_filing_result_status',
    'extract_filing_result_status_desc',
    'extract_filing_status',
    'extract_filing_submitted',
    'extract_filing_type',
    'extract_filing_updated',
    'extract_finra_api_request_id',
    'extract_location',
    'extract_record_limit',
    'extract_record_max_limit',
    'extract_record_offset',
    'extract_record_total',
    'extract_request_id',
    'extract_request_timestamp',
    'extract_request_timestamp_dt',
    'extract_response_payload_max_size',
    'extract_result_link',
    'extract_status',
    'extract_total_records_on_page',
    ]


##############################################################################
# HEADER UTILITIES

# Use these utilities to extract values from a response header

def extract_content_type(response: Response) -> Optional[str]:
    """
    Extract and return the value of the ``Content-Type`` header from the
    ``httpx.Response`` object, if it exists.
    
    The value is set to match the value of the request's ``Accept`` header
    unless an error occurred, in which case it will be set to
    ``application/json``. Possible values include ``application/json`` and
    ``text/plain``.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Content-Type`` header
    """
    return response.headers.get("Content-Type")


def extract_finra_api_request_id(response: Response) -> Optional[str]:
    """
    Extract and return the value of the ``FINRA-api-request-id`` header from
    the ``httpx.Response`` object, if it exists.
    
    This is the unique tracking id for the request made. Use this if contacting
    FINRA about this request.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``FINRA-api-request-id`` header
    """
    return response.headers.get("FINRA-api-request-id")


def extract_record_total(response: Response) -> Optional[int]:
    """
    Extract and return the value of the ``Record-Total`` header from the
    ``httpx.Response`` object, if it exists.
    
    The total number of records found at the time of the request. Use this
    value when paging through large datasets to determine when all data has
    been retrieved.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Record-Total`` header
    """
    record_total = response.headers.get("Record-Total")
    if record_total:
        return int(record_total)
    return None


def extract_record_limit(response: Response) -> Optional[int]:
    """
    Extract and return the value of the ``Record-Limit`` header from the
    ``httpx.Response`` object, if it exists.
    
    The value is set to match the limit value provided with the request or the
    platform maximum limit, whichever is smaller.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Record-Limit`` header
    """
    record_limit = response.headers.get("Record-Limit")
    if record_limit:
        return int(record_limit)
    return None


def extract_record_offset(response: Response) -> Optional[int]:
    """
    Extract and return the value of the ``Record-Offset`` header from the
    ``httpx.Response`` object, if it exists.
    
    The value is set to match the offset value provided with the request.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Record-Offset`` header
    """
    record_offset = response.headers.get("Record-Offset")
    if record_offset:
        return int(record_offset)
    return None


def extract_total_records_on_page(response: Response) -> Optional[int]:
    """
    Extract and return the value of the ``Total-Records-On-Page`` header from
    the ``httpx.Response`` object, if it exists.
    
    The total number of records returned for this page. This will be the
    default number of records for the page, except for the last page which
    might be less than the default.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Total-Records-On-Page`` header
    """
    total_records_on_page = response.headers.get("Total-Records-On-Page")
    if total_records_on_page:
        return int(total_records_on_page)
    return None


def extract_record_max_limit(response: Response) -> Optional[int]:
    """
    Extract and return the value of the ``Record-Max-Limit`` header from the
    ``httpx.Response`` object, if it exists.
    
    The value is set to the maximum number of records that will be returned by
    the platform, regardless of the size of the response payload. Use this
    header to build an API client that can adapt to future record limit value
    changes.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Record-Max-Limit`` header
    """
    record_max_limit = response.headers.get("Record-Max-Limit")
    if record_max_limit:
        return int(record_max_limit)
    return None


def extract_response_payload_max_size(response: Response) -> Optional[str]:
    """
    Extract and return the value of the ``Response-Payload-Max-Size`` header
    from the ``httpx.Response`` object, if it exists.
    
    The value is set to the maximum payload size (in MB) that will be returned
    by the platform, regardless of the number of records returned. Use this
    header to build an API client that can adapt to future response payload
    size changes.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Response-Payload-Max-Size`` header
    """
    return response.headers.get("Response-Payload-Max-Size")


def extract_location(response: Response) -> Optional[str]:
    """
    Extract and return the value of the ``Location`` header from the
    ``httpx.Response`` object, if it exists.
    
    The value is the check status URL returned by the first leg in an
    asynchronous request. Use this URL in the second leg of the operation to
    check the status of an asynchronous request.
    
    For most datasets, just pass this URL to
    :py:meth:`BaseClient.get_async_request_status()
    <finra.base_client.BaseClient.get_async_request_status>` to check the
    result status.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``Location`` header
    """
    return response.headers.get("Location")


##############################################################################
# ASYNCHRONOUS REQUEST UTILITIES

# Extract values from a response body
def _extract_response_field(response: Response | dict[str, Any], field: str
                            ) -> Optional[Any]:
    if isinstance(response, Response):
        _response: dict[str, Any] = response.json()
        return _response.get(field)
    return response.get(field)


def extract_status(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract and return the result status from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the status of the file requested.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Result status
    """
    return _extract_response_field(response, "status")


def extract_result_link(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract and return the result link URL from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the *pre-signed* URL for data object retrieval. This attribute
    is only included in the response body when the status is ``complete``.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Result link URL
    """
    return _extract_response_field(response, "resultLink")


def extract_expires(
    response: Response | dict[str, Any]
    ) -> Optional[datetime]:
    """
    Extract and return the result expiration datetime from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The ``expires`` field must have the format ``%Y-%m-%d %H:%M:%S %Z``. This is
    typically the case with non-native asynchronous request flows that check their
    status using :py:meth:`BaseClient.get_async_request_status()
    <finra.base_client.BaseClient.get_async_request_status>`.
    
    The returned value is the timezone-aware UTC expiration datetime of the
    *pre-signed* URL. After the URL expires, the URL will no longer be valid.
    This attribute is only included in the response body when the status is
    ``complete``.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Result expiration
    """
    expires = _extract_response_field(response, "expires")
    if expires:
        return datetime.strptime(
            expires, "%Y-%m-%d %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
    return None


def extract_expires_isoformat(
    response: Response | dict[str, Any]
    ) -> Optional[datetime]:
    """
    Extract and return the result expiration datetime from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The ``expires`` field must be in ISO format. This is typically the case with
    asynchronous request flows that check their status natively within their
    original request method.
    
    The returned value is the timezone-aware UTC expiration datetime of the
    *pre-signed* URL. After the URL expires, the URL will no longer be valid.
    This attribute is only included in the response body when the status is
    ``complete``.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Result expiration
    """
    expires = _extract_response_field(response, "expires")
    if expires:
        return datetime.fromisoformat(expires)
    return None


def extract_check_status_link(
    response: Response | dict[str, Any]
    ) -> Optional[str]:
    """
    Extract and return the check status link from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the check status URL returned by the first leg in an
    asynchronous request. Use this URL in the second leg of the operation to
    check the status of an asynchronous request.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Check status link URL
    
    .. note:: This is an alternative to :py:func:`extract_location` for
        certain datasets, for example, TRACE Report Cards datasets. Even though
        it may work in general, the documented method for most datasets for
        retrieving the check status URL when doing asynchronous requests is via
        the ``Location`` header.
    """
    return _extract_response_field(response, "checkStatusLink")


def extract_request_id(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract and return the ``request_id`` from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the FINRA UUID used to uniquely identify the request.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``request_id``
    
    .. note:: For filings, use :func:`extract_filing_request_id`.
    """
    return _extract_response_field(response, "requestId")


def extract_request_timestamp(
    response: Response | dict[str, Any]
    ) -> Optional[str]:
    """
    Extract and return the ``request_timestamp`` from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the ISO datetime string when the API request was created, returned
    as a string.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``request_timestamp``
    """
    return _extract_response_field(response, "requestTimestamp")


def extract_request_timestamp_dt(
    response: Response | dict[str, Any]
    ) -> Optional[datetime]:
    """
    Extract and return the ``request_timestamp`` from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the ISO datetime when the API request was created, returned as a
    ``datetime.datetime`` object.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: ``request_timestamp``
    """
    request_timestamp = _extract_response_field(response, "requestTimestamp")
    if request_timestamp:
        return datetime.fromisoformat(request_timestamp)
    return None


def extract_error_messages(
    response: Response | dict[str, Any]
    ) -> Optional[list[str]]:
    """
    Extract and return any error messages from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if they exist.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Error messages
    
    .. note::
        This functionality is only documented for
        :py:meth:`BaseClient.get_composite_individual_seed()
        <finra.base_client.BaseClient.get_composite_individual_seed>`.
    """
    return _extract_response_field(response, "errorMessages")


##############################################################################
# ASYNCHRONOUS SUBMISSION API REQUEST UTILITIES

def extract_filing_request_id(
    response: Response | dict[str, Any]
    ) -> Optional[str]:
    """
    Extract and return a filing's ``request_id`` field from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists.
    
    The value is the FINRA UUID used to identify the filing request.
    This value must be passed back to the same method that was originally
    called.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's ``request_id``
    
    .. note:: For methods other than Submission API filings, use
        :func:`extract_request_id`.
    """
    return _extract_response_field(response, "id")


def extract_filing_group(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract the dataset group from the body of the ``httpx.Response``
    object (value should be ``registration``), or from the JSON data returned
    by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's dataset group
    """
    return _extract_response_field(response, "group")


def extract_filing_name(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract the dataset name from the body of the ``httpx.Response`` object, or
    from the JSON data returned by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's dataset name
    """
    return _extract_response_field(response, "name")


def extract_filing_data(response: Response | dict[str, Any]) -> Optional[dict]:
    """
    Extract the filing data from the body of the ``httpx.Response`` object, or
    from the JSON data returned by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's data object
    """
    filing = _extract_response_field(response, "filing")
    if filing:
        return filing.get("filingData")
    return None


# Extract metadata fields from a filing response
def extract_filing_metadata(
    response: Response | dict[str, Any]
    ) -> Optional[dict]:
    """
    Extract metadata from the body of the ``httpx.Response`` object, or the
    JSON data returned by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: Either the filing's metadata object
    """
    filing = _extract_response_field(response, "filing")
    if filing:
        return filing.get("metadata")
    return None


def extract_filing_status(
    response: Response | dict[str, Any]
    ) -> Optional[str]:
    """
    Extract the ``filing_status`` from the body of the ``httpx.Response``
    object, or from the JSON data returned by ``httpx.Response.json()``, if it
    exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's status
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        return metadata.get("filingStatus")
    return None


def extract_filing_id(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract the ``filing_id`` from the body of the ``httpx.Response`` object,
    or from the JSON data returned by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's ID
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        return metadata.get("filingId")
    return None


def extract_filing_type(response: Response | dict[str, Any]) -> Optional[str]:
    """
    Extract the ``filing_type`` from the body of the ``httpx.Response`` object,
    or from the JSON data returned by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's type
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        return metadata.get("filingType")
    return None


def extract_filing_result_status(
    response: Response | dict[str, Any]
    ) -> Optional[str]:
    """
    Extract the result status from the body of the ``httpx.Response`` object,
    or from the JSON data returned by ``httpx.Response.json()``, if it exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's result status
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        return metadata.get("resultStatus")
    return None


def extract_filing_result_status_desc(
    response: Response | dict[str, Any]
    ) -> Optional[dict]:
    """
    Extract the result status description from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists. Possible fields included in the
    result status description object include ``message`` with a summary
    message, ``errors`` with a list of error messages, and ``warnings`` with a
    list of warning messages.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's result status description object
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        return metadata.get("resultStatusDesc")
    return None


def extract_filing_created(
    response: Response | dict[str, Any]
    ) -> Optional[dict]:
    """
    Extract metadata on filing creation from the body of the ``httpx.Response``
    object, or from the JSON data returned by ``httpx.Response.json()``, if it
    exists. Returned dictionary contains a ``by`` field with the api client id
    of the user who created the filing, and an ``on`` field with the creation
    timestamp returned as a timezone-aware ``datetime.datetime`` object.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's creation data object
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        created = metadata.get("created")
        if created is not None and "on" in created:
            created["on"] = datetime.fromisoformat(created["on"])
        return created
    return None


def extract_filing_updated(
    response: Response | dict[str, Any]
    ) -> Optional[dict]:
    """
    Extract metadata on filing update from the body of the ``httpx.Response``
    object, or from the JSON data returned by ``httpx.Response.json()``, if it
    exists. Returned dictionary contains a ``by`` field with the api client id
    of the user who updated the filing, and an ``on`` field with the update
    timestamp returned as a timezone-aware ``datetime.datetime`` object.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's update data object
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        updated = metadata.get("updated")
        if updated is not None and "on" in updated:
            updated["on"] = datetime.fromisoformat(updated["on"])
        return updated
    return None


def extract_filing_submitted(
    response: Response | dict[str, Any]
    ) -> Optional[dict]:
    """
    Extract metadata on filing submission from the body of the
    ``httpx.Response`` object, or from the JSON data returned by
    ``httpx.Response.json()``, if it exists. Returned dictionary contains a
    ``by`` field with the api client id of the user who submitted the filing,
    and an ``on`` field with the submission timestamp returned as a
    timezone-aware ``datetime.datetime`` object.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's submission data object
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        submitted = metadata.get("submitted")
        if submitted is not None and "on" in submitted:
            submitted["on"] = datetime.fromisoformat(submitted["on"])
        return submitted
    return None


def extract_filing_individual_crd_number(
    response: Response | dict[str, Any]
    ) -> Optional[int]:
    """
    Extract the Individual CRD Number from the body of the ``httpx.Response``
    object, or from the JSON data returned by ``httpx.Response.json()``, if it
    exists.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's Individual CRD Number
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        individual_crd_number = metadata.get("individualCrdNumber")
        if individual_crd_number:
            return int(individual_crd_number)
    return None


def extract_filing_date_of_birth(
    response: Response | dict[str, Any]
    ) -> Optional[date]:
    """
    Extract the Date of Birth from the body of the ``httpx.Response`` object,
    or from the JSON data returned by ``httpx.Response.json()``, if it exists.
    The value is returned as a ``datetime.date`` object.
    
    :param response:
    :type response: :py:class:`httpx.Response`
    :return: The filing's Date of Birth
    """
    metadata = extract_filing_metadata(response)
    if metadata:
        dob = metadata.get("dateOfBirth")
        if dob:
            return date.fromisoformat(dob)
    return None


##############################################################################
# RELABELING RESPONSE UTILITIES

#: Type for nested ``labels`` mapping used by :py:class:`RelabelJSON`.
LabelsMapType: TypeAlias = dict[str, Union[str, "LabelsMapType"]]

_OrderedMapType: TypeAlias = dict[str, Union[None, "_OrderedMapType"]]


# Recursively expand a joined schema with period-delimited keys
def _expand_relabel(
    labels: LabelsMapType,
    key: str,
    value: str | LabelsMapType
    ) -> None:
    if not isinstance(key, str):
        raise TypeError("Relabel mapping can only have string-valued keys")
    
    if "." in key: # expand keys, pass values through
        group, key = key.split(".", 1)
        if group not in labels:
            labels[group] = {}
        _expand_relabel(cast(LabelsMapType, labels[group]), key, value)
        
    elif isinstance(value, dict):
        d: LabelsMapType = {}
        labels[key] = d
        for k, v in value.items():
            _expand_relabel(d, k, v)
        
    elif not isinstance(value, str):
        raise TypeError(
            "Relabel mapping can only have string values, or dictionaries "
            "for nested mappings."
            )
    else:
        labels[key] = value


# Wrapper around recursive relabel
def _expand_relabel_map(labels: EnumType | LabelsMapType) -> LabelsMapType:
    if isinstance(labels, EnumType): # enum inverse mapping
        members: Iterable[tuple[str, Enum]] = labels.__members__.items()
        labels = {e.value: name for name, e in members}
    
    out: LabelsMapType = {} # relabel map
    for key, value in labels.items(): # expand period-delimited keys
        _expand_relabel(out, key, value)
    return out


# Returns an ordered mapping of labels based on the provided labels
# Ordering is determined by labels, not by obj labels
# Ordering of "."-delimited objects is determined by the first group member
def _order_labels(
    labels: LabelsMapType,
    obj_labels: dict[str, str],
    out: _OrderedMapType
    ) -> _OrderedMapType:
    
    for k, v in labels.items():
        if isinstance(v, str): # leaf relabel
            out[v] = None
            
        else: # re-order sub-mapping
            out[obj_labels.get(k, k)] = _order_labels(v, obj_labels, {})
    
    return out


# Recursively copy and relabel JSON object
def _relabel_json(
    obj: Any,
    labels: LabelsMapType,
    obj_labels: dict[str, str],
    ordered: Optional[_OrderedMapType]
    ) -> Any:
    
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj # leaf node, literals are passed through
    
    if isinstance(obj, dict): # dicts are processed recursively
        k: str
        out = {}
        for k, v in obj.items():
            
            if k in labels:
                _labels = labels[k] # needed for typing
                
                if isinstance(_labels, dict): # object node label sub-mapping
                    out[obj_labels.get(k, k)] = _relabel_json(
                        v, _labels, obj_labels, (
                            None if ordered is None
                            else ordered[obj_labels.get(k, k)]
                            )
                        )
                    
                else: # leaf node re-label , resolve on next recursion
                    out[_labels] = _relabel_json(v, {}, obj_labels, None)
                
            elif isinstance(v, (dict, list)): # object node key not in labels
                out[obj_labels.get(k, k)] = _relabel_json(
                    v, {}, obj_labels, None
                    )
                
            else: # leaf node not in labels
                out[k] = _relabel_json(v, {}, obj_labels, None)
        
        if ordered is not None: # re-order labels
            _out = {k: out[k] for k in ordered if k in out}
            _out.update({k: v for k, v in out.items() if k not in ordered})
            return _out
        
        return out
    
    if isinstance(obj, list): # lists are passed through, processed recursively
        return [_relabel_json(v, labels, obj_labels, ordered) for v in obj]
    
    raise TypeError(
        f"Type '{type(obj).__name__}' not supported. Expected: "
        "None, str, int, float, bool, dict, or list"
        )


# Relabel response data from an API's labels to an app's canonical labels
class RelabelJSON:
    """
    Relabel JSON data from an ``httpx.Response`` object based on a provided
    label mapping. See :ref:`relabeler` for more information and examples.
    
    :param labels: One of the following:
        
        1. The enum type representing the field names for a dataset.
        
        2. A mapping from the old labels to the new labels. If a node is a leaf
           node, the key should be the old label, and the value should be the
           new label. If the returned json object has object or array nodes,
           then the nested leaf node labels can be specified using either
           period-delimited (``.``) syntax, or using nested mappings.
        
    :param obj_labels: An optional flat mapping for relabeling object nodes,
        regardless of the depth of the node
    :param keep_label_order: Re-order the response data in the order of
        ``labels``
    """
    
    def __init__(
        self,
        labels: EnumType | LabelsMapType,
        obj_labels: dict[str, str]={},
        keep_label_order: bool=True
        ):
        _labels = _expand_relabel_map(labels) # expanded mapping to relabel obj
        if keep_label_order: # used to re-order a relabeled obj
            ordered = _order_labels(_labels, obj_labels, {})
        else:
            ordered = None
        self.labels = _labels
        self.obj_labels = obj_labels
        self._ordered = ordered
        
    # Re-map response labels based on enum, or a mapping
    def __call__(self, response: Response | dict[str, Any]) -> dict[str, Any]:
        """
        :param response: Either the ``httpx.Response`` object, or the JSON data
            to relabel that was returned by ``httpx.Response.json()``
        :type response: :py:class:`httpx.Response` | :py:type:`dict[str, Any]`
        :return: The relabeled JSON data
        """
        if isinstance(response, Response):
            response = response.json()
        return _relabel_json(
            response, self.labels, self.obj_labels, self._ordered
            )

