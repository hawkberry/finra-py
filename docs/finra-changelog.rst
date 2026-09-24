.. _finra_api_changelog:

===================
FINRA API Changelog
===================

This is an unofficial changelog for the `FINRA API <https://developer.finra.org/docs>`__.

This page tracks various kinds of changes to the API and its documentation. The purpose of the page is to help developers track API drift and better understand and implement FINRA API integrations.

See the :ref:`changelog` below for a complete record of ``HIGH`` and ``MEDIUM`` priority changes, sorted in reverse chronological order.

To receive a weekly digest of ``HIGH`` priority changes, and occasional ``finra-py`` related articles, subscribe by email:

* Weekly Digest (coming soon)

To receive changes of all priority levels, including ``LOW`` priority messages, subscribe to the RSS feed and filter categories based on your own requirements:

* `RSS Feed <https://raw.githubusercontent.com/hawkberry/finra-py/main/changelog.rss>`__

Changes are categorized based on the ``kind`` of change and the documentation ``section_type``, and each combination of categories is assigned a fixed message ``priority``. These fields are provided for category-based filtering in the RSS feed.

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

September 24, 2026
~~~~~~~~~~~~~~~~~~

* **HIGH** — Query API > TRACE Report Cards > TRACE Foreign Sovereign Debt Summary: Section added
* **HIGH** — Query API > TRACE Report Cards > TRACE Treasuries Execution Time Difference Summary: Section added
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Detail > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Summary > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Detail > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Summary > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Detail > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Summary > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Detail > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Summary > Dataset Details: Table removed — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Detail > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card Treasuries Summary > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Detail > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Card for Agency Debt Summary > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Detail > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Corporate Bonds Summary > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Detail > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')
* **MEDIUM** — Query API > TRACE Report Cards > TRACE Quality of Markets Report Cards for Securitized Products Summary > Dataset Details: Table added — Table ; Headers: ('Field', 'Required', 'Format', 'Example with Notes', 'Permitted Values', 'Notes')

.. END_FINRA_DOCUMENTATION_CHANGES

