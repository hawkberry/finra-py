============================================
``finra-py``: An Unofficial FINRA API Client
============================================

.. image:: https://github.com/hawkberry/finra-py/actions/workflows/run-tests.yml/badge.svg
  :target: https://github.com/hawkberry/finra-py/actions/workflows/run-tests.yml

.. image:: https://codecov.io/github/hawkberry/finra-py/coverage.svg?branch=main
  :target: https://codecov.io/github/hawkberry/finra-py?branch=main

.. image:: https://readthedocs.org/projects/finra-py/badge/?version=latest
  :target: https://finra.hawkberry.com/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/finra-py.svg
  :target: https://badge.fury.io/py/finra-py

.. image:: https://img.shields.io/pypi/pyversions/finra-py.svg
   :target: https://pypi.org/project/finra-py/

.. image:: https://img.shields.io/pypi/l/finra-py.svg
   :target: https://github.com/hawkberry/finra-py/blob/main/LICENSE

.. image:: https://img.shields.io/badge/Support-blue
   :target: https://support.hawkberry.com/

+++++++++++++++++++++
What is ``finra-py``?
+++++++++++++++++++++

``finra-py`` is an unofficial, open-source Python client library for the `FINRA API Platform <https://developer.finra.org/products>`__. It is designed to be as thin and unopinionated as possible, offering an elegant programmatic interface to every endpoint and dataset.

Notable functionality includes:
 
 - Authentication and client creation
 - Equity, Fixed Income, FINRA, Firm, Registration and TRACE Report Card datasets via the `Query API <https://finra.hawkberry.com/en/latest/query-api.html>`__
 - Notification datasets via the `Notification API <https://finra.hawkberry.com/en/latest/notification-api.html>`__
 - Submission of regulatory filings and other data to FINRA via the `Submission API <https://finra.hawkberry.com/en/latest/submission-api.html>`__
 - Support for the Mock API
 - Support for the QA Test Environment API
 - Support for all credential types
 - Support for asynchronous requests (server-side)
 - Support for ``asyncio`` (client-side)
 
Python requirement: **3.11 or later**

++++++++++++++++++++++++++
How do I use ``finra-py``?
++++++++++++++++++++++++++

You can find a full description of the ``finra-py`` library's functionality in the `documentation <https://finra.hawkberry.com/en/latest/>`__.

For detailed instructions on how to get started with ``finra-py``, see `Getting Started <https://finra.hawkberry.com/en/latest/getting-started.html>`__.

++++++++++++++++++++++++++++++
Why should I use ``finra-py``?
++++++++++++++++++++++++++++++

``finra-py`` is designed to provide a few important pieces of functionality:

1. **Safe Authentication**: The FINRA API Platform authentication and authorization scheme is based on OAuth 2.0. However, too many people online end up rolling their own implementation of the OAuth 2.0 authentication flow, which is both unnecessarily complex and dangerous. ``finra-py`` handles the token fetch and management for you.

2. **Minimal API Wrapping**: Unlike some other API wrappers, which build in lots of opinionated logic and validation, ``finra-py`` takes raw values and returns raw responses, allowing you to interpret the complex API responses as you see fit. Anything you can do with raw HTTP requests you can do with ``finra-py``, only more easily.

3. **All API Endpoints**: The ``finra-py`` library is designed to provide thorough coverage of the FINRA API Platform. With this goal in mind, ``finra-py`` implements full functionality for every dataset and regulatory filing supported by the FINRA API and described in the documentation.

+++++++++++
Limitations
+++++++++++

``finra-py`` strives to provide comprehensive coverage of all documented datasets for the FINRA API. However, there are some datasets and services available through FINRA that may not be available through the FINRA API. See `FINRA Data <https://www.finra.org/finra-data>`__ for information about all available FINRA datasets.

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

Need help implementing the FINRA API?

As the author and maintainer of ``finra-py``, I provide consulting on FINRA API integrations, Web EFT migrations, compliance-related workflows, and market data systems.

See the `consulting page <https://finra.hawkberry.com/en/latest/consulting.html>`__ for more information.

+++++++++++++
Project Links
+++++++++++++

* `Documentation <https://finra.hawkberry.com/en/latest/>`__
* `Repository <https://github.com/hawkberry/finra-py>`__
* `PyPI <https://pypi.org/project/finra-py/>`__
* `Changelog <https://github.com/hawkberry/finra-py/blob/main/CHANGELOG.md>`__
* `Consulting <https://finra.hawkberry.com/en/latest/consulting.html>`__
* `Support <https://support.hawkberry.com/>`__
* `Issues <https://github.com/hawkberry/finra-py/issues>`__

**Disclaimer:** ``finra-py`` *is an unofficial, open-source client library for the FINRA API. It is not endorsed by, affiliated with, or sponsored by FINRA or any associated organization. Users are responsible for reviewing and complying with the terms of service and usage requirements of the underlying FINRA API. This software is provided under the terms of the* `LICENSE <https://github.com/hawkberry/finra-py/blob/main/LICENSE>`__ *without warranty of any kind.*

