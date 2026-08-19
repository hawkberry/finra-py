.. highlight:: python

.. _help:

============
Getting Help
============

This page describes how to troubleshoot problems, report bugs, and get assistance with ``finra-py``.

.. _debug:

+++++++++++++
Bug Reporting
+++++++++++++

If you are experiencing a problem with the client, first ensure you're using the most recent version. You can see the version you're using by running ``from importlib import metadata as md; print(md.version('finra-py'))`` from within Python. You can also make sure you have the most recent version by executing the command ``pip install --upgrade finra-py``. If you are running the most recent version, and you are still experiencing problems, the next step is to enable logging and inspect the output.

--------------
Enable Logging
--------------

This client library performs diagnostic logging of its activity using Python's `logging <https://docs.python.org/3/library/logging.html>`__ module. To enable logging, add a handler to the root logger. The default output stream for `StreamHandler <https://docs.python.org/3/library/logging.handlers.html#logging.StreamHandler>`__ is ``sys.stderr``.

.. code-block:: python

  import logging
  
  logging.getLogger('').addHandler(logging.StreamHandler())  # write to stderr
  
Sometimes, this additional logging is enough to help you debug your application. Before asking for help, carefully review the logs and determine whether you can identify and resolve the issue yourself. You may be the best person to investigate and fix it!

------------------
Bug Report Logging
------------------

If you still can't figure out what's going wrong, this library provides a special utility for preparing bug reports that collects diagnostic logs. This utility redacts sensitive values and common secrets such as tokens, API keys, CRD numbers, SSNs, DOBs, etc. If you need to provide logs in a bug report, please use this utility to generate the logs you submit, and write them to a file (see the second example below). It is not necessary to separately enable logging (as in the previous example); the bug reporting utility configures the required logging automatically.

**IMPORTANT: Log redaction is only a best effort, and is not guaranteed to be perfect. Never share your logs without verifying that all secret information has been properly redacted. It is your responsibility to ensure that your information is secure.**

The bug report utility configures dedicated loggers for the ``finra-py`` client, authentication, and debug modules. The logging handlers created by this utility write diagnostic logs from ``finra-py`` to the configured stream or file. Users may provide their own stream or file destination, but any additional logging written to that destination by external code is outside the control of this library. When filing bug reports, provide this utility a dedicated log file location so that the file contains only ``finra-py`` logs.

The bug report utility (and the ``DEBUG`` log-level in general) is not designed to be used in production code. All logged output is recorded, which creates a performance penalty. Be aware that a value collision can occasionally occur during redaction, which may result in unintended fields being redacted or inaccurate redaction labels.

The recommended practice is to enable bug report logging at the beginning of your program so that the entire API interaction is recorded. To terminate bug report logging, exit the program.

.. code-block:: python

  from finra.debug import enable_bug_report_logging
  
  enable_bug_report_logging()  # enable at beginning, log to sys.stderr
  
  # ...get a client
  # ...do some requests
  # ...then exit the program
  
When submitting logs as part of a bug report, write the logs to a file by passing the ``filename`` as the first argument. Unless explicitly turned off, the default behavior is to also write logs to ``sys.stderr``. To turn this functionality off explicitly set ``stream=None``. You can also write to a custom stream by passing the file-like stream object as the ``stream`` keyword argument.

.. code-block:: python

  from finra.debug import enable_bug_report_logging
  
  filename = 'my_log_file.txt'  # some log file
  
  enable_bug_report_logging(filename=filename, stream=None) # only log to file
  
  # ...get a client
  # ...do some requests
  # ...then exit the program
  
------------------
Submit Your Ticket
------------------

You are now ready to write your bug report. Before submitting an issue, please ensure it includes the following information. Issues may be closed if they cannot be investigated effectively:
 
- Include code: reproducing the reported behavior requires code demonstrating the failure.
- Include logs: it is difficult to debug problems without logs.
- Redact logs: issues may be closed or deleted if logs are not adequately redacted. This is for your own protection.
- Attach log files: logs that are copy-pasted into the issue message field will not be accepted. Please write them to a file and attach it to your issue.
- Follow the issue template: this is not strict, but you should at least include all the information it asks for.
 
You can file an issue on the ``finra-py`` `Issues Page <https://github.com/hawkberry/finra-py/issues>`__ on GitHub.

.. _known_bugs:

++++++++++++++++++++++
Known FINRA API Issues
++++++++++++++++++++++

Before reporting bugs on GitHub, please make sure your issue is due to the client implementation, and not the FINRA API.

The FINRA API has a number of known behaviors and inconsistencies that may appear to be client issues. These issues have been reported to FINRA, but some may remain unresolved for an extended period of time.

The following is a list of known FINRA API issues and inconsistencies. This list is not exhaustive, and you may encounter issues that are not yet documented here. This section will be updated as known issues are resolved or new issues are discovered.

--------------
Submission API
--------------

The Submission API has several discepancies between the FINRA API documentation and the values defined in the JSON Schemas. Many of the examples in the Submission API are also inconsistent with the JSON Schema definitions, but those are beyond the scope of this section.

#. The API documentation for Form BR lists ``WITHDRAW`` or ``CLOSUREWITHDRAW`` as valid filing types, however the `Form BR JSON Schema <https://schemas.api.finra.org/FINRAApiPlatformBRFiling.json>`__ definition does not allow these values (see the `Metadata Schema <https://schemas.api.finra.org/FINRAApiPlatformBRFilingMetadata.json>`__). The Form BR JSON Schema definition shows that only ``AMENDMENT``, ``CLOSURE`` and ``INTIAL`` filing types are accepted. For now, the client library will keep these filing types implemented on :py:class:`FormBR <finra.filings.form_br.FormBR>` unless they are removed from the documentation.
   
#. The API documentation  for Form U5 lists ``ignoreWarnings`` as a valid metadata property, however the `Form U5 JSON Schema <https://schemas.api.finra.org/FINRAApiPlatformU5Filing.json>`__ definition does not list this as a required value and does not allow additional properties (see the `Metadata Schema <https://schemas.api.finra.org/FINRAApiPlatformU5FilingMetadata.json>`__). For now, the client library will keep this feature implemented on :py:class:`FormU5 <finra.filings.form_u5.FormU5>` unless it is removed from the documentation.
   
--------------------
Query Production API
--------------------

This section includes issues and inconsistencies for Query API production datasets.

#. The :py:class:`BaseClient.get_weekly_summary() <finra.base_client.BaseClient.get_weekly_summary>` production and mock datasets, and :py:class:`BaseClient.get_weekly_summary_historic() <finra.base_client.BaseClient.get_weekly_summary_historic>` production dataset, contain undocumented values in the :py:attr:`WeeklySummary.TIER_IDENTIFIER <finra.base_client.BaseClient.WeeklySummary.TIER_IDENTIFIER>` partition field: ``NA`` and ``NMS``. They also contain undocumented :py:attr:`WeeklySummary.TIER_DESCRIPTION <finra.base_client.BaseClient.WeeklySummary.TIER_DESCRIPTION>` values: ``Not Applicable`` and ``OTC`` (typo?). These values are present in both :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>` and :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>`, but are not in the FINRA API documentation.
   
#. The :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>` for the :py:class:`BaseClient.get_individual_registration_validation() <finra.base_client.BaseClient.get_individual_registration_validation>` production and mock datasets are missing the ``datasetGroup`` and ``datasetName`` properties.
   
#. For production and mock datasets, :py:class:`BaseClient.get_individual_registration_validation_details() <finra.base_client.BaseClient.get_individual_registration_validation_details>` returns erroneous :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>` that does not match the JSON Schemas for either versions of this dataset.
   
#. The following Fixed Income production and mock datasets do not support partitions, however they return inconsistent status codes when querying :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>`; the response returns ``200``, but the ``statusCode`` field returns ``500 Internal Server Error``:
   
   - :py:class:`BaseClient.get_agency_tba_pricing() <finra.base_client.BaseClient.get_agency_tba_pricing>`
   - :py:class:`BaseClient.get_agency_cmo_pricing() <finra.base_client.BaseClient.get_agency_cmo_pricing>`
   - :py:class:`BaseClient.get_agency_mbs_trading_activity() <finra.base_client.BaseClient.get_agency_mbs_trading_activity>`
   - :py:class:`BaseClient.get_agency_mbs_arm_hybrid_pricing() <finra.base_client.BaseClient.get_agency_mbs_arm_hybrid_pricing>`
   - :py:class:`BaseClient.get_agency_mbs_pricing() <finra.base_client.BaseClient.get_agency_mbs_pricing>`
   - :py:class:`BaseClient.get_collateralized_obligations_pricing() <finra.base_client.BaseClient.get_collateralized_obligations_pricing>`
   - :py:class:`BaseClient.get_daily_cmbs_pricing() <finra.base_client.BaseClient.get_daily_cmbs_pricing>`
   - :py:class:`BaseClient.get_non_agency_cmo_abs_pricing() <finra.base_client.BaseClient.get_non_agency_cmo_abs_pricing>`
   - :py:class:`BaseClient.get_non_agency_cmo_pricing() <finra.base_client.BaseClient.get_non_agency_cmo_pricing>`
   - :py:class:`BaseClient.get_securitized_products_errata() <finra.base_client.BaseClient.get_securitized_products_errata>`
   - :py:class:`BaseClient.get_securitized_products_trading_activity() <finra.base_client.BaseClient.get_securitized_products_trading_activity>`
   - :py:class:`BaseClient.get_weekly_cmbs_pricing() <finra.base_client.BaseClient.get_weekly_cmbs_pricing>`
   
--------------
Query Mock API
--------------

This section includes issues and inconsistencies for Query API mock datasets retrieved using mock credential types. It's possible that some of these are also found in the production datasets, but have not been enumerated in the previous section. If you discover that is the case, please file an issue on the ``finra-py`` `Issues Page <https://github.com/hawkberry/finra-py/issues>`__ on GitHub so this page can be updated.

#. Some mock datasets return empty for :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>` and :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>`, even when returning a ``200`` status code. Requests with no data should return a ``204``.
   
#. The :py:class:`BaseClient.get_weekly_summary() <finra.base_client.BaseClient.get_weekly_summary>` and :py:class:`BaseClient.get_monthly_summary() <finra.base_client.BaseClient.get_monthly_summary>` production datasets contain a :py:attr:`WeeklySummary.TOTAL_NOTIONAL_SUM <finra.base_client.BaseClient.WeeklySummary.TOTAL_NOTIONAL_SUM>` field in the :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>` and :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` that is not present in the mock datasets.
   
#. The :py:meth:`BaseClient.get_otc_daily_list() <finra.base_client.BaseClient.get_otc_daily_list>` mock dataset returns a ``404 Not Found`` status code for all endpoints, and for asynchronous requests.
   
#. Async requests on the **first leg** for the following Fixed Income mock datasets return a ``500 Internal Server Error`` status code:
   
   - :py:class:`BaseClient.get_agency_tba_pricing() <finra.base_client.BaseClient.get_agency_tba_pricing>`
   - :py:class:`BaseClient.get_agency_cmo_pricing() <finra.base_client.BaseClient.get_agency_cmo_pricing>`
   - :py:class:`BaseClient.get_agency_mbs_trading_activity() <finra.base_client.BaseClient.get_agency_mbs_trading_activity>`
   - :py:class:`BaseClient.get_agency_mbs_arm_hybrid_pricing() <finra.base_client.BaseClient.get_agency_mbs_arm_hybrid_pricing>`
   - :py:class:`BaseClient.get_agency_mbs_pricing() <finra.base_client.BaseClient.get_agency_mbs_pricing>`
   - :py:class:`BaseClient.get_collateralized_obligations_pricing() <finra.base_client.BaseClient.get_collateralized_obligations_pricing>`
   - :py:class:`BaseClient.get_daily_cmbs_pricing() <finra.base_client.BaseClient.get_daily_cmbs_pricing>`
   - :py:class:`BaseClient.get_non_agency_cmo_abs_pricing() <finra.base_client.BaseClient.get_non_agency_cmo_abs_pricing>`
   - :py:class:`BaseClient.get_non_agency_cmo_pricing() <finra.base_client.BaseClient.get_non_agency_cmo_pricing>`
   - :py:class:`BaseClient.get_securitized_products_errata() <finra.base_client.BaseClient.get_securitized_products_errata>`
   - :py:class:`BaseClient.get_securitized_products_trading_activity() <finra.base_client.BaseClient.get_securitized_products_trading_activity>`
   - :py:class:`BaseClient.get_weekly_cmbs_pricing() <finra.base_client.BaseClient.get_weekly_cmbs_pricing>`
   
#. Async requests on the **first leg** for the following Firm mock datasets return asynchronously (as expected) when queried without the ``firm_crd_number``, but return **synchronously** when queried with the ``firm_crd_number`` (single-record query):
   
   - :py:class:`BaseClient.get_firm_disclosures() <finra.base_client.BaseClient.get_firm_disclosures>`
   - :py:class:`BaseClient.get_firm_profile() <finra.base_client.BaseClient.get_firm_profile>`
   - :py:class:`BaseClient.get_firm_registration_status_history() <finra.base_client.BaseClient.get_firm_registration_status_history>`
   - :py:class:`BaseClient.get_firm_registrations() <finra.base_client.BaseClient.get_firm_registrations>`
   
#. Async requests on the **first leg** for the following Registration mock datasets return a ``404 Not Found`` status code:
   
   - :py:class:`BaseClient.get_individual_registration_validation() <finra.base_client.BaseClient.get_individual_registration_validation>`
   - :py:class:`BaseClient.get_individual_registration_validation_details() <finra.base_client.BaseClient.get_individual_registration_validation_details>`
   
#. Async requests on the **first leg** for the following TRACE Report Card mock datasets return a ``403 Forbidden`` status code:
   
   - :py:class:`BaseClient.get_trace_agency_debt_summary() <finra.base_client.BaseClient.get_trace_agency_debt_summary>`
   - :py:class:`BaseClient.get_trace_treasuries_summary() <finra.base_client.BaseClient.get_trace_treasuries_summary>`
   - :py:class:`BaseClient.get_trace_corporate_bonds_summary() <finra.base_client.BaseClient.get_trace_corporate_bonds_summary>`
   - :py:class:`BaseClient.get_trace_securitized_products_summary() <finra.base_client.BaseClient.get_trace_securitized_products_summary>`
   
#. Async requests on the **second leg** for **ALL** Equity (OTCMarket) mock datasets return a ``403 Forbidden`` status code.
   
#. Async requests on the **second leg** for the :py:class:`BaseClient.get_firm_registration_types() <finra.base_client.BaseClient.get_firm_registration_types>` mock dataset returns a ``403 Forbidden`` status code.
   
#. The :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` for the :py:class:`BaseClient.get_accounting() <finra.base_client.BaseClient.get_accounting>` mock dataset does not filter dates correctly when ``start_date`` and ``end_date`` parameters are provided, and instead returns dates outside the queried range.
   
#. The :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` for the :py:class:`BaseClient.get_branch_delta() <finra.base_client.BaseClient.get_branch_delta>` and :py:class:`BaseClient.get_individual_delta() <finra.base_client.BaseClient.get_individual_delta>` mock datasets do not filter dates correctly when ``start_datetime`` and ``end_datetime`` parameters are provided, and instead returns dates outside the queried range.
   
#. The :py:class:`BaseClient.get_composite_branch() <finra.base_client.BaseClient.get_composite_branch>` mock dataset does not filter based on provided :py:class:`BaseClient.CompositeBranchSections <finra.base_client.BaseClient.CompositeBranchSections>`. Instead it returns all sections, regardless of the sections filter. This is in contrast to the :py:class:`BaseClient.get_composite_individual() <finra.base_client.BaseClient.get_composite_individual>` mock dataset, which has similar section filtering functionality, and behaves as expected.
   
#. The :py:class:`BaseClient.get_individual_pre_registration_search() <finra.base_client.BaseClient.get_individual_pre_registration_search>` mock dataset returns field names that are inconsistent with the :py:attr:`Endpoint.METADATA <finra.base_client.BaseClient.Endpoint.METADATA>`.
   
#. The :py:class:`BaseClient.get_individual_registration_validation() <finra.base_client.BaseClient.get_individual_registration_validation>` mock dataset returns a  ``404 Not Found`` status code.
   
#. The :py:class:`BaseClient.get_registered_individual_search() <finra.base_client.BaseClient.get_registered_individual_search>` mock dataset returns a ``middleName`` field that is not in production or mock metadata. This field cannot be used as a ``fields`` or ``sort_fields`` query parameter.
   
#. The :py:attr:`Endpoint.DATASETS <finra.base_client.BaseClient.Endpoint.DATASETS>` for the :py:class:`BaseClient.get_broker_dealer_firm_list() <finra.base_client.BaseClient.get_broker_dealer_firm_list>` mock dataset **Version 2** shows ``supportedGetById`` as ``True``, indicating that the dataset supports single record query. This is incorrect, since **Version 2** of this dataset passes the Individual CRD Number as a query parameter, rather than accessing a URL subpath. This is also inconsistent with the value of ``supportedGetById`` shown for the production dataset.
   
#. The :py:attr:`Endpoint.DATASETS <finra.base_client.BaseClient.Endpoint.DATASETS>` for the :py:class:`BaseClient.get_broker_dealer_firm_list() <finra.base_client.BaseClient.get_broker_dealer_firm_list>` mock dataset shows ``supportsRecordLimit`` and ``supportsRecordOffset`` as ``False``, indicating that this dataset does not supports pagination. The :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` for the mock dataset also does not accept ``limit`` and ``offset`` keywords. However, this is inconsistent with the production dataset which show ``supportsRecordLimit`` and ``supportsRecordOffset`` as ``True``. Therefore, pagination is implemented in the client's query method.
   
#. The :py:attr:`Endpoint.DATASETS <finra.base_client.BaseClient.Endpoint.DATASETS>` for the :py:class:`BaseClient.get_u4_form_prefill() <finra.base_client.BaseClient.get_u4_form_prefill>` mock dataset shows ``supportsRecordLimit`` as ``True`` (even though ``supportsRecordOffset`` is ``False``), indicating that this dataset supports pagination. However, this is inconsistent with the production dataset which show ``supportsRecordLimit`` as ``False``. Therefore, pagination is **not** implemented in the client's query method.
   
#. The following Registration and TRACE Report Card mock datasets do not support partitions, however they return inconsistent status codes when querying :py:attr:`Endpoint.PARTITIONS <finra.base_client.BaseClient.Endpoint.PARTITIONS>`, with the response returning a ``200``, but the ``statusCode`` field shows a ``500 Internal Server Error``:
   
   - :py:class:`BaseClient.get_accounting() <finra.base_client.BaseClient.get_accounting>`
   - :py:class:`BaseClient.get_branch_delta() <finra.base_client.BaseClient.get_branch_delta>`
   - :py:class:`BaseClient.get_branch_list() <finra.base_client.BaseClient.get_branch_list>`
   - :py:class:`BaseClient.get_broker_dealer_firm_list() <finra.base_client.BaseClient.get_broker_dealer_firm_list>`
   - :py:class:`BaseClient.get_composite_branch() <finra.base_client.BaseClient.get_composite_branch>`
   - :py:class:`BaseClient.get_composite_individual() <finra.base_client.BaseClient.get_composite_individual>`
   - :py:class:`BaseClient.get_individual_delta() <finra.base_client.BaseClient.get_individual_delta>`
   - :py:class:`BaseClient.get_individual_pre_registration_search_v2() <finra.base_client.BaseClient.get_individual_pre_registration_search_v2>`
   - :py:class:`BaseClient.get_u4_form_prefill() <finra.base_client.BaseClient.get_u4_form_prefill>`
   - :py:class:`BaseClient.get_trace_agency_debt_summary() <finra.base_client.BaseClient.get_trace_agency_debt_summary>`
   - :py:class:`BaseClient.get_trace_treasuries_summary() <finra.base_client.BaseClient.get_trace_treasuries_summary>`
   - :py:class:`BaseClient.get_trace_corporate_bonds_summary() <finra.base_client.BaseClient.get_trace_corporate_bonds_summary>`
   - :py:class:`BaseClient.get_trace_securitized_products_summary() <finra.base_client.BaseClient.get_trace_securitized_products_summary>`
   

