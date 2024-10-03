XTwitter Advanced Search
========================

The Advanced Search feature allows users to perform more complex queries to filter tweets according to various criteria such as date ranges, specific users, hashtags, and more. Below you will find detailed information on how to construct advanced search queries.

Exact Search
------------

Search for tweets containing specific hashtags.

**Syntax:** `"\"searchterm\"`

**Example:**

.. code-block:: json

    {
        "query": "\"masa\"",
        "count": 10
    }

Hashtag
-------

Search for tweets containing specific hashtags.

**Syntax:** `#hashtag`

**Example:**

.. code-block:: json

    {
        "query": "#MasaNode",
        "count": 10
    }

Mention
-------

Search for tweets mentioning a specific user.

**Syntax:** `@username`

**Example:**

.. code-block:: json

    {
        "query": "@getmasafi",
        "count": 10
    }

From User
---------

Search for tweets posted by a specific user.

**Syntax:** `from:username`

**Example:**

.. code-block:: json

    {
        "query": "from:getmasafi",
        "count": 10
    }

To User
-------

Search for tweets directed to a specific user.

**Syntax:** `to:username`

**Example:**

.. code-block:: json

    {
        "query": "to:getmasafi",
        "count": 10
    }

Language-Specific
-----------------

Search for tweets in a specific language.

**Syntax:** `lang:language_code`

**Example:**

.. code-block:: json

    {
        "query": "Masa lang:en",
        "count": 10
    }

Date Range
----------

Search for tweets within a specific date range.

**Syntax:** `since:yyyy-mm-dd until:yyyy-mm-dd`

**Example:**

.. code-block:: json

    {
        "query": "Masa since:2021-01-01 until:2021-12-31",
        "count": 10
    }

Retweets Filtering
------------------

Exclude retweets from your search results.

**Syntax:** `-filter:retweets`

**Example:**

.. code-block:: json

    {
        "query": "Masa -filter:retweets",
        "count": 10
    }

Minimum Likes Filter
--------------------

Search for tweets with a minimum number of likes.

**Syntax:** `min_faves:number`

**Example:**

.. code-block:: json

    {
        "query": "Masa min_faves:100",
        "count": 10
    }

Minimum Retweets Filter
-----------------------

Search for tweets with a minimum number of retweets.

**Syntax:** `min_retweets:number`

**Example:**

.. code-block:: json

    {
        "query": "Masa min_retweets:50",
        "count": 10
    }

Keyword Exclusion
-----------------

Exclude tweets with certain keywords.

**Syntax:** `-keyword`

**Example:**

.. code-block:: json

    {
        "query": "Masa -moon",
        "count": 10
    }

OR Operator
-----------

Combine multiple terms, where at least one must be present.

**Syntax:** `term1 OR term2`

**Example:**

.. code-block:: json

    {
        "query": "Masa OR Oracle",
        "count": 10
    }

Geo-location Based
------------------

Search for tweets by users located within a certain radius of a given latitude and longitude.

**Syntax:** `geocode:latitude,longitude,radius`

**Example:**

.. code-block:: json

    {
        "query": "Masa geocode:37.781157,-122.398720,1mi",
        "count": 10
    }

URL Inclusion
-------------

Search for tweets containing a specific URL.

**Syntax:** `url:"http://example.com"`

**Example:**

.. code-block:: json

    {
        "query": "url:\"http://example.com\"",
        "count": 10
    }

Question Tweets Filter
----------------------

Search for tweets asking a question.

**Syntax:** `?`

**Example:**

.. code-block:: json

    {
        "query": "Masa ?",
        "count": 10
    }

Safe Search Mode
----------------

Exclude adult content from your search results.

**Syntax:** `filter:safe`

**Example:**

.. code-block:: json

    {
        "query": "Masa filter:safe",
        "count": 10
    }

Composition Examples
--------------------

Combine multiple search criteria to create more complex queries.

**Example 1:**

Search for tweets containing the hashtag `#MasaNode`, posted by `@getmasafi`, and within a specific date range.

.. code-block:: json

    {
        "query": "#MasaNode from:getmasafi since:2021-01-01 until:2021-12-31",
        "count": 10
    }

**Example 2:**

Search for tweets mentioning `@getmasafi`, excluding retweets, and in English.

.. code-block:: json

    {
        "query": "@getmasafi -filter:retweets lang:en",
        "count": 10
    }

**Example 3:**

Search for tweets containing the keyword `Masa`, with a minimum of 100 likes, and within a 1-mile radius of a specific geolocation.

.. code-block:: json

    {
        "query": "Masa min_faves:100 geocode:37.781157,-122.398720,1mi",
        "count": 10
    }

Each of these search types can be combined to create more complex queries, allowing for highly targeted searches. Remember to test each example to ensure they work as expected and to provide users with accurate and helpful documentation.
