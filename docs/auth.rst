.. highlight:: python

.. _auth:

==================================
Authentication and Client Creation
==================================

The `FINRA API Platform <https://developer.finra.org/docs#getting_started-api_platform_basics-authorization>`__ authentication and authorization scheme is based on OAuth 2.0.  OAuth 2.0 enhances security by replacing the use of long-lasting credentials with limited life span tokens, reducing the potential of exposing an API Credential.

Internally, this client uses `Authlib's HTTPX integration <https://docs.authlib.org/en/stable/oauth2/client/http/httpx.html>`__ to perform requests and implement the OAuth 2.0 standard. This OAuth2 session securely manages the credentials and token path you provide, which are never stored directly on the ``finra-py`` client.

``finra-py`` is designed to handle credentials and authentication tokens securely. However, you are ultimately responsible for securing your credentials, authentication tokens, and any data written to disk. This software is provided "as is."

Read the official `FINRA API Documentation <https://developer.finra.org/docs>`__ to learn more about the API's authentication process. Make sure to take any additional steps necessary to secure your data. This client will save authentication tokens to any file path you provide (assuming you have appropriate file permissions).  It is your responsibility to ensure that this location is secure and appropriate for your environment. Consult your system administrator or security team as appropriate.

**IMPORTANT! Only use one client at a time. The behavior is undefined if you try to use multiple clients with the same credentials at the same time, and may cause problems with the underlying OAuth2 session management.**

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

To create an asynchronous client instead, set ``is_asyncio=True`` in :py:func:`get_client() <finra.auth.get_client>`. See :ref:`async` for more information.

If a valid token exists at the given path it will be used, otherwise a new token will be fetched from the `FINRA Identity Platform <https://developer.finra.org/docs#getting_started-api_platform_basics-authorization>`__ and saved to the provided path.

++++++++++++++
Mock Endpoints
++++++++++++++

Many datasets provide mock endpoints for development and demonstration purposes. To use mock endpoints, a unique ``api_key`` and ``api_secret`` pair must be created through the `FINRA API Console <https://developer.finra.org/docs#getting_started-the_api_console>`__. Because mock endpoints require separate credentials, you will not be able to query production API endpoints when this feature is enabled, including :ref:`notification` and :ref:`submission` endpoints.

**IMPORTANT! Make sure you use mock credentials, and set a different** ``token_path`` **to store your mock API token. Otherwise, you may overwrite your production token, or inadvertently load the wrong token and have your requests rejected by the API server. If this happens, create a new client using** :py:func:`client_from_new_token() <finra.auth.client_from_new_token>` **or delete your tokens manually.**

Set ``mock=True`` when creating a client to use this feature.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="MOCK_API_KEY",
      api_secret="MOCK_API_SECRET",
      token_path="/tmp/finra/mock_token.json",  # different file name
      mock=True
      )

Not all datasets have mock endpoints. If a dataset is queried that does not have a mock endpoint, a :py:class:`finra.exceptions.MockException` will be raised.

.. note::
	Mock endpoints are intended for demonstration purposes, not for comprehensive integration testing, and may lack some functionality documented for production endpoints. Additionally, some mock datasets are sparsely populated, and some endpoints contain no data at all (see :ref:`known_bugs`), so it may be necessary to walk the partitions to locate available records (see the :ref:`large_datasets`). For comprehensive integration testing, use the QA Test Environment.

+++++++++++++++++++
QA Test Environment
+++++++++++++++++++

More extensive testing features are available through the QA Test Environment endpoints, which are only available for firms with paid FINRA API subscriptions (see `FINRA Developer Center <https://developer.finra.org/>`__). To use QA Test Environment endpoints, a unique ``api_key`` and ``api_secret`` pair must be created through the `FINRA API Console <https://developer.finra.org/docs#getting_started-the_api_console>`__.

**IMPORTANT! Make sure you use QA Test Environment credentials, and set a different** ``token_path`` **to store your QA Test Environment API token. Otherwise, you may overwrite your production token, or inadvertently load the wrong token and have your requests rejected by the API server. If this happens, create a new client using** :py:func:`client_from_new_token() <finra.auth.client_from_new_token>` **or delete your tokens manually.**

Set ``test_environment=True`` when creating a client to use this feature.

.. code-block:: python

  from finra.auth import get_client
  
  c = get_client(
      api_key="QA_TEST_API_KEY",
      api_secret="QA_TEST_API_SECRET",
      token_path="/tmp/finra/qa_test_token.json",  # different file name
      test_environment=True
      )

If a dataset is queried that requires QA Test Environment credentials and the client is not configured for it, a :py:class:`finra.exceptions.QATestEnvException` will be raised.

Mock datasets can also be used in the QA Test Environment by setting ``mock=True`` when creating a client. This will not disable :ref:`notification` and :ref:`submission` endpoints within the QA Test Environment.

+++++++++++++++++
Advanced Creation
+++++++++++++++++

Aside from :py:func:`get_client() <finra.auth.get_client>` there are additional routines for creating a client with specific behavior.

----------------------
Load an Existing Token
----------------------

To load an existing token and create a client with it, use :py:func:`client_from_token_file() <finra.auth.client_from_token_file>`. This function does not check whether the token is expired or not, and can result in a ``401 Unauthorized`` response code when making a request if the token is already expired. It will not fetch a new token.

-----------------
Fetch a New Token
-----------------

To force a new token to be fetched and create a client with it, use :py:func:`client_from_new_token() <finra.auth.client_from_new_token>`. This will write the token to the token path, and will overwrite any file that already exists at that path.

----------------------------
Customized Storage Functions
----------------------------

Most users will not need this functionality. However, for use cases involving specialized credential storage, :py:func:`client_from_storage_functions() <finra.auth.client_from_storage_functions>` allows custom callback functions to read and write the token files. This is useful when credentials are managed outside the local filesystem, for example in cloud-hosted or enterprise environments. You are responsible for ensuring these callbacks function securely and behave as expected.

------------
Build Client
------------

The :py:func:`build_client <finra.auth.build_client>` function provides the most fine-grained control over client creation, but requires additional setup to configure the client correctly. All of the above client creation functions ultimately call :py:func:`build_client <finra.auth.build_client>`.

Keyword arguments for this function can be passed through any of the above client creation functions, including custom constructors that return an instance of :py:class:`Client <finra.client.Client>` or a subclass thereof. Calling this function directly requires a correctly configured instance of :py:class:`TokenManager <finra.token_manager.TokenManager>` or a subclass.

Similarly, :py:func:`build_async_client <finra.auth.build_async_client>` can be used to create an :py:class:`AsyncClient <finra.async_client.AsyncClient>` with ``asyncio`` support.

