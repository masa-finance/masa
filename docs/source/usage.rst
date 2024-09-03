Usage
=====

The MASA application is designed to process data retrieval requests, primarily from Twitter (now X). The main entry point is the `main.py` script, which accepts a JSON file containing a list of requests.

Command Line Usage
------------------

To use the MASA application, you can run the following command:

.. code-block:: bash

    python main.py <action> [path_to_requests_json]

Actions:
    - 'process': Process all requests (both resumed and new)
    - 'request_history': Get a history of all requests

Example usage:

.. code-block:: bash

    python main.py process /path/to/request_list.json
    python main.py request_history

Request Format
--------------

Requests are defined in a JSON file. Each request should have the following structure:

.. code-block:: json

    {
        "retriever": "XTwitterRetriever",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 1,
        "params": {
            "query": "#Bitcoin since:2023-01-01 until:2023-01-05",
            "count": 100
        }
    }

XTwitterRetriever and Timeframes
--------------------------------

The XTwitterRetriever now handles timeframes more flexibly:

1. If both 'since' and 'until' dates are provided in the query, they will be used as the date range for tweet retrieval.

2. If only 'until' date is provided, the 'since' date will be set to the default timeframe (specified in settings) before the 'until' date.

3. If no dates are provided, the 'until' date will be set to the current date, and the 'since' date will be set to the default timeframe before the current date.

4. The retriever processes the date range in smaller iterations (default is daily) to ensure comprehensive data collection.

Example:

.. code-block:: json

    {
        "retriever": "XTwitterRetriever",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 1,
        "params": {
            "query": "#Bitcoin",  // No dates specified, will use default timeframe
            "count": 100
        }
    }

    {
        "retriever": "XTwitterRetriever",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 2,
        "params": {
            "query": "Ethereum lang:en -filter:retweets since:2023-06-10 until:2023-06-15",  // Specific date range
            "count": 75
        }
    }

Request Processing
------------------

The RequestManager handles the processing of requests. It reads the JSON file, prioritizes the requests, and executes them using the appropriate retriever (currently only XTwitterRetriever is implemented).

The application will process all requests in the JSON file, handling both new requests and resuming any previously interrupted requests.

Request History
---------------

You can retrieve the history of all processed requests using the 'request_history' action. This will display the status and progress of all requests that have been processed by the system.