.. highlight:: python

.. _getting_started:

===============
Getting Started
===============

Welcome to ``finra-py``, an unofficial, open-source Python client library for the FINRA API Platform.

This page describes how to install and configure your first ``finra-py`` client, and it provides some basic examples you can build on for your application.

``finra-py`` is designed for software developers, researchers, media companies, the general public, and FINRA member firms and organizations. To support this diverse set of user groups, the client implements all documented endpoints for the :ref:`query`, the :ref:`notification`, and the :ref:`submission`.

You can read the official FINRA API documentation `here <https://developer.finra.org/docs>`__.

``finra-py`` is open source and may be used, modified, and distributed according to the terms of the `LICENSE <https://github.com/hawkberry/finra-py/blob/main/LICENSE>`__. Organizations are welcome to use the library in their own applications and workflows.

For assistance implementing the FINRA API, migrating from Web EFT, or building reliable applications using FINRA data, see `FINRA API Consulting <https://finra.hawkberry.com/en/latest/consulting.html>`__.

++++++++++++++++
FINRA API Access
++++++++++++++++

Before using ``finra-py``, you'll need to create a developer account with FINRA and provision a set of credentials. There are different types of credentials based on what type of user you are: Individual, Firm, Organization, etc. Individual user accounts are free, and all other account types are available with a subscription. See the `FINRA Developer Center <https://developer.finra.org/>`__ and `FINRA API Console <https://developer.finra.org/docs#getting_started-the_api_console>`__ in the official documentation for detailed instructions on how to gain access for your user type. You can create an account via the `FINRA Gateway <https://gateway.finra.org/>`__.

You must have the correct credentials for datasets, or you will receive a ``401 Unauthorized`` or ``403 Forbidden`` response from the API. The required credentials for each dataset are detailed in the documentation for its query method on the client, as well as in the server's documentation.

To ensure the integrity of the API platform, please use this client responsibly and adhere to usage limits. To avoid being throttled or blocked, make sure you familiarize yourself with the API's `Platform Usage Limits <https://developer.finra.org/docs#getting_started-api_platform_basics-platform_usage_limits>`__, as well as FINRA's `Terms of Service <https://developer.finra.org/docs#getting_started-terms_of_service>`__.

+++++++++++++++++++++++
Installing ``finra-py``
+++++++++++++++++++++++

``finra-py`` requires Python 3.11 or later.

Install the package using ``pip``:

.. code-block:: shell

  python -m pip install finra-py

Import the package in Python:

.. code-block:: python

  import finra

+++++++++++
Basic Usage
+++++++++++

The easiest way to create a client is with the :py:func:`get_client() <finra.auth.get_client>` function. Replace the values below with your ``api_key`` and ``api_secret``, and choose an appropriate, secure ``token_path`` to store your API token. It is your responsibility to ensure your credentials and tokens are stored and accessed securely.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="API_KEY",                  # replace with your API key
      api_secret="API_SECRET",            # replace with your API secret
      token_path="/tmp/finra/token.json"  # replace with your secure location
      )

For more information about creating clients, see :ref:`auth`. For details on basic client functionality, see :ref:`client`. For a thorough description of options for requesting datasets, see :ref:`query`.

-------------------
Basic Query Pattern
-------------------

Internally, ``finra-py`` uses `Authlib's HTTPX integration <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html>`__ to implement the OAuth 2.0 standard and perform requests securely. Every API request returns an ``httpx.Response`` object, which is passed directly to the caller. It is up to the caller to handle the response object. This design choice gives the caller the most control possible over their requests.

This is the most basic query pattern to fetch a dataset, and handle the ``httpx.Response`` object.

.. code-block:: python

  r = c.get_consolidated_short_interest()  # returns httpx.Response object
  
  r.raise_for_status()  # raise exception if request was unsuccessful
  
  data = r.json()       # extract json content from response object

Calling ``r.raise_for_status()`` raises ``httpx.HTTPStatusError`` if a status code is received indicating the request was unsuccessful (``300`` or higher). If the status code is less than ``300``, then the request was successful and the line does nothing. The status code can be accessed directly via the response object's attribute ``r.status_code``.

For :ref:`query` datasets, the response content type can be set to either ``application/json`` (the client's default) or ``text/plain``. If the response content type is ``application/json``, the data can be extracted using the ``httpx.Response.json()`` method. For :ref:`notification` and :ref:`submission` datasets, the response content type is always ``application/json``. For more details see :ref:`content_types`.

See more information about handling HTTPX response content `here <https://www.python-httpx.org/quickstart/#response-content>`__.

---------------
Specific Fields
---------------

For most datasets this client uses enums from Python's `enum <https://docs.python.org/3/library/enum.html>`__ module to simplify access to specific dataset fields. With few exceptions, each dataset has a unique enum containing all of its available field names. This enum is typically documented on the client just above the dataset's query method.

The example below requests a subset of fields from the :py:class:`ConsolidatedShortInterest <finra.base_client.BaseClient.ConsolidatedShortInterest>` dataset: the symbol, the settlement date, and the current short position. To specify fields for this dataset, use the :py:class:`ConsolidatedShortInterest <finra.base_client.BaseClient.ConsolidatedShortInterest>` enum.

.. code-block:: python

  e = c.ConsolidatedShortInterest  # enum for this dataset
  
  r = c.get_consolidated_short_interest(
      fields=[e.SYMBOL, e.SETTLEMENT_DATE, e.CURRENT_SHORT_POSITION]
      )
  
  r.raise_for_status()
  
  data = r.json()

---------------
Specific Values
---------------

This example shows how to request records for a specific set of symbols. In this case you can use a :py:class:`Filter <finra.filters.Filter>` object to create a domain filter, which allows you to specify one or more values for a field that each record must match.

.. code-block:: python

  from finra.filters import Filter
  
  symbols = ["AAPL", "MSFT"]  # only return records for these values
  
  e = c.ConsolidatedShortInterest
  
  r = c.get_consolidated_short_interest(
      filters=Filter(e).add_domain(e.SYMBOL, symbols)  # filter on values
      )
  
  r.raise_for_status()
  
  data = r.json()

Due to server-side constraints, this code will only fetch the first 1,000 records matching the filter conditions. If you need to query a larger number of records, or require a more advanced query pattern, see the :ref:`large_datasets`.

----------------
Close the Client
----------------

When you're done with the client, connections should be closed properly to free up resources. The recommended way to use a :py:class:`Client <finra.client.Client>` is as a context manager.

.. code-block:: python

  with get_client(...) as c:  # context management
      ...

Alternatively, you can explicitly close the connection pool by calling :py:meth:`Client.close() <finra.client.Client.close>`.

.. code-block:: python

  c = get_client(...)
  try:
      ...
  finally:
      c.close()               # close manually

For the asynchronous client use :py:meth:`await AsyncClient.close() <finra.async_client.AsyncClient.close>`. See :ref:`async`.

.. code-block:: python

  async with get_client(..., is_asyncio=True) as c:  # async context
      ...

.. code-block:: python

  c = get_client(..., is_asyncio=True)
  try:
      ...
  finally:
      await c.close()         # close manually

Any requests made after closing a client will raise a ``RuntimeError``. To make additional requests, create a new client.

++++++++++++
Getting Help
++++++++++++

For information on how to report a bug see :ref:`debug`.

If you are looking for additional support, please see `FINRA API Consulting <https://finra.hawkberry.com/en/latest/consulting.html>`__.

