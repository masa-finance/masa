import pytest
from masa_ai.tools.validator.trending_queries import TrendingQueries

@pytest.fixture
def trending_queries():
    return TrendingQueries()

def test_fetch_trending_topic(trending_queries):
    """Test the fetch method of TrendingQueries."""
    results = trending_queries.fetch()
    for result in results:
        print(result)
    assert len(results) > 0, "Expected at least one trending topic"
