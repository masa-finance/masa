Usage
=====

The MASA application is designed to process data retrieval requests, primarily from Twitter (now X). The main entry point is the `masa-cli` command, which provides various actions for processing requests, viewing documentation, and listing scraped data.

Installation
------------

To install the MASA package, use pip:

.. code-block:: bash

    pip install masa

Command Line Usage
------------------

To use the MASA application, you can run the following command:

.. code-block:: bash

    masa-cli <action> [arguments]

Actions:
    - 'process [path_to_requests_json]': Process all requests (both resumed and new)
    - '--docs [page_name]': View the documentation for the specified page
    - '--data': List the scraped data files

Example usage:

.. code-block:: bash

    masa-cli process /path/to/request_list.json
    masa-cli --docs usage
    masa-cli --data

Request Format
--------------

Requests are defined in a JSON file. Each request should have the following structure:

.. code-block:: json

    {
        "retriever": "XTwitterRetriever",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 5,
        "params": {
            "query": "#Bitcoin since:2023-01-01 until:2023-01-05",
            "count": 100
        }
    }

Request Priority
----------------

The MASA application uses Python's priority queue to process requests in order of priority. The `priority` field in each request determines the order of execution, with lower values indicating higher priority. If the `priority` field is not specified, a default value of 100 is used.

.. code-block:: json

    {
        "retriever": "XTwitterRetriever",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 1,  // High priority request
        "params": {
            "query": "#Bitcoin",
            "count": 100
        }
    }

    {
        "retriever": "XTwitterRetriever",
        "endpoint": "data/twitter/tweets/recent",
        // No priority specified, default value of 100 will be used
        "params": {
            "query": "Ethereum lang:en -filter:retweets since:2023-06-10 until:2023-06-15",
            "count": 75
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

The RequestManager handles the processing of requests. It reads the JSON file, prioritizes the requests based on the `priority` field, and executes them using the appropriate retriever (currently only XTwitterRetriever is implemented).

The application will process all requests in the JSON file, handling both new requests and resuming any previously interrupted requests, in the order determined by their priority.
