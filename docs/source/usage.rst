Usage
=====

The MASA package provides several modules for data retrieval, structuring, augmentation, and quality control. Here's a brief overview of how to use the main components:

Retrieve Module
---------------

The retrieve module is used for fetching data from various sources.

.. code-block:: python

   from masa.retrieve import retrieve_twitter

   # Example usage of retrieve_twitter
   tweets = retrieve_twitter.get_tweets(query="python", count=100)
