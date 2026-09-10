============================================
``finra-py``: An Unofficial FINRA API Client
============================================

.. image:: https://github.com/hawkberry/finra-py/actions/workflows/run-tests.yml/badge.svg
  :target: https://github.com/hawkberry/finra-py/actions/workflows/run-tests.yml

.. image:: https://codecov.io/gh/hawkberry/finra-py/branch/main/graph/badge.svg
  :target: https://app.codecov.io/gh/hawkberry/finra-py

.. image:: https://app.readthedocs.org/projects/finra-py/badge/?version=latest
  :target: https://finra.hawkberry.com/en/latest/

.. image:: https://badge.fury.io/py/finra-py.svg
  :target: https://badge.fury.io/py/finra-py

.. image:: https://img.shields.io/pypi/pyversions/finra-py.svg
   :target: https://pypi.org/project/finra-py/

.. image:: https://img.shields.io/pypi/l/finra-py.svg
   :target: https://github.com/hawkberry/finra-py/blob/main/LICENSE

.. image:: https://img.shields.io/badge/open%20source-support-blue
   :target: https://support.hawkberry.com/

+++++++++++++++++++++
What is ``finra-py``?
+++++++++++++++++++++

``finra-py`` is an unofficial, open-source Python client library for the `FINRA API Platform <https://developer.finra.org/products>`__. It provides a lightweight, unopinionated Python interface to the FINRA API while preserving direct access to the API's responses and full functionality for every supported API endpoint and dataset.

The core features include:

- OAuth 2.0 authentication, client creation, token management, and custom token storage
- Equity, Fixed Income, FINRA, Firm, Registration and TRACE Report Card datasets via the `Query API <https://finra.hawkberry.com/en/latest/query-api.html>`__
- FINRA notification event datasets via the `Notification API <https://finra.hawkberry.com/en/latest/notification-api.html>`__
- Submission of regulatory filings and other data to FINRA, including creation, validation, submission, updates, and retrieval for Form U4, Form U5, Form BR, Create Individual, Non-Registered Fingerprint, and other supported workflows via the `Submission API <https://finra.hawkberry.com/en/latest/submission-api.html>`__
- Support for all credential types
- Support for Mock datasets
- Support for the QA Test Environment API
- Support for asynchronous requests (server-side)
- Support for ``asyncio`` (client-side)

+++++++++++++++++++++++
Installing ``finra-py``
+++++++++++++++++++++++

``finra-py`` requires **Python 3.11 or later**.

Install the package using ``pip``:

.. code-block:: shell

  python -m pip install finra-py

Import the package in Python:

.. code-block:: python

  import finra

You can find a full description of the ``finra-py`` library's functionality in the `documentation <https://finra.hawkberry.com/en/latest/>`__.

For detailed instructions on how to get started with ``finra-py``, see `Getting Started <https://finra.hawkberry.com/en/latest/getting-started.html>`__.

+++++++++++++++++++++
Why use ``finra-py``?
+++++++++++++++++++++

``finra-py`` is FINRA-specific on the way in, and standard HTTPX on the way out.

1. **OAuth 2.0 Authentication**: The FINRA API uses OAuth 2.0 for authentication and authorization. Implementing the OAuth 2.0 authentication flow yourself can introduce unnecessary complexity and security risks. ``finra-py`` handles token acquisition and lifecycle management for you, with customizable token storage for applications that need to manage credentials in their own storage systems.

2. **Direct API Access**: ``finra-py`` keeps the client layer deliberately thin. It maps requests to the FINRA API and returns the raw ``httpx.Response`` objects directly to you, without imposing a custom response or data model. You get the convenience of a dedicated FINRA client with all of the API's features, without giving up the control available through direct HTTP requests.

3. **All API Endpoints**: The ``finra-py`` library is designed to provide thorough coverage of the FINRA API Platform. With this goal in mind, ``finra-py`` implements full functionality for every dataset and regulatory filing supported by the FINRA API and described in the documentation. It also provides comprehensive test coverage across Windows, macOS, and Linux.

+++++++++++
Limitations
+++++++++++

Even though ``finra-py`` strives to provide coverage of all documented datasets for the FINRA API, there are some datasets and services available through FINRA that may not be available through their API. See `FINRA Data <https://www.finra.org/finra-data>`__ for information about all available FINRA datasets.

- ``finra-py`` does not currently support FINRA's fileX API

++++++++++++++++++++
Help and Development
++++++++++++++++++++

For troubleshooting guidance and answers to common questions, see the
`Getting Help <https://finra.hawkberry.com/en/latest/help.html>`__ page.

Submit bug reports on the ``finra-py`` `Issues Page <https://github.com/hawkberry/finra-py/issues>`__ on GitHub.

If you need a dataset or feature that is not currently supported by the client, please file a `Feature Request <https://github.com/hawkberry/finra-py/issues>`__. Pull requests are not currently accepted.

++++++++++++++++++++
FINRA API Consulting
++++++++++++++++++++

Need help with a custom integration?

As the author and maintainer of ``finra-py``, I provide consulting on FINRA API integrations, Web EFT migrations, compliance-related workflows, and market data systems.

See the `consulting page <https://finra-py.readthedocs.io/en/latest/consulting.html>`__ for more information.

+++++++++++++
Project Links
+++++++++++++

* `Documentation <https://finra.hawkberry.com/en/latest/>`__
* `Repository <https://github.com/hawkberry/finra-py>`__
* `PyPI <https://pypi.org/project/finra-py/>`__
* `Issues <https://github.com/hawkberry/finra-py/issues>`__
* `Changelog <https://github.com/hawkberry/finra-py/blob/main/CHANGELOG.md>`__
* `ADRs <https://finra.hawkberry.com/en/latest/adr.html>`__
* `Consulting <https://finra.hawkberry.com/en/latest/consulting.html>`__
* `Support <https://support.hawkberry.com/>`__

**Disclaimer:** ``finra-py`` *is an unofficial, open-source client library for the FINRA API Platform. It is not endorsed by, affiliated with, or sponsored by FINRA or any associated organization.* ``finra-py`` *does not provide financial advice, investment recommendations, trading strategies, or financial analysis. Users are responsible for reviewing and complying with the terms of service and usage requirements of the underlying FINRA API. This software is provided under the terms of the* `LICENSE <https://github.com/hawkberry/finra-py/blob/main/LICENSE>`__ *without warranty of any kind.*

