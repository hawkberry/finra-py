.. _finra_api_changelog:

===================
FINRA API Changelog
===================


**THIS PAGE AND RSS FEED ARE CURRENTLY UNDER DEVELOPMENT AND SUBJECT TO CHANGE**


This is an unofficial changelog for the `FINRA API <https://developer.finra.org/docs>`__.

This page tracks various kinds of changes to the API and its documentation. The purpose of the page is to help developers track API drift and better understand and implement FINRA API integrations.

See the :ref:`changelog` below for a complete record of ``HIGH`` and ``MEDIUM`` priority changes, sorted in reverse chronological order. This is the changelog that enables ``finra-py`` to stay up-to-date.

To receive a weekly digest of ``HIGH`` priority changes, and occasional ``finra-py`` related articles, subscribe by email:

* Weekly Digest (coming soon)

To receive changes of all priority levels, including ``LOW`` priority messages, subscribe to the RSS feed and filter categories based on your own requirements:

* `RSS Feed <https://raw.githubusercontent.com/hawkberry/finra-py/main/finra-changelog.rss>`__

Changes are categorized by the ``kind`` of change and the documentation ``section_type``, with each combination assigned a fixed message ``priority``. These fields are included as RSS category tags to support category-based filtering, and also as ``label=value`` pairs in the description so feeds that do not support category filtering can still filter messages based on the description text.

Message ``priority``:

- ``HIGH``
- ``MEDIUM``
- ``LOW``

Change ``kind``:

- ``dataset_status_changed``
- ``dataset_version_status_changed``
- ``event_type_status_changed``
- ``event_type_version_status_changed``
- ``submission_type_status_changed``
- ``submission_type_version_status_changed``
- ``section_added``
- ``section_removed``
- ``section_title_changed``
- ``credential_types_changed``
- ``link_added``
- ``link_removed``
- ``link_url_changed``
- ``link_text_changed``
- ``table_added``
- ``table_removed``
- ``table_title_changed``
- ``table_headers_changed``
- ``table_column_added``
- ``table_column_removed``
- ``table_row_added``
- ``table_row_removed``
- ``table_value_changed``
- ``text_changed``

Documentation ``section_type``:

- ``top``
- ``major``
- ``dataset_group``
- ``dataset``
- ``event_type``
- ``submission_type``
- ``non_dataset``
- ``dataset_subsection``
- ``non_dataset_subsection``
- ``unknown``

.. _changelog:

+++++++++
Changelog
+++++++++

.. BEGIN_FINRA_DOCUMENTATION_CHANGES

.. _finra_docs_2026_09:

September 2026
--------------

September 26, 2026
~~~~~~~~~~~~~~~~~~

* **HIGH — Section added**

  - Path: Query API > TRACE Report Cards > TRACE Foreign Sovereign Debt Summary
* **HIGH — Section added**

  - Path: Query API > TRACE Report Cards > TRACE Treasuries Execution Time Difference Summary
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Detail > Dataset Details
  - Table: Available parameters
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Summary > Dataset Details
  - Table: Available Parameters
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Detail > Dataset Details
  - Table: Available parameters
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Summary > Dataset Details
  - Table: Available parameters
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Detail > Dataset Details
  - Table: Available parameters
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Summary > Dataset Details
  - Table: (no title)
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Detail > Dataset Details
  - Table: Available parameters
  - Column: Permitted Values
* **HIGH — Table column added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Summary > Dataset Details
  - Table: Available Parameters
  - Column: Permitted Values
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Detail > Dataset Details
  - Table: Available parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Summary > Dataset Details
  - Table: Available Parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Detail > Dataset Details
  - Table: Available parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All, P1, S1', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Summary > Dataset Details
  - Table: Available parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All, P1, S1', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Detail > Dataset Details
  - Table: Available parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All, P1, S1', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Summary > Dataset Details
  - Table: (no title)
  - Row: ('reportView', 'No', 'String', 'All', 'All, P1, S1', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Detail > Dataset Details
  - Table: Available parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All, ABS, ABSX, CMO, MBS, TBA', 'Defaults to "All" when no reportView is provided')
* **HIGH — Table row added**

  - Path: Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Summary > Dataset Details
  - Table: Available Parameters
  - Row: ('reportView', 'No', 'String', 'All', 'All, ABS, ABSX, CMO, MBS', 'Defaults to "All" when no reportView is provided')

.. END_FINRA_DOCUMENTATION_CHANGES

