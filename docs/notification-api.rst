.. highlight:: python

.. _notification:

================
Notification API
================

If you haven't read :ref:`getting_started`, :ref:`auth` and :ref:`client`, please start by reading those sections.

Each `Notification API <https://developer.finra.org/docs#notification_api>`__ dataset has its own query method. All datasets require Firm or Organization credentials. See each dataset's query method for the exact requirements.
 
 - :py:meth:`Client.get_finra_rulebook_notifications() <finra.base_client.BaseClient.get_finra_rulebook_notifications>`
 - :py:meth:`Client.get_draft_registration_filing_notifications() <finra.base_client.BaseClient.get_draft_registration_filing_notifications>`
 
+++++++++++++++
Datetime Ranges
+++++++++++++++

All Notification API datasets use ``start_datetime`` and ``end_datetime`` to specify a range for the requested data. These values can be provided to a dataset's query method as ``datetime.date`` or ``datetime.datetime`` objects, and will raise a ``TypeError`` for any other types. A ``datetime.datetime`` object will be automatically converted to the ``America/New_York`` timezone before a request is submitted. If a ``datetime.datetime`` object is not timezone-aware, it is assumed to be in the timezone of the application's local environment.

Response data follows these rules:
 
 - Notifications are only returned for the last 12 months.
 - If only the ``start_datetime`` is provided, notifications published at or after ``start_datetime`` are returned.
 - If only the ``end_datetime`` is provided, notifications published within the last 12 months up to the ``end_datetime`` are returned.
 - If neither datetimes are provided, only notifications published within the last month are returned.
 - If the date range is outside the last 12 months, the response will have a status code of ``200``, but no results.
 
Notification API endpoints do not support asynchronous requests, and only return ``application/json`` data.

++++++++
Examples
++++++++

The examples in this section are intended to demonstrate specific API concepts, not as production routines. In almost all cases, you should write your own routine that suits your application's needs.

------------------------
Chaining Datetime Ranges
------------------------

This example incrementally steps over one-day intervals to fetch all notifications in a date range. For additional considerations regarding pagination loops, see :ref:`large_datasets`.

.. code-block:: python

  from datetime import date, timedelta
  
  start = date(2025, 1, 1)          # initial date (inclusive)
  stop = date(2026, 1, 1)           # final date (non-inclusive)
  step = timedelta(days=1)          # step size
  
  start_date = start                # start of first query range
  limit = 1_000
  data = []                         # output data
  while start_date < stop:          # datetime loop
      end_date = start_date + step  # end of query range
      
      offset = 0
      while True:                   # pagination loop
          r = c.get_finra_rulebook_notifications(
              start_datetime=start_date,
              end_datetime=end_date,
              limit=limit,
              offset=offset
              )
          
          r.raise_for_status()
          
          _data = r.json()
          data.extend(_data)        # aggregate output data
          if len(_data) < limit:    # exit loop if fewer records than limit
              break
          
          offset += limit           # increment next page offset
          
      start_date = end_date         # increment start of next query range

