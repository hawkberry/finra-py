.. highlight:: python

.. _submission:

==============
Submission API
==============

If you haven't read :ref:`getting_started`, :ref:`auth` and :ref:`client`, please start by reading those sections.

The `Submission API <https://developer.finra.org/docs#submission_api>`__ allows third-party systems to automate compliance operations by submitting regulatory filings and other data directly to FINRA.

Each filing has a single method for submitting, validating and retrieving filing data. All endpoints require Firm credentials.
 
 - :py:meth:`Client.create_individual_submission() <finra.base_client.BaseClient.create_individual_submission>`
 - :py:meth:`Client.form_br_submission() <finra.base_client.BaseClient.form_br_submission>`
 - :py:meth:`Client.form_u4_submission() <finra.base_client.BaseClient.form_u4_submission>`
 - :py:meth:`Client.form_u5_submission() <finra.base_client.BaseClient.form_u5_submission>`
 - :py:meth:`Client.non_registered_fingerprint_submission() <finra.base_client.BaseClient.non_registered_fingerprint_submission>`
 
Each of the following classes corresponds to a specific filing. They are useful for building metadata for submissions, and configuring partial update operations.
 
 - :py:class:`CreateIndividual <finra.filings.create_individual.CreateIndividual>`
 - :py:class:`FormBR <finra.filings.form_br.FormBR>`
 - :py:class:`FormU4 <finra.filings.form_u4.FormU4>`
 - :py:class:`FormU5 <finra.filings.form_u5.FormU5>`
 - :py:class:`NonRegisteredFingerprint <finra.filings.non_registered_fingerprint.NonRegisteredFingerprint>`
  
.. _request_flow:

++++++++++++
Request Flow
++++++++++++

Each time a submission request is created, the API generates a universally unique identifier (UUID) that is used to uniquely identify the submission request. This UUID is returned in the body of the ``httpx.Response`` and referred to as the ``request_id`` throughout the documentation. It can be used in subsequent requests to update, delete or retrieve the filing. The ``request_id`` can be extracted using :py:func:`extract_filing_request_id() <finra.utils.extract_filing_request_id>`. To retrieve the results for the request, pass the ``request_id`` back to the filing's submission method as an argument.

Submission requests are processed synchronously or asynchronously depending on the filing. Synchronous submissions are processed immediately, and will return the result status immediately provided there are no server-side validation errors. The only filing that currently supports synchronous submission requests is :py:class:`CreateIndividual <finra.filings.create_individual.CreateIndividual>`. All other submission filings are asynchronous.

For asynchronous submissions, the API will process the request in the background, as long as the submission passes the server-side validation check. The submission response will contain the ``request_id``, but it does not include information on the processing itself, which must be retrieved in a subsequent request using the ``request_id``. Background processing can take from 5 to 15 minutes when the :ref:`filing_status` is :py:attr:`FilingStatus.SUBMITTED <finra.filings.base_filing.BaseFilingOps.FilingStatus.SUBMITTED>`, and FINRA asks users to wait at least this long before requesting the result status.

If a server-side validation failure does occur, the ``filing_status`` will be set to ``DRAFT``, if the filing supports it. Information related to the validation error can be retrieved by calling the submission method with the ``request_id``. The response will contain a ``result_status`` field with the value ``FAILED_VALIDATION``, which can be extracted using :py:func:`extract_filing_result_status() <finra.utils.extract_filing_result_status>`. The ``result_status_description`` field will include any error and warning messages, which can be extracted using :py:func:`extract_filing_result_status_desc() <finra.utils.extract_filing_result_status_desc>`.

Read more about the `Overall Flow <https://developer.finra.org/docs#submission_api-api_basics-overall_flow>`__ of Submission API requests in the official documentation.

.. _filing_status:

+++++++++++++
Filing Status
+++++++++++++

The request flow for a submission depends on the value of the :py:class:`FilingStatus <finra.filings.base_filing.BaseFilingOps.FilingStatus>`, which specifies the state of a submission.

There are three available values:
 
 - :py:attr:`FilingStatus.DRAFT <finra.filings.base_filing.BaseFilingOps.FilingStatus.DRAFT>`
 - :py:attr:`FilingStatus.SUBMITTED <finra.filings.base_filing.BaseFilingOps.FilingStatus.SUBMITTED>`
 - :py:attr:`FilingStatus.VALIDATE <finra.filings.base_filing.BaseFilingOps.FilingStatus.VALIDATE>`
 
The :py:class:`FilingStatus <finra.filings.base_filing.BaseFilingOps.FilingStatus>` can be set on the filing object using the :py:meth:`set_filing_status() <finra.filings.base_filing.BaseFilingOps.set_filing_status>` method, if supported by the filing. The :py:class:`CreateIndividual <finra.filings.create_individual.CreateIndividual>` and :py:class:`NonRegisteredFingerprint <finra.filings.non_registered_fingerprint.NonRegisteredFingerprint>` filings only support :py:attr:`FilingStatus.SUBMITTED <finra.filings.base_filing.BaseFilingOps.FilingStatus.SUBMITTED>`, and do not allow this value to be altered.

-----------------------
Submitted Filing Status
-----------------------

The following example builds an initial submission using :py:attr:`FilingStatus.SUBMITTED <finra.filings.base_filing.BaseFilingOps.FilingStatus.SUBMITTED>` for a :py:class:`FormBR <finra.filings.form_br.FormBR>` filing. The filing is submitted to the API, and the ``request_id`` is extracted from the response.

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra import utils
  
  f = FormBR()                                   # branch office registration
  (
      f.set_filing_status(f.FilingStatus.SUBMITTED)  # finalize submission
       .set_filing_type(f.FilingType.INITIAL)        # initial filing
       .set_filing_data({...})                       # add some filing data
  )                                                  # methods chained in-line
  
  r = c.form_br_submission(filing=f)                 # submit the filing
  
  r.raise_for_status()
  
  request_id = utils.extract_filing_request_id(r)    # UUID for request

To check the status of the submission, call the same submission method again with the ``request_id`` as the first argument. The ``result_status`` will be ``PROCESSED`` when it is complete. A value of ``PROCESSING`` indicates the API server is still working, and to wait several minutes before re-checking the status. If the ``result_status`` is ``FAILED`` or ``FAILED_VALIDATION``, it means an error or warning has occurred.

.. code-block:: python

  r = c.form_br_submission(request_id)  # check the status of the submission
  
  r.raise_for_status()
  
  result_status = utils.extract_filing_result_status(r)  # done if "PROCESSED"
  
  result_status_description = \
      utils.extract_filing_result_status_desc(r)         # message / errors
  
  data = r.json()  # submission data, wrapped with response metadata

-------------------
Draft Filing Status
-------------------

The primary advantage of using draft submissions is that they can be updated and re-validated as many times as needed, without having to file amendments. The following example builds an initial draft submission using :py:attr:`FilingStatus.DRAFT <finra.filings.base_filing.BaseFilingOps.FilingStatus.DRAFT>` for a :py:class:`FormBR <finra.filings.form_br.FormBR>` filing. It submits the draft, and extracts the ``request_id`` from the response.

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra import utils
  
  f = FormBR()                                   # branch office registration
  (
      f.set_filing_status(f.FilingStatus.DRAFT)  # draft submission
       .set_filing_type(f.FilingType.INITIAL)    # initial filing
       .set_filing_data({...})                   # add some filing data
  )                                              # methods chained in-line
  
  r = c.form_br_submission(filing=f)             # submit the draft
  
  r.raise_for_status()
  
  request_id = utils.extract_filing_request_id(r)  # UUID for request

To retrieve the draft submission data, call the same submission method again with the ``request_id`` as the first argument.

.. code-block:: python

  r = c.form_br_submission(request_id)  # use the same method to get the draft
  
  r.raise_for_status()
  
  data = r.json()  # draft submission data, wrapped with response metadata

----------------------
Validate Filing Status
----------------------

A server-side completeness check can be triggered for submissions in ``DRAFT`` status, without changing the status to ``SUBMITTED``. To trigger a completeness check, create a submission with :py:attr:`FilingStatus.VALIDATE <finra.filings.base_filing.BaseFilingOps.FilingStatus.VALIDATE>`. If a draft submission does not already exist, one will be created.

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra import utils
  
  f = FormBR()                                    # branch office registration
  (
      f.set_filing_status(f.FilingStatus.VALIDATE)  # validate submission
       .set_filing_type(f.FilingType.INITIAL)       # initial filing
       .set_filing_data({...})                      # add some filing data
  )                                                 # methods chained in-line
  
  r = c.form_br_submission(filing=f)                # validate the filing
  
  r.raise_for_status()
  
  request_id = utils.extract_filing_request_id(r)   # UUID for request

To retrieve the results of the completeness check, call the same submission method again with the ``request_id`` as the first argument. If the completeness check is unsuccessful, the ``result_status`` will have the value ``FAILED_VALIDATION``, and the ``result_status_description`` will contain additional information about errors and warnings.

.. code-block:: python

  r = c.form_br_submission(request_id)  # check the status of the submission
  
  r.raise_for_status()
  
  result_status = utils.extract_filing_result_status(r) # pass or fail?
  
  result_status_description = \
      utils.extract_filing_result_status_desc(r)        # message / errors
  
  data = r.json()  # draft submission data, wrapped with response metadata
  
  filing_status = utils.extract_filing_status(r)        # should be "DRAFT"

.. _filing_type:

+++++++++++
Filing Type
+++++++++++

Filing types are specific to each filing, and identify a filing procedure such as an amendment or a withdrawal. They are required for all filings except :py:class:`CreateIndividual <finra.filings.create_individual.CreateIndividual>`.

Amendments and other filing types can be created using the full filing data, or using :ref:`operations`. In this example, an amendment is created and submitted using an operation.

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra import utils
  
  f = FormBR()                                    # branch office registration
  (
      f.set_filing_status(f.FilingStatus.SUBMITTED)  # finalize submission
       .set_filing_type(f.FilingType.AMENDMENT)      # amendment
       .add_operation(...)                           # amendment operation
  )
  
  r = c.form_br_submission(filing=f)                 # submit the amendment
  
  r.raise_for_status()
  
  request_id = utils.extract_filing_request_id(r)    # UUID for request

The one exception to this pattern is :py:class:`NonRegisteredFingerprint <finra.filings.non_registered_fingerprint.NonRegisteredFingerprint>`, which does not support ``DRAFT`` status or operations. However, amendments can be submitted using the full filing data, or just the delta changes in the filing data.

.. _operations:

++++++++++
Operations
++++++++++

Operations are instructions for updating a filing using JSON operations. If both filing data and operations are provided in a single call, operations will be ignored.

If a filing supports operations, they can be added using the filing object's :py:meth:`add_operation() <finra.filings.base_filing.BaseFilingOps.add_operation>` method, which takes three arguments:
 
 1. ``op`` is the action in a JSON operation specified as a member of the :py:class:`Op <finra.filings.base_filing.BaseFilingOps.Op>` enum.
 
 2. ``path`` specifies the location or traversal route within a JSON document. It is based on the `RFC 6901 <https://www.rfc-editor.org/rfc/rfc6901>`__ standard, except with arrays where an additional syntax is supported to uniquely identify an element within an array, instead of relying on array indexes.
 
 3. ``value`` is placed at the ``path``. For operations with :py:attr:`Op.REMOVE <finra.filings.base_filing.BaseFilingOps.Op.REMOVE>`, the ``value`` must be omitted or ``None``.
 
Consider the following example filing data:

.. code-block:: python

  {
      "individualInformation": {
          "personalInformation": {
              "individualFilingName": {
                  "middleName": null,
                  "lastName": "lexicon"
              }
          },
          "residentialHistory": [
              {
                  "id": "5f2df182-f6d0-4504-9e18-38a8c7268b77",
                  "addressStartDate": "2022-01"
              },
              {
                  "id": "c970abd7-37d2-4c7e-b695-b8cb7a0b5817",
                  "addressStartDate": "2022-01"
              }
          ]
      }
  }

A ``path`` can be specified directly as a string, or it can be specified as an iterable representing the traversal route. The following ``path`` selects an array element from the example data using the syntax ``[<key>:<value>]``, where the key is a label within each element, and the value uniquely identifies an element in the array:
 
 - "/individualInformation/residentialHistory/[id:5f2df182-f6d0-4504-9e18-38a8c7268b77]"
 
Alternatively, the same ``path`` can also be specified as an iterable, and elements within an array can be identified uniquely using a (key, value) 2-tuple:
 
 - ["individualInformation", "residentialHistory", ("id", "5f2df182-f6d0-4504-9e18-38a8c7268b77")]
 
The following code block uses operations to modify the example filing data:

.. code-block:: python

  from finra.filings.form_br import FormBR
  
  f = FormBR()                                   # branch office registration
  (
      f.set_filing_status(f.FilingStatus.DRAFT)  # draft submission
       .set_filing_type(f.FilingType.INITIAL)    # initial filing
       .add_operation(
           f.Op.ADD,                                          # add op
           ["individualInformation", "personalInformation"],  # path
           {"firstName": "John", "lastName": "Smith"}         # value
           )
       .add_operation(
           f.Op.REMOVE,                                       # remove op
           ["individualInformation", "residentialHistory",
            ("id", "5f2df182-f6d0-4504-9e18-38a8c7268b77")]   # path
           )                                                  # no value
  )

Read more about operations in `Partial Updates <https://developer.finra.org/docs#submission_api-api_basics-partial_update>`__ in the official Submission API documentation.

++++++++++++
Update Draft
++++++++++++

:ref:`operations` are particularly useful for submissions in ``DRAFT`` status, which can be updated as many times as needed. To update a draft submission, provide the ``request_id`` as the first argument in the filing's submission method, along with the filing object containing the update operations.

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra import utils
  
  f = FormBR()                                   # branch office registration
  (
      f.set_filing_status(f.FilingStatus.DRAFT)  # draft submission
       .set_filing_type(f.FilingType.INITIAL)    # initial filing
       .add_operation(...)                       # add operations
  )
  
  r = c.form_br_submission(request_id, filing=f)   # submit PATCH update
  
  r.raise_for_status()

The default behavior for an update is to use a PATCH request, which will merge the filing data with the update data, preserving fields that are not included in the update. To replace a data sub-structure instead of merging it, use a PUT request by setting ``put=True`` in the filing's submission method. Read more about the difference between PATCH and PUT requests `here <https://medium.com/@mirzasreza/understanding-the-difference-between-put-and-patch-in-restful-apis-6aa456388fe3>`__.

The ``filing_status`` can also be changed in a PATCH/PUT request without providing any filing data or operations. This can be used to finalize the submission and process it to FINRA by changing the value to :py:attr:`FilingStatus.SUBMITTED <finra.filings.base_filing.BaseFilingOps.FilingStatus.SUBMITTED>`, or to trigger a completeness check on the draft filing by changing the value to :py:attr:`FilingStatus.VALIDATE <finra.filings.base_filing.BaseFilingOps.FilingStatus.VALIDATE>`. 

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra import utils
  
  f = FormBR()                                    # branch office registration
  (
      f.set_filing_status(f.FilingStatus.SUBMITTED) # finalize submission
       .set_filing_type(f.FilingType.INITIAL)       # initial filing
  )                                                 # no data or operations
  
  r = c.form_br_submission(request_id, filing=f)    # submit PATCH update
  
  r.raise_for_status()

++++++++++++
Delete Draft
++++++++++++

Only submissions in ``DRAFT`` status can be deleted. To delete a submission, provide the ``request_id`` as the first argument in the filing's submission method, and set ``delete=True``.

.. code-block:: python

  r = c.form_br_submission(request_id, delete=True)     # delete the draft
  
  r.raise_for_status()

The status of the deletion can be tracked in a subsequent request using the ``request_id``. Once the submission is deleted, the ``result_status`` in the response will be set to ``DELETED``. Deletion is processed in the background, and may take several minutes.

.. code-block:: python

  r = c.form_br_submission(request_id)                  # track the deletion
  
  r.raise_for_status()
  
  result_status = utils.extract_filing_result_status(r) # should be "DELETED"
  
  result_status_description = \
      utils.extract_filing_result_status_desc(r)        # message / errors

.. _validation:

++++++++++++++++++++++
Client-Side Validation
++++++++++++++++++++++

Client-side validation is available through the :py:class:`Client <finra.client.Client>` class. This functionality **DOES NOT** currently support the :py:class:`AsyncClient <finra.async_client.AsyncClient>` class.

Client-side validation uses the :py:class:`Validator <finra.filings.validator.Validator>` class to validate filing data and metadata on the client-side before it is submitted to the API. Client-side validation is completely optional, and is not intended as a replacement for the API's server-side validation process. However, it can be used as a supplemental tool to catch errors prior to submission.

The :py:class:`Validator <finra.filings.validator.Validator>` class validates a filing's JSON object against its JSON Schema, which defines the expected structure and allowed values for the object. It is effectively a proxy for the ``jsonschema.Draft7Validator``, which can validate JSON objects against schemas that follow the `JSON Schema Draft 7 <https://json-schema.org/draft-07>`__ specification. See more information about the ``jsonschema`` validation process `here <https://python-jsonschema.readthedocs.io/en/stable/validate/>`__.

During client-side validation, the schemas are fetched directly from the API and stored in memory, and are accessible from the client's ``schema_registry`` attribute. This significantly reduces validation time because each schema component only needs to be fetched once. To free up resources when all validation is complete, and the schemas are no longer needed, just clear the schema registry.

To perform client-side validation within a client's submission method, set ``validate=True``. If the filing passes, it will then be submitted to the API. If it fails, a ``jsonschema.ValidationError`` will be raised.

.. code-block:: python

  from finra.filings.form_br import FormBR
  
  f = FormBR()
  
  # ...add some filing data or operations
  
  r = c.form_br_submission(
      filing=f,              # submit the filing
      validate=True          # validate client-side before submission
      )
  
  c.schema_registry.clear()  # clear local store, free up memory

The :py:class:`Validator <finra.filings.validator.Validator>` class can also be used outside the client. However, it still requires a client to fetch the schemas. This can be useful to validate the filing data without submitting it to the API. The schema registry can also be managed outside the validator, which enables it to be reused to prevent redundant network operations; many schema parts are shared across filings.

.. code-block:: python

  from finra.filings.form_br import FormBR
  from finra.filings.validator import Validator
  
  schema_registry = {}  # save to reuse schemas across multiple validators
  
  f = FormBR()
  
  # ...add some filing data or operations
  
  obj = f.build()       # filing data/metadata as a JSON object for submission
  
  v = Validator(                                # create validator object
      c,                                        # client
      f.schema_url,                             # top-level schema URL
      schema_registry=schema_registry           # optional, reusable
      )
  
  v.validate(obj)       # client-side validation without submission to the API
  
  schema_registry.clear()  # cleared schemas will need to be re-fetched

