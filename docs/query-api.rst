.. highlight:: python

.. _query:

=========
Query API
=========

If you haven't read :ref:`getting_started`, :ref:`auth` and :ref:`client`, please start by reading those sections.

The `Query API <https://developer.finra.org/docs#query_api>`__ datasets belong to one of several API groups. Each dataset has its own method for requesting data. Some datasets have access restrictions requiring specific credential types. See each dataset's query method for exact requirements.

The **OTC Market** group (also known as the **Equity** group) datasets that provide access to Over-the-Counter (OTC) trade and equity data:

- :py:meth:`Client.get_ats_block_summary() <finra.base_client.BaseClient.get_ats_block_summary>`
- :py:meth:`Client.get_otc_block_summary() <finra.base_client.BaseClient.get_otc_block_summary>`
- :py:meth:`Client.get_consolidated_short_interest() <finra.base_client.BaseClient.get_consolidated_short_interest>`
- :py:meth:`Client.get_daily_short_sale_volume() <finra.base_client.BaseClient.get_daily_short_sale_volume>`
- :py:meth:`Client.get_threshold_list() <finra.base_client.BaseClient.get_threshold_list>`
- :py:meth:`Client.get_weekly_summary() <finra.base_client.BaseClient.get_weekly_summary>`
- :py:meth:`Client.get_weekly_summary_historic() <finra.base_client.BaseClient.get_weekly_summary_historic>`
- :py:meth:`Client.get_monthly_summary() <finra.base_client.BaseClient.get_monthly_summary>`
- :py:meth:`Client.get_otc_daily_list() <finra.base_client.BaseClient.get_otc_daily_list>`

The **Fixed Income** group datasets provide access to Over-the-Counter secondary market transaction data for fixed income securities as reported to TRACE:

- :py:meth:`Client.get_agency_tba_pricing() <finra.base_client.BaseClient.get_agency_tba_pricing>`
- :py:meth:`Client.get_agency_cmo_pricing() <finra.base_client.BaseClient.get_agency_cmo_pricing>`
- :py:meth:`Client.get_agency_debt_market_breadth() <finra.base_client.BaseClient.get_agency_debt_market_breadth>`
- :py:meth:`Client.get_agency_debt_market_sentiment() <finra.base_client.BaseClient.get_agency_debt_market_sentiment>`
- :py:meth:`Client.get_agency_mbs_trading_activity() <finra.base_client.BaseClient.get_agency_mbs_trading_activity>`
- :py:meth:`Client.get_agency_mbs_arm_hybrid_pricing() <finra.base_client.BaseClient.get_agency_mbs_arm_hybrid_pricing>`
- :py:meth:`Client.get_agency_mbs_pricing() <finra.base_client.BaseClient.get_agency_mbs_pricing>`
- :py:meth:`Client.get_collateralized_obligations_pricing() <finra.base_client.BaseClient.get_collateralized_obligations_pricing>`
- :py:meth:`Client.get_corporate_144a_debt_market_breadth() <finra.base_client.BaseClient.get_corporate_144a_debt_market_breadth>`
- :py:meth:`Client.get_corporate_144a_debt_market_sentiment() <finra.base_client.BaseClient.get_corporate_144a_debt_market_sentiment>`
- :py:meth:`Client.get_corporate_and_agency_capped_volume() <finra.base_client.BaseClient.get_corporate_and_agency_capped_volume>`
- :py:meth:`Client.get_corporate_debt_market_breadth() <finra.base_client.BaseClient.get_corporate_debt_market_breadth>`
- :py:meth:`Client.get_corporate_debt_market_sentiment() <finra.base_client.BaseClient.get_corporate_debt_market_sentiment>`
- :py:meth:`Client.get_daily_cmbs_pricing() <finra.base_client.BaseClient.get_daily_cmbs_pricing>`
- :py:meth:`Client.get_non_agency_cmo_abs_pricing() <finra.base_client.BaseClient.get_non_agency_cmo_abs_pricing>`
- :py:meth:`Client.get_non_agency_cmo_pricing() <finra.base_client.BaseClient.get_non_agency_cmo_pricing>`
- :py:meth:`Client.get_securitized_products_capped_volume() <finra.base_client.BaseClient.get_securitized_products_capped_volume>`
- :py:meth:`Client.get_securitized_products_errata() <finra.base_client.BaseClient.get_securitized_products_errata>`
- :py:meth:`Client.get_securitized_products_trading_activity() <finra.base_client.BaseClient.get_securitized_products_trading_activity>`
- :py:meth:`Client.get_treasury_daily_aggregates() <finra.base_client.BaseClient.get_treasury_daily_aggregates>`
- :py:meth:`Client.get_treasury_monthly_aggregates() <finra.base_client.BaseClient.get_treasury_monthly_aggregates>`
- :py:meth:`Client.get_weekly_cmbs_pricing() <finra.base_client.BaseClient.get_weekly_cmbs_pricing>`

The **FINRA** group datasets include data and content typically found on FINRA.org including the FINRA Rulebook:

- :py:meth:`Client.get_finra_rulebook() <finra.base_client.BaseClient.get_finra_rulebook>`
- :py:meth:`Client.get_firm_registration_types() <finra.base_client.BaseClient.get_firm_registration_types>`

The **Firm** group datasets provide access to information that is specific to individual FINRA member firms, some of which are involved in registration operations and only accessible by the firm itself:

- :py:meth:`Client.get_firm_customer_complaints() <finra.base_client.BaseClient.get_firm_customer_complaints>`
- :py:meth:`Client.get_firm_disclosures() <finra.base_client.BaseClient.get_firm_disclosures>`
- :py:meth:`Client.get_firm_profile() <finra.base_client.BaseClient.get_firm_profile>`
- :py:meth:`Client.get_firm_registration_status_history() <finra.base_client.BaseClient.get_firm_registration_status_history>`
- :py:meth:`Client.get_firm_registrations() <finra.base_client.BaseClient.get_firm_registrations>`

The **Registration** group datasets provide member firms access to their registration records as stored in the Central Registration Depository (CRD):

- :py:meth:`Client.get_accounting() <finra.base_client.BaseClient.get_accounting>`
- :py:meth:`Client.get_altered_ssn_and_dob() <finra.base_client.BaseClient.get_altered_ssn_and_dob>`
- :py:meth:`Client.get_branch_delta() <finra.base_client.BaseClient.get_branch_delta>`
- :py:meth:`Client.get_branch_list() <finra.base_client.BaseClient.get_branch_list>`
- :py:meth:`Client.get_broker_dealer_firm_list() <finra.base_client.BaseClient.get_broker_dealer_firm_list>`
- :py:meth:`Client.get_composite_branch() <finra.base_client.BaseClient.get_composite_branch>`
- :py:meth:`Client.get_composite_individual() <finra.base_client.BaseClient.get_composite_individual>`
- :py:meth:`Client.get_composite_individual_seed() <finra.base_client.BaseClient.get_composite_individual_seed>`
- :py:meth:`Client.get_individual_delta() <finra.base_client.BaseClient.get_individual_delta>`
- :py:meth:`Client.get_individual_fingerprint() <finra.base_client.BaseClient.get_individual_fingerprint>`
- :py:meth:`Client.get_individual_pre_registration_search() <finra.base_client.BaseClient.get_individual_pre_registration_search>`
- :py:meth:`Client.get_individual_pre_registration_search_v2() <finra.base_client.BaseClient.get_individual_pre_registration_search_v2>`
- :py:meth:`Client.get_individual_registration_validation() <finra.base_client.BaseClient.get_individual_registration_validation>`
- :py:meth:`Client.get_individual_registration_validation_details() <finra.base_client.BaseClient.get_individual_registration_validation_details>`
- :py:meth:`Client.get_registered_individual_search() <finra.base_client.BaseClient.get_registered_individual_search>`
- :py:meth:`Client.get_u4_form_prefill() <finra.base_client.BaseClient.get_u4_form_prefill>`

The **TRACE Report Card** group datasets provide access to firms to detect potential compliance issues early and cover a variety of topics and rule sets:

- :py:meth:`Client.get_trace_agency_debt_details() <finra.base_client.BaseClient.get_trace_agency_debt_details>`
- :py:meth:`Client.get_trace_agency_debt_summary() <finra.base_client.BaseClient.get_trace_agency_debt_summary>`
- :py:meth:`Client.get_trace_treasuries_details() <finra.base_client.BaseClient.get_trace_treasuries_details>`
- :py:meth:`Client.get_trace_treasuries_summary() <finra.base_client.BaseClient.get_trace_treasuries_summary>`
- :py:meth:`Client.get_trace_corporate_bonds_details() <finra.base_client.BaseClient.get_trace_corporate_bonds_details>`
- :py:meth:`Client.get_trace_corporate_bonds_summary() <finra.base_client.BaseClient.get_trace_corporate_bonds_summary>`
- :py:meth:`Client.get_trace_securitized_products_details() <finra.base_client.BaseClient.get_trace_securitized_products_details>`
- :py:meth:`Client.get_trace_securitized_products_summary() <finra.base_client.BaseClient.get_trace_securitized_products_summary>`

.. _endpoints:

+++++++++
Endpoints
+++++++++

Datasets that support multiple endpoints have an ``endpoint`` keyword in their query method. In general, there are four resource endpoints that can be queried for a dataset: :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>`, :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>`, :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>` and :py:attr:`Endpoint.DATASETS <finra.base_client.BaseClient.Endpoint.DATASETS>`. Read more about `Resource Endpoints <https://developer.finra.org/docs#query_api-resource_endpoints>`__ in the official API documentation.

----
Data
----

All datasets support the :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` endpoint, which returns the data for the dataset. This is the default endpoint when calling a dataset's query method on the client.

.. code-block:: python

  r = c.get_ats_block_summary(endpoint=c.Endpoint.DATA)  # kwarg default
  
  r.raise_for_status()
  
  data = r.json()  # the actual data for this dataset

If a response has no content, it will return a ``204 No Content`` response code, which will not raise an exception when calling ``r.raise_for_status()``. However, calling ``r.json()`` with no content will raise ``json.JSONDecodeError``.

All other query method keywords only apply to the :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` endpoint.

--------
Metadata
--------

Many datasets support the :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>` endpoint, which provides information about each of the fields in a dataset. These datasets are represented on the client using enums, and the :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>` response for a dataset should contain the same information that is documented on its enum.

.. code-block:: python

  r = c.get_ats_block_summary(endpoint=c.Endpoint.METADATA)
  
  r.raise_for_status()
  
  metadata = r.json()  # field names, types & descriptions

Some datasets do not support :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>`, and consequently do not have an enum on the client. Any endpoint restrictions are detailed in the documentation for a dataset's query method on the client.

----------
Partitions
----------

Many datasets have partition fields, which are typically used by a database program to distribute a large table across multiple machines. The partition fields for a dataset can be determined from the :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>` or :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>` responses. They are also labeled on the dataset's enum in the reference documentation.

.. code-block:: python

  r = c.get_ats_block_summary(endpoint=c.Endpoint.PARTITIONS)
  
  r.raise_for_status()
  
  partitions = r.json()  # available values for partition fields

Some datasets do not support :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>`. Any endpoint restrictions are detailed in the documentation for a dataset's query method on the client.

--------
Datasets
--------

Almost all datasets support the :py:attr:`Endpoint.DATASETS <finra.base_client.BaseClient.Endpoint.DATASETS>` endpoint. It can be used to retrieve information about the capabilities and features supported by each dataset, including API request methods, data format, versioning, and whether or not it is currently active. To request information about a specific dataset use the dataset's query method.

.. code-block:: python

  r = c.get_ats_block_summary(endpoint=c.Endpoint.DATASETS)
  
  r.raise_for_status()
  
  datasets = r.json()  # supported API request methods, data formats, etc.

This information can be retrieved as a comprehensive list of Query API datasets using the :py:meth:`Client.get_datasets() <finra.base_client.BaseClient.get_datasets>` method. If no arguments are provided, this method will return information for all datasets available using the client's credentials, including undocumented and unsupported datasets. If a member of :py:class:`Group <finra.base_client.BaseClient.Group>` is provided, information is returned for only datasets in that group.

.. code-block:: python

  r = c.get_datasets(group=c.Group.EQUITY)
  
  r.raise_for_status()
  
  datasets = r.json()  # information for all EQUITY datasets

.. _fields:

++++++
Fields
++++++

Most datasets support requesting only a subset of fields. These datasets have a ``fields`` keyword in their query method, which accepts one or more fields specified as members of a dataset's enum. To request multiple fields, provide them as an iterable. The order of the fields does not affect the response data.

In this example, the query returns only three fields for each record.

.. code-block:: python

  e = c.ConsolidatedShortInterest  # enum for this dataset
  
  r = c.get_consolidated_short_interest(
      fields=[e.SYMBOL, e.CURRENT_SHORT_POSITION, e.SETTLEMENT_DATE]
      )
  
  r.raise_for_status()
  
  data = r.json()

.. _filters:

+++++++
Filters
+++++++

Filters can be used to narrow the scope of the returned data. These are useful when selecting a subset of data from a large dataset. Datasets that support filtering have a ``filters`` keyword in their query method that accepts either a :py:class:`Filter <finra.filters.Filter>` object, or a ``dict`` representing the JSON object to pass directly to the API. However, if the JSON object is incorrectly formatted, the request will be rejected by the API.

To simplify this process, the :py:class:`Filter <finra.filters.Filter>` class implements each of the available API filters. Methods that add a filter also return the :py:class:`Filter <finra.filters.Filter>` object, allowing calls to be chained together so that a complex filter can be built in a single line.

See the :py:mod:`finra.filters` module for complete reference documentation.

--------------
Compare Filter
--------------

A compare filter can be used to create a condition for comparing specific field values using the :py:meth:`Filter.add_compare() <finra.filters.Filter.add_compare>` method. The comparison operation is determined by the value of the :py:class:`CompareType <finra.filters.Filter.CompareType>` enum passed as the third argument. If no compare type is provided, the value defaults to :py:attr:`CompareType.EQUAL <finra.filters.Filter.CompareType.EQUAL>`. Compare filters are required for datasets with partitions when requesting sorted records (see :ref:`sorting` below).

.. code-block:: python

  from datetime import date
  
  from finra.filters import Filter
  
  e = c.WeeklySummary                   # enum for this dataset
  
  f = (
      Filter(e)
          .add_compare(
              e.WEEK_START_DATE,        # a partition field for this dataset
              date(2025, 1, 6),         # partition value (Monday)
              Filter.CompareType.EQUAL  # not necessary, this is the default
              )
          .add_compare(                 # chain another filter in-line
              e.TOTAL_TRADES,
              10_000,
              Filter.CompareType.GREATER
              )                  # only records with more than 10,000 trades
      )

If a value other than a member of :py:class:`CompareType <finra.filters.Filter.CompareType>` is passed for the compare type, a ``TypeError`` will be raised. This functionality can be disabled by setting ``require_enums=False`` during instantiation, or via the :py:meth:`set_require_enums() <finra.enum_converter.EnumConverter.set_require_enums>` method.

-----------------
Date Range Filter
-----------------

Date range filters can be added on date- and datetime-typed columns using the :py:meth:`Filter.add_date_range() <finra.filters.Filter.add_date_range>` method. The method accepts ``datetime.date`` and ``datetime.datetime`` objects to specify start and end dates for the range, and will raise a ``TypeError`` for any other types. Start and end dates are inclusive.

.. code-block:: python

  from datetime import date
  
  from finra.filters import Filter
  
  e = c.WeeklySummary            # enum for this dataset
  
  f = Filter(e).add_date_range(
      e.LAST_REPORTED_DATE,
      date(2025, 1, 1),          # start date (inclusive)
      date(2026, 1, 1)           # end date (inclusive)
      )

-------------
Domain Filter
-------------

To select records with a specific field value, or set of values, add a domain filter using the :py:meth:`Filter.add_domain() <finra.filters.Filter.add_domain>` method. For a single field value this is effectively the same as a compare filter with :py:attr:`CompareType.EQUAL <finra.filters.Filter.CompareType.EQUAL>`. However, a domain filter can be used to select records matching multiple field values.

.. code-block:: python

  from finra.filters import Filter
  
  e = c.WeeklySummary           # enum for this dataset
  
  f = Filter(e).add_domain(
      e.SYMBOL,
      ["AAPL", "MSFT", "NVDA"]  # only records for these symbols
      )

.. _sorting:

+++++++
Sorting
+++++++

Datasets that support requesting data in sorted order have a ``sort_fields`` keyword in their query method, which accepts fields specified as members of a dataset's enum. By default, records are returned in ascending order. To specify the sort direction, provide a 2-tuple of the form ``(direction, <member>)``, where ``direction`` is a number and ``<member>`` is an enum member. A negative ``direction`` sorts records in descending order. To sort by multiple fields, provide them as a list (or an iterable that is not a tuple).

When requesting sorted records, a request must include a compare filter with :py:attr:`CompareType.EQUAL <finra.filters.Filter.CompareType.EQUAL>` on each of the partition fields for the dataset. If a dataset does not have partition fields (such as Registration group datasets), then a compare filter is not required.

In this example, the query returns records sorted by symbol in ascending order. For this dataset, the partition field is the settlement date.

.. code-block:: python

  from datetime import date
  
  from finra.filters import Filter
  
  d = date(2025, 12, 31)           # settlement date for the query
  
  e = c.ConsolidatedShortInterest  # enum for this dataset
  
  r = c.get_consolidated_short_interest(
      filters=Filter(e).add_compare(e.SETTLEMENT_DATE, d),  # EQUAL is default
      sort_fields=e.SYMBOL         # sort by symbol in ascending order
      )
  
  r.raise_for_status()
  
  data = r.json()

Similarly, this example sorts by multiple fields: first by change percent in descending order, and then by symbol in ascending order.

.. code-block:: python

  r = c.get_consolidated_short_interest(
      filters=Filter(e).add_compare(e.SETTLEMENT_DATE, d),  # EQUAL is default
      sort_fields=[(-1, e.CHANGE_PERCENT), e.SYMBOL]        # multi-field sort
      )

Sorting is not supported on historical datasets, for example, when calling :py:meth:`Client.get_weekly_summary_historic <finra.base_client.BaseClient.get_weekly_summary_historic>`.

Read more about `Sorting Restrictions <https://developer.finra.org/docs#query_api-api_basics-sorting_restrictions>`__ in the official API documentation.

.. _async_requests:

+++++++++++++++++++++
Asynchronous Requests
+++++++++++++++++++++

Asynchronous requests are useful when accessing a large number of records. They allow more records to be obtained per API request while reducing the load on the platform. Datasets that support the asynchronous request flow described below have an ``async_request`` keyword in their query method.

Asynchronous requests involve making (at least) three separate requests to the API. The first leg of an asynchronous operation is to call the dataset's query method with the keyword argument ``async_request=True``. The response will include a status code, but it will not include the requested data in the response body. Instead, the response will include a ``Location`` header that contains the URL to use for the second leg of the operation to check the status of the request. To simplify handling the ``Location`` header, pass the ``httpx.Response`` object from the first leg to the :py:func:`extract_location() <finra.utils.extract_location>` function as an argument, which will return the check status URL.

.. code-block:: python

  from finra import utils
  
  r = c.get_consolidated_short_interest(async_request=True)  # first leg
  
  r.raise_for_status()
  
  assert r.status_code == 202      # status code should be 202
  
  check_status_link = utils.extract_location(r)  # URL for second leg

For the second leg, pass the check status URL to :py:meth:`Client.get_async_request_status() <finra.base_client.BaseClient.get_async_request_status>` to request the status of the results. The result status can be extracted from the response using :py:func:`extract_status() <finra.utils.extract_status>`. If the results are still being processed, the response will return with a status code of ``202``, and the result status will have a value of ``pending``. When the response returns a status code of ``200``, the result status will have a value of ``complete``, indicating that the result data is ready. The result URL can then be extracted from the response using the :py:func:`extract_result_link() <finra.utils.extract_result_link>` function.

.. code-block:: python

  import time
  
  while True:                      # keep checking status until "complete"
      r = c.get_async_request_status(check_status_link)   # second leg
      
      r.raise_for_status()
      
      if r.status_code == 200:     # result status is "complete"
          # assert utils.extract_status(r) == "complete"  # expected status
          break
      
      assert r.status_code == 202  # result status is "pending"
      # assert utils.extract_status(r) == "pending"       # expected status
      
      time.sleep(60)  # FINRA recommends polling no more than once per minute
      
  result_link = utils.extract_result_link(r)  # URL for third leg

When the result status is ``complete``, the response body will contain several other fields. A timezone-aware UTC datetime object representing the expiration of the result link can be extracted using the :py:func:`extract_expires() <finra.utils.extract_expires>` function. And the ``request_id`` field containing the FINRA UUID used to uniquely identify the request can be extracted using the :py:func:`extract_request_id() <finra.utils.extract_request_id>` function.

The third and final leg of the asynchronous request operation involves fetching the result by passing the result URL to :py:meth:`Client.get_async_result() <finra.base_client.BaseClient.get_async_result>`. The result URL is *pre-signed*, meaning the caller's authentication token is not used to access the result data. Any caller with this URL can fetch the result, however it will expire 2 hours after a status code of ``200`` is received from the check status URL, or 24 hours after the result dataset is created, whichever is earlier.

.. code-block:: python

  r = c.get_async_result(result_link)  # third leg, get the data
  
  r.raise_for_status()
  
  data = r.json()                      # this is the requested dataset

Read more about `Request Types <https://developer.finra.org/docs#query_api-api_basics-api_request_types>`__ in the official API documentation.

.. _native_async_requests:

-----------------------
Natively Async Requests
-----------------------

A few datasets do not follow the operation flow described above, and instead handle the second leg of the asynchronous request natively through their own API endpoint. For these datasets, extract the ``request_id`` from the response in the first leg, and pass it back to the same query method to check the status of the request. Notable examples that implement this pattern include :py:meth:`Client.get_composite_individual_seed() <finra.base_client.BaseClient.get_composite_individual_seed>` and :py:meth:`Client.get_firm_renewal() <finra.base_client.BaseClient.get_firm_renewal>` in the Registration group, as well as most of the :ref:`submission` endpoints. See the client's reference documentation for details about specific datasets.

.. _large_datasets:

+++++++++++++++++++++++++++
Working with Large Datasets
+++++++++++++++++++++++++++

When working with large datasets that contain more records than the **maximum record limit (5,000 synchronous / 100,000 asynchronous)** an application must be designed to access the data in tranches that honor the `Platform Usage Limits <https://developer.finra.org/docs#getting_started-api_platform_basics-platform_usage_limits>`__.

The examples in this section are intended to demonstrate specific API concepts, not as production routines. In almost all cases, you should write your own routine that suits your application's needs.

----------
Pagination
----------

To facilitate accessing data in tranches, many datasets support pagination. These datasets have ``limit`` and ``offset`` keywords in their query method:

- ``limit`` : the number of records to request (default: 1,000)
- ``offset`` : the record number to start with (non-inclusive)

For example, if the ``offset`` is 0 and the ``limit`` is 20, then records 1 to 20 are returned for a total of 20 records. If the ``offset`` is 10 and the ``limit`` is 10, then records 11 to 20 are returned.

The ``offset`` parameter has a maximum value of 500,000. The effect of this constraint is that a maximum of 505,000 records can be accessed synchronously, and a maximum of 600,000 records can be accessed asynchronously, without the use of additional ``filters``. For example, the :py:class:`WeeklySummary <finra.base_client.BaseClient.WeeklySummary>` dataset contains millions of records. Because of the 500,000 maximum ``offset``, it is not possible to access all records simply by increasing the ``offset`` parameter until all data is accessed.

Instead, ``filters`` must be used together with the ``limit`` and ``offset`` parameters to reduce the size of the result set. For example, the :py:class:`WeeklySummary <finra.base_client.BaseClient.WeeklySummary>` dataset can be filtered by its partition fields, allowing each partition to be paginated independently without exceeding the API's maximum ``offset`` value.

------------------
Iterate Partitions
------------------

Many large datasets require the use of partition fields to access and sort tranches of data. To fetch data in sorted order, a request must include a compare filter on each of the partition fields for a dataset (see :ref:`sorting`). Most datasets only have a single partition field, however :py:class:`WeeklySummary <finra.base_client.BaseClient.WeeklySummary>` is so large that it has two: :py:attr:`WeeklySummary.WEEK_START_DATE <finra.base_client.BaseClient.WeeklySummary.WEEK_START_DATE>` and :py:attr:`WeeklySummary.TIER_IDENTIFIER <finra.base_client.BaseClient.WeeklySummary.TIER_IDENTIFIER>`.

The following example fetches data for all ``T1`` securities with more than 10,000 weekly trades, with week start dates going back through 2026. It returns the data sorted first by number of trades in descending order, and then by symbol in ascending order.

.. code-block:: python

  from finra.filters import Filter
  
  r = c.get_weekly_summary(endpoint=c.Endpoint.PARTITIONS)
  r.raise_for_status()
  partitions = r.json()       # partitions for this dataset
  
  e = c.WeeklySummary         # enum for this dataset
  ct = Filter.CompareType
  
  data = {}  # output data {partition date: list of records}
  for p in partitions["availablePartitions"]:  # dates are in descending order
      d, t = p["partitions"]  # date string yyyy-MM-dd, and tier identifier
      if d < "2026-01-01":    # skip dates prior to 2026
          continue
      if t != "T1":           # only NMS tier one securities
          continue
      
      r = c.get_weekly_summary(
          filters=(
              Filter(e)
                  .add_compare(e.WEEK_START_DATE, d)  # primary partition
                  .add_compare(e.TIER_IDENTIFIER, t)  # secondary partition
                  .add_compare(e.TOTAL_TRADES, 10_000, ct.GREATER)
              ),
          sort_fields=[(-1, e.TOTAL_TRADES), e.SYMBOL]
          )
      
      r.raise_for_status()
      
      data[d] = r.json()      # aggregate output data

Due to the API's maximum record limit, this query will only fetch up to the maximum number of records for each partition. In general, selecting all of the requested records will require pagination (see the following examples).

-------------------------
Partitions and Pagination
-------------------------

In this example, ``limit`` and ``offset`` are used to fetch records matching the filter conditions for all ``T1`` securities with week start dates going back through 2026. It fetches symbols with more than 10,000 weekly trades, and sorts the data first by number of trades in descending order, and then by symbol in ascending order.

.. code-block:: python

  from collections import defaultdict
  
  from finra.filters import Filter
  
  r = c.get_weekly_summary(endpoint=c.Endpoint.PARTITIONS)
  r.raise_for_status()
  partitions = r.json()        # partitions for this dataset
  
  e = c.WeeklySummary          # enum for this dataset
  ct = Filter.CompareType
  
  limit = 1_000                # must be <= maximum record limit for query
  data = defaultdict(list)     # output data {partition date: list of records}
  for p in partitions["availablePartitions"]:  # dates are in descending order
      d, t = p["partitions"]   # date string yyyy-MM-dd, and tier identifier
      if d < "2026-01-01":     # skip dates prior to 2026
          continue
      if t != "T1":            # only NMS tier one securities
          continue
      
      offset = 0               # initial offset for partition
      while True:              # pagination loop
          r = c.get_weekly_summary(
              filters=(
                  Filter(e)
                      .add_compare(e.WEEK_START_DATE, d) # primary partition
                      .add_compare(e.TIER_IDENTIFIER, t) # secondary partition
                      .add_compare(e.TOTAL_TRADES, 10_000, ct.GREATER)
                  ),
              sort_fields=[(-1, e.TOTAL_TRADES), e.SYMBOL],
              limit=limit,
              offset=offset
              )
          
          r.raise_for_status()
          
          _data = r.json()
          data[d].extend(_data)   # aggregate output data
          
          if len(_data) < limit:  # exit loop if fewer records than limit
              break               # may exit early if payload size constrained
          
          offset += limit         # increment next page offset

However, this query pattern does not guarantee that all matching records will be fetched, even if the ``limit`` is less than the maximum record limit. This is because the API also has a maximum payload size constraint of 3MB, which limits the data returned in each request regardless of the value of ``limit``. If the maximum payload size is the limiting constraint, this query pattern will exit early, and fail to fetch all of the requested records. To mitigate this issue, do one or more of the following:

- adapt pagination variables using response headers (see the next example)
- reduce the payload size by requesting fewer fields
- reduce the payload size by requesting ``text/plain`` content
- use asynchronous requests, which do not have a maximum payload size

-------------------
Adaptive Pagination
-------------------

The response headers returned by the API contain important information that can be used to adapt pagination loops. In general, the number of records returned by a single synchronous query can be limited by either the maximum record limit, or by the maximum payload size of 3MB. This can lead to unexpected behavior unless the application monitors the response headers.

The :py:mod:`finra.utils` module provides functions to simplify handling response headers, which can be used with ``httpx.Response`` objects. The following example uses :py:func:`extract_record_total() <finra.utils.extract_record_total>`, which returns the total number of records found at the time of the request, to determine when all of the data has been retrieved. The :py:func:`extract_record_max_limit() <finra.utils.extract_record_max_limit>` function is used to reduce the initial ``limit`` to the maximum record limit, if it is greater. Additionally, several assert statements are included as commented lines to demonstrate other response header utilities and their expected values.

.. code-block:: python

  from finra import utils
  
  limit = 1_000         # initial limit
  offset = 0            # initial offset
  record_total = 0      # total records available for query
  data = []             # output data
  while True:           # pagination loop
      r = c.get_weekly_summary(
          limit=limit,
          offset=offset
          )
      
      r.raise_for_status()
      
      _data = r.json()            # new records
      count = len(_data)          # count of new records
      # assert count <= utils.extract_record_limit(r)            # expected
      # assert offset == utils.extract_record_offset(r)          # expected
      
      if count == 0:              # fail-safe, prevent infinite loop
          raise Exception(
              "Something went wrong. No records returned. Response:\n" + \
              r.text
              )
      
      data.extend(_data)          # aggregate output data
      offset += count             # increment offset ( == len(data) )
      
      if record_total == 0:       # first iteration only
          record_total = utils.extract_record_total(r)  # set record total
          if record_total is None:
              raise Exception("Record Total not found in headers!")
          
          limit = min(limit, utils.extract_record_max_limit(r))  # adapt limit
          # assert limit == utils.extract_record_limit(r)        # expected
      
      if offset >= record_total:  # all records have been retrieved
          break

Three additional response headers may also be useful: see :py:func:`extract_response_payload_max_size() <finra.utils.extract_response_payload_max_size>`, :py:func:`extract_total_records_on_page() <finra.utils.extract_total_records_on_page>`, and :py:func:`extract_finra_api_request_id() <finra.utils.extract_finra_api_request_id>`.

.. _content_types:

+++++++++++++
Content Types
+++++++++++++

--------------------
Default Content Type
--------------------

Within this client, the response content type defaults to ``application/json``. However, many datasets support ``text/plain`` response content when querying their :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` endpoint. All other :ref:`endpoints <endpoints>` return only ``application/json`` content.

The default response content type can be changed to ``text/plain`` by passing ``False`` to :py:meth:`Client.set_default_accept_json() <finra.base_client.BaseClient.set_default_accept_json>`. Pass ``True`` for ``application/json``, or ``None`` for the API's default. Data will only be returned as ``text/plain`` if the dataset being queried supports it. To get the current default content type, call :py:meth:`Client.get_default_accept_json() <finra.base_client.BaseClient.get_default_accept_json>`.

When requesting ``text/plain`` content, the data can be accessed through the ``httpx.Response.text`` attribute.

.. code-block:: python

  c.set_default_accept_json(False)  # ALL responses text/plain, if supported
  
  r = c.get_consolidated_short_interest()  # comma-delimited, unquoted values
  
  r.raise_for_status()
  
  data = r.text                     # text data from response attribute

-------------------------------
Content Type for a Single Query
-------------------------------

For a single query, the response content type can be changed using the boolean-valued ``accept_json`` keyword, if it is supported by the dataset's query method. When requesting ``text/plain`` content, two additional keywords can be used to configure the response data:

- ``delimiter`` : a single-character that separates fields, which must be one of the following values: comma ``,``, pipe ``|``, tab ``\\t`` or ``\\x09``, or ctrl+A ``\\x01`` (default: comma ``,``)
- ``quote_values`` : a boolean specifying whether non-empty values should be quoted (default: ``False``)

In this example, the query requests ``text/plain`` content type, with a non-default field ``delimiter`` and quoted values.

.. code-block:: python

  from finra import utils
  
  r = c.get_consolidated_short_interest(
      accept_json=False,     # text/plain for this request only
      delimiter="|",         # fields are pipe-delimited
      quote_values=True      # all non-empty values have quotes
      )
  
  r.raise_for_status()
  
  assert utils.extract_content_type(r) == "text/plain"  # verify content type
  
  data = r.text              # text data from response attribute

The response content type can also be retrieved from the response headers using the :py:func:`extract_content_type() <finra.utils.extract_content_type>` function.

.. _relabeler:

++++++++++++++++++++++++
Relabeling Response Data
++++++++++++++++++++++++

Response data is returned with the field names used by the API. This labeling scheme can be inconvenient if an application requires a different set of field names to process records downstream.

To mitigate this issue, this library provides the :py:class:`RelabelJSON <finra.utils.RelabelJSON>` class that can be used to relabel both flat response data and nested JSON objects. It accepts a mapping as the first argument during instantiation, which can either be a dataset's enum, or a ``dict`` that maps the API's labels to the application's canonical labels. To relabel response data, just call the :py:class:`RelabelJSON <finra.utils.RelabelJSON>` object with the ``httpx.Response`` returned by a query, or the JSON data returned by ``httpx.Response.json()``.

The following example relabels flat response data with names from a dataset's enum.

.. code-block:: python

  from finra.utils import RelabelJSON
  
  e = c.WeeklySummary            # enum for this dataset
  
  r = c.get_weekly_summary()
  
  r.raise_for_status()
  
  relabeler = RelabelJSON(e)     # set the relabel mapping using the enum
  
  relabeled_data = relabeler(r)  # relabel response data with enum names

Response data that has a nested JSON object structure can also be relabeled. Labels can be specified using a period-delimited (``.``) syntax, or using a nested mapping that contains only strings and dictionaries; relabel mappings are applied to all objects in an array. An optional secondary mapping can be set using the ``obj_labels`` argument to relabel the keys of nodes containing objects or arrays. The ``obj_labels`` mapping is a flat mapping that will relabel object node keys regardless of the depth of the node.

The following example relabels nested response data based on the dataset's enum. The enum for this dataset has values that follow a period-delimited (``.``) syntax, indicating the response data will be returned as a nested JSON object.

.. code-block:: python

  from finra.utils import RelabelJSON
  
  e = c.FirmProfile              # enum for this dataset
  
  r = c.get_firm_profile()
  
  r.raise_for_status()
  
  obj_labels = {
      "firmAddress": "ADDRESS",
      "registrations": "REGISTRATIONS",
      }  # flat mapping for object node keys {API's label: canonical label}
  
  relabeler = RelabelJSON(e, obj_labels=obj_labels)     # relabel object nodes
  
  relabeled_data = relabeler(r)

The example below uses a relabel mapping for a JSON object with one leaf node and two object nodes. For demonstration purposes the relabel mapping uses the period-delimited (``.``) syntax for the "registrations" object, and a nested mapping for the "disclosures" object. Both of these nodes are populated by arrays of objects, so the relabel mapping is applied to all objects in the array.

.. code-block:: python

  from finra.utils import RelabelJSON
  
  relabel_mapping = {
      "firmCrdNumber": "FIRM_CRD_NUMBER",
      "disclosures": {                                  # nested mapping
          "disclosureType": "DISCLOSURE_TYPE",
          "occurrenceNumber": "OCCURRENCE_NUMBER",
          "reportableFlag": "REPORTABLE_FLAG",
          "disclosableFlag": "DISCLOSABLE_FLAG",
          "archivedFlag": "ARCHIVED_FLAG",
          "eventDate": "EVENT_DATE",
          },
      "registrations.regulatorCode": "REGULATOR_CODE",  # period-delimited
      }
  
  r = c.get_firm_disclosures()
  
  r.raise_for_status()
  
  relabeler = RelabelJSON(relabel_mapping)  # set the relabel mapping
  
  relabeled_data = relabeler(r)  # relabel data with canonical labels

The default behavior is to re-order the response data so that it has the same order as the relabel mapping. However if the label order is unimportant, this can be disabled by setting ``keep_label_order=False`` when instantiating the relabeler object, which makes relabeling slightly faster. If ``keep_label_order=True``, any fields that are not contained in the relabel mapping will still be returned with the API's label, but sorted to the bottom of the record and in the order returned in the response.

