Usage
=====

The MASA application is designed to process data scraping requests, primarily from Twitter (now X). The main entry point is the `masa-ai-cli` command, which provides various actions for processing requests, viewing documentation, listing scraped data, and managing requests.

Installation
------------

To install the MASA package, use pip:

.. code-block:: bash

    pip install masa-ai

Command Line Usage
------------------

To use the MASA application, run the following command:

.. code-block:: bash

    masa-ai-cli <command> [options]

Available commands:

- **process [path_to_requests_json]**: Process all requests (both resumed and new).
- **docs [page_name]**: Rebuild and view the documentation for the specified page (`page_name` is optional).
- **data**: List the scraped data files.
- **list-requests [--statuses STATUS_LIST]**: List requests filtered by statuses.
- **clear-requests [REQUEST_IDS]**: Clear queued or in-progress requests by IDs.

Example usage:

.. code-block:: bash

    # Process requests from a JSON file
    masa-ai-cli process /path/to/request_list.json

    # View the usage documentation
    masa-ai-cli docs usage

    # List scraped data files
    masa-ai-cli data

    # List queued and in-progress requests
    masa-ai-cli list-requests

    # List requests with specific statuses
    masa-ai-cli list-requests --statuses completed,failed

    # Clear all queued and in-progress requests
    masa-ai-cli clear-requests

    # Clear specific requests by IDs
    masa-ai-cli clear-requests req1,req2,req3

Managing Requests
-----------------

### Listing Requests

You can list the current requests that are queued or in progress:

.. code-block:: bash

    masa-ai-cli list-requests

By default, this command lists requests with statuses ``queued`` and ``in_progress``. You can specify other statuses using the ``--statuses`` option:

.. code-block:: bash

    masa-ai-cli list-requests --statuses completed,failed

To list all requests regardless of their status:

.. code-block:: bash

    masa-ai-cli list-requests --statuses all

### Clearing Requests

To clear all requests that are queued or in progress:

.. code-block:: bash

    masa-ai-cli clear-requests

To clear specific requests by their IDs:

.. code-block:: bash

    masa-ai-cli clear-requests req1,req2,req3

**Note:** Requests that are cleared will have their status changed to ``cancelled`` and will not be processed.

Request Format
--------------

Requests are defined in a JSON file. Each request should have the following structure:

.. code-block:: json

    {
        "scraper": "XTwitterScraper",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 5,
        "params": {
            "query": "#Bitcoin since:2023-01-01 until:2023-01-05",
            "count": 100
        }
    }

Request Priority
----------------

The MASA application uses a priority queue to process requests in order of priority. The ``priority`` field in each request determines the order of execution, with lower values indicating higher priority. If the ``priority`` field is not specified, a default value of 100 is used.

Example:

.. code-block:: json

    {
        "scraper": "XTwitterScraper",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 1,  // High priority request
        "params": {
            "query": "#Bitcoin",
            "count": 100
        }
    }

    {
        "scraper": "XTwitterScraper",
        "endpoint": "data/twitter/tweets/recent",
        // No priority specified, default value of 100 will be used
        "params": {
            "query": "Ethereum lang:en -filter:retweets since:2023-06-10 until:2023-06-15",
            "count": 75
        }
    }

XTwitterScraper and Timeframes
------------------------------

The XTwitterScraper handles timeframes flexibly:

1. If both ``since`` and ``until`` dates are provided in the query, they will be used as the date range for tweet retrieval.

2. If only the ``until`` date is provided, the ``since`` date will be set to the default timeframe (specified in settings) before the ``until`` date.

3. If no dates are provided, the ``until`` date will be set to the current date, and the ``since`` date will be set to the default timeframe before the current date.

4. The scraper processes the date range in smaller iterations (default is daily) to ensure comprehensive data collection.

Example:

.. code-block:: json

    {
        "scraper": "XTwitterScraper",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 1,
        "params": {
            "query": "#Bitcoin",  // No dates specified, will use default timeframe
            "count": 100
        }
    }

    {
        "scraper": "XTwitterScraper",
        "endpoint": "data/twitter/tweets/recent",
        "priority": 2,
        "params": {
            "query": "Ethereum lang:en -filter:retweets since:2023-06-10 until:2023-06-15",  // Specific date range
            "count": 75
        }
    }

Request Processing
------------------

The RequestManager handles the processing of requests. It reads the JSON file, prioritizes the requests based on the ``priority`` field, and executes them using the appropriate scraper (currently only XTwitterScraper is implemented).

The application processes all requests in the JSON file, handling both new requests and resuming any previously interrupted requests, in the order determined by their priority.

Viewing Scraped Data
--------------------

To view the scraped data files, use the following command:

.. code-block:: bash

    masa-ai-cli data

This command lists all the data files scraped and saved in the ``data`` directory.

Configuration
-------------

The MASA application uses YAML files for configuration:

- **settings.yaml**: Main configuration file containing settings for Twitter API, request management, and logging.
- **.secrets.yaml**: (Optional) File for storing sensitive information like API keys.

These files are located in the ``configs`` directory.

For custom configurations, you can edit the ``settings.yaml`` file or set environment variables as needed.

Documentation
-------------

You can rebuild and view the project documentation using the following command:

.. code-block:: bash

    masa-ai-cli docs [page_name]

If no ``page_name`` is provided, the documentation for the entire project will be displayed.

Further Assistance
------------------

For additional help and information, refer to the project's README or use the ``--help`` option with any command:

.. code-block:: bash

    masa-ai-cli --help

    masa-ai-cli process --help

    masa-ai-cli list-requests --help