.. highlight:: python

.. _client:

===========
HTTP Client
===========

For details on client creation and authentication see :ref:`auth`.

See :py:mod:`finra.base_client` module for complete reference documentation.

+++++++++++++++++++
Calling Conventions
+++++++++++++++++++

Each dataset has its own method for requesting data. Many of these methods have the same signature, however there are some datasets that require different arguments, especially those in the Firm and Registration groups.

The API recognizes an extensive number of special values, for example the field names for each dataset. Rather than requiring users to manually enter these values, this library represents them using enums from Python's `enum <https://docs.python.org/3/library/enum.html>`__ module. The reason for this design choice is that the API rejects requests with unrecognized values, which would be a common source of error and frustration for users. Using enums to manage these values avoids these common errors and simplifies access to the datasets. A dataset's enum is typically displayed in the reference documentation just above its associated query method. With a few exceptions, each dataset has its own enum containing all of its available field names.

If a value is passed other than a member of the expected enum, a ``TypeError`` will be raised. This functionality can be disabled on the client by setting ``require_enums=False`` during creation, or via its :py:meth:`set_require_enums() <finra.enum_converter.EnumConverter.set_require_enums>` method. Several other classes in this library have the same functionality, including the :py:class:`Filter <finra.filters.Filter>` class (see :ref:`filters`), and the filing classes used by :ref:`submission` methods. In general, disabling this constraint should not be necessary, however it may be useful if you notice the API accepts a value that is not yet supported by this library. If you do find a value that is not supported here, please open an issue on the ``finra-py`` `Issues Page <https://github.com/hawkberry/finra-py/issues>`__ on GitHub and describe your findings.

Additionally, all :ref:`query` datasets support multiple :ref:`endpoints` for accessing information about them. When querying the :py:attr:`Endpoint.DATA <finra.base_client.BaseClient.Endpoint.DATA>` endpoint, required parameters can be passed as positional or keyword arguments. Optional parameters are always passed as keyword arguments. Any deviation from this convention is described in the reference documentation.

This client also supports the API's server-side asynchronous request flow. This is different than the client-side ``asyncio`` support detailed below. For information about asynchronous requests for Query API datasets see :ref:`here <async_requests>`, or for Submission API filings see :ref:`here <request_flow>`.

.. _async:

+++++++++++++++
Asyncio Support
+++++++++++++++

In addition to the standard synchronous client, this library provides an asynchronous client for improved throughput with I/O-bound applications. To learn about asynchronous I/O, see Python's `asyncio <https://docs.python.org/3/library/asyncio.html#module-asyncio>`__ module. To create a configured instance of :py:class:`AsyncClient <finra.async_client.AsyncClient>`, set ``is_asyncio=True`` in :py:func:`get_client() <finra.auth.get_client>`.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="API_KEY",
      api_secret="API_SECRET",
      token_path="/tmp/finra/token.json",
      is_asyncio=True
      )

The :py:class:`AsyncClient <finra.async_client.AsyncClient>` uses an asynchronous OAuth2 session to make requests, and returns awaitable coroutines. A coroutine must be awaited to execute an API request and receive an ``httpx.Response`` object. While waiting for the API server to respond, other coroutines and tasks can be executed concurrently and will not be blocked.

.. code-block:: python

  r = await c.get_consolidated_short_interest()  # await async coroutine
  
  r.raise_for_status()  # raise exception if request was unsuccessful
  
  data = r.json()  # extract data from response object

++++++++++++++++++
Session Management
++++++++++++++++++

There are several settings for managing how the client interacts with the API server.

---------------
Request Timeout
---------------

To set the session timeout for all HTTP requests made by the client, use the :py:meth:`Client.set_timeout() <finra.base_client.BaseClient.set_timeout>` method. To get the current session timeout, call :py:meth:`Client.get_timeout() <finra.base_client.BaseClient.get_timeout>`. The default value is 30 seconds.

.. code-block:: python

  c.set_timeout(60)  # now all requests will timeout after 60 seconds

.. _token_expiration:

----------------
Token Expiration
----------------

Access tokens have a limited lifetime. If an API request returns a ``401 Unauthorized`` response and the dataset credentials are valid, the stored access token has likely expired. 

To get a new token for an existing client call the :py:meth:`Client.refresh_token <finra.client.Client.refresh_token>` method (awaitable for asynchronous client). This will fetch a new token from the `FINRA Identity Platform <https://developer.finra.org/docs#getting_started-api_platform_basics-authorization>`__ and store it at the ``token_path``, or using the ``token_write_func`` if it was set during client creation.

The client offers several read-only attributes that can be used to anticipate token expiration:
 
 - :py:attr:`token_expires_in <finra.base_client.BaseClient.token_expires_in>` : the number of seconds until expiration
 - :py:attr:`token_expires_at <finra.base_client.BaseClient.token_expires_at>` : the expiration timestamp in UTC
 - :py:attr:`token_age <finra.base_client.BaseClient.token_age>` : the number of seconds since token creation
 
These attributes describe a token's lifecycle, and can indicate when to proactively fetch a new token before it expires. Additionally, the :py:func:`get_client <finra.auth.get_client>` function has a ``min_expires_in`` keyword that can be used to set minimum time to expiration (in seconds) when creating a client from a stored token, and will force a new token to be fetched if the stored token expires sooner.

.. _data_version:

+++++++++++++++
Data Versioning
+++++++++++++++

Some datasets support multiple versions. This is usually the case only when a dataset's structure or its access patterns have been upgraded, with the older version(s) typically having a limited support window and a retirement date.

To request a specific data version use the ``version`` keyword in a dataset's query method. If the value is set to ``None``, the data version of the response will be the server's default for that dataset. Even though most datasets only support a single data version, the ``version`` keyword is included as a calling convention for all datasets to support potential future updates.

See `Data Versioning <https://developer.finra.org/docs#query_api-api_basics-data_versioning>`__ in the official API documentation, and see the documentation for a specific dataset for information about the versioning options it supports.

