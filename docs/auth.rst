.. highlight:: python

.. _auth:

==================================
Authentication and Client Creation
==================================

Before using ``finra-py``, you'll need to create a developer account with FINRA and provision a set of credentials, see :ref:`api_access`.

The `FINRA API Platform <https://developer.finra.org/docs#getting_started-api_platform_basics-authorization>`__ uses OAuth 2.0 for authentication and authorization. OAuth 2.0 uses short-lived access tokens instead of the resource owner’s long-term credentials, reducing the risk of credential exposure.

Internally, ``finra-py`` uses `Authlib's HTTPX integration <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html>`__ to perform requests and implement the OAuth 2.0 standard. This OAuth2 session manages the credentials and ``token_path`` you provide, which are never stored directly on the ``finra-py`` client.

You are ultimately responsible for securing your credentials, authentication tokens, and any data written to disk. ``finra-py`` will save authentication tokens to any file path you provide (assuming you have the necessary file permissions). It is your responsibility to ensure that this location is secure and appropriate for your environment.

To manage credentials outside your local filesystem, see :ref:`advanced_creation`. For broader security considerations, see the `Security Policy <https://github.com/hawkberry/finra-py/blob/main/SECURITY.md>`__.

See the :py:mod:`auth <finra.auth>` module for complete reference documentation.

++++++++++++
Get a Client
++++++++++++

The easiest way to create a configured instance of :py:class:`Client <finra.client.Client>` is to use the :py:func:`get_client() <finra.auth.get_client>` function.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="API_KEY",
      api_secret="API_SECRET",
      token_path="/tmp/finra/token.json"
      )

If a valid token exists at the given path it will be used, otherwise a new token will be fetched from the `FINRA Identity Platform <https://developer.finra.org/docs#getting_started-api_platform_basics-authorization>`__ and saved to the provided path.

To create an asynchronous client instead, use :py:func:`await get_async_client() <finra.auth.get_async_client>`, which performs the initial token fetch asynchronously and accepts both synchronous and asynchronous callbacks when customizing the ``token_read_func`` and ``token_write_func``.

.. code-block:: python

  from finra.auth import get_async_client
  
  c = await get_async_client(
      api_key="API_KEY",
      api_secret="API_SECRET",
      token_path="/tmp/finra/token.json"        # token file path
      )

For more information about basic ``asyncio`` usage, see :ref:`async`.

++++++++++++++
Mock Endpoints
++++++++++++++

Many :ref:`query` datasets provide mock endpoints for development and demonstration purposes. To use mock endpoints, a unique ``api_key`` and ``api_secret`` pair must be created through the `FINRA API Console <https://developer.finra.org/docs#getting_started-the_api_console>`__. Because mock endpoints require separate credentials, you will not be able to access production API endpoints when this feature is enabled, including :ref:`notification` and :ref:`submission` endpoints.

**IMPORTANT! Make sure you use mock credentials, and set a different** ``token_path`` **to store your mock API token. Otherwise, you may overwrite your production token, or inadvertently load the wrong token and have your requests rejected by the API server. If this happens, create a new client using** :py:func:`client_from_new_token() <finra.auth.client_from_new_token>` **or delete your tokens manually.**

Set ``mock=True`` when creating a client to use mock endpoints.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="MOCK_API_KEY",
      api_secret="MOCK_API_SECRET",
      token_path="/tmp/finra/mock_token.json",  # different file path
      mock=True
      )

Not all datasets have mock endpoints. If a dataset is queried that does not have a mock endpoint, a :py:class:`finra.exceptions.MockException` will be raised.

.. note::
	Mock endpoints are intended for demonstration purposes, not for comprehensive integration testing, and may lack some functionality documented for production endpoints. Additionally, some mock datasets are sparsely populated, and some datasets contain no data at all (see :ref:`known_bugs`), so it may be necessary to walk the partitions to locate available records (see :ref:`large_datasets`). For comprehensive integration testing, use the QA Test Environment.

+++++++++++++++++++
QA Test Environment
+++++++++++++++++++

More extensive testing features are available through the QA Test Environment, which is only available for firms with paid FINRA API subscriptions (see `FINRA Developer Center <https://developer.finra.org/>`__). To use the QA Test Environment, a unique ``api_key`` and ``api_secret`` pair must be created through the `FINRA API Console <https://developer.finra.org/docs#getting_started-the_api_console>`__.

**IMPORTANT! Make sure you use QA Test Environment credentials, and set a different** ``token_path`` **to store your QA Test Environment API token. Otherwise, you may overwrite your production token, or inadvertently load the wrong token and have your requests rejected by the API server. If this happens, create a new client using** :py:func:`client_from_new_token() <finra.auth.client_from_new_token>` **or delete your tokens manually.**

Set ``test_environment=True`` when creating a client to use the QA Test Environment.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="QA_TEST_API_KEY",
      api_secret="QA_TEST_API_SECRET",
      token_path="/tmp/finra/qa_test_token.json",  # different file path
      test_environment=True
      )

If a dataset is queried that requires QA Test Environment credentials and the client is not configured for it, a :py:class:`finra.exceptions.QATestEnvException` will be raised.

Mock datasets can also be accessed in the QA Test Environment by setting ``mock=True`` when creating a client. This setting will disable non-mock :ref:`query` endpoints while using the client, but it will not disable :ref:`notification` and :ref:`submission` endpoints.

.. _advanced_creation:

+++++++++++++++++
Advanced Creation
+++++++++++++++++

For most users, :py:func:`get_client() <finra.auth.get_client>` and :py:func:`await get_async_client() <finra.auth.get_async_client>` have all the necessary functionality. However, for users that need additional control over the authentication and client creation process, the library exposes several sub-routines, each with different behaviors.

----------------------
Load an Existing Token
----------------------

To load an existing token from a file and create a client with it, use :py:func:`client_from_token_file() <finra.auth.client_from_token_file>`. This function does not check whether the token has expired or not, and can result in a ``401 Unauthorized`` response code when making an API request if the token has already expired. If the file does not exist, it will raise ``FileNotFoundError``. It will not fetch a new token.

-----------------
Fetch a New Token
-----------------

To force a new token to be fetched from the `FINRA Identity Platform <https://developer.finra.org/docs#getting_started-api_platform_basics-authorization>`__ and create a client with it, use :py:func:`client_from_new_token() <finra.auth.client_from_new_token>`. By default, the token will be written to the given ``token_path``, and will overwrite any file that already exists there. The token write behavior can be customized by setting a synchronous callback as the ``token_write_func``, however it is your responsibility to ensure your callback function operates securely and behaves as expected.

To create an :py:class:`AsyncClient <finra.async_client.AsyncClient>`, use :py:func:`await async_client_from_new_token() <finra.auth.async_client_from_new_token>`, which performs the initial token fetch asynchronously and accepts both synchronous and asynchronous callbacks for the ``token_write_func``. An :py:class:`AsyncClient <finra.async_client.AsyncClient>` can also be created by setting ``is_asyncio=True`` in :py:func:`client_from_new_token() <finra.auth.client_from_new_token>`, however this uses the synchronous client to perform the initial token fetch, which will block other coroutines, and it only accepts synchronous callbacks.

----------------------------
Customized Storage Functions
----------------------------

For use cases involving specialized credential storage, :py:func:`client_from_storage_functions() <finra.auth.client_from_storage_functions>` allows custom callback functions to read and write tokens. This is useful when credentials are managed outside the local filesystem, for example in cloud-hosted or enterprise environments. It is your responsibility to ensure your callback functions operate securely and behave as expected.

This function calls the ``token_read_func`` callback to fetch an existing token from the storage location. It will not automatically fetch a new token if the token does not exist.

This function calls the ``token_write_func`` callback to write a new token to the storage location, for example when calling :py:meth:`Client.refresh_token() <finra.client.Client.refresh_token>` (see :ref:`token_expiration`).

To create an :py:class:`AsyncClient <finra.async_client.AsyncClient>`, use :py:func:`await async_client_from_storage_functions() <finra.auth.async_client_from_storage_functions>`, which accepts both synchronous and asynchronous callbacks for the ``token_read_func`` and ``token_write_func``. An :py:class:`AsyncClient <finra.async_client.AsyncClient>` can also be created by setting ``is_asyncio=True`` in :py:func:`client_from_storage_functions() <finra.auth.client_from_storage_functions>`, however this only accepts synchronous callbacks.

------------
Build Client
------------

The following creation functions are included for completeness, but unless you need to subclass :py:class:`TokenManager <finra.token_manager.TokenManager>`, you should not need them.

The :py:func:`build_client() <finra.auth.build_client>` and :py:func:`build_async_client() <finra.auth.build_async_client>` functions provide the most fine-grained control over client creation, but they require additional setup to configure correctly. All of the other client creation functions ultimately call one of these to instantiate the client.

Keyword arguments for these functions can be passed through any of the other client creation functions, including custom constructors that return an instance of :py:class:`Client <finra.client.Client>` or :py:class:`AsyncClient <finra.async_client.AsyncClient>`. Calling these functions directly requires a correctly configured instance of :py:class:`TokenManager <finra.token_manager.TokenManager>`.

