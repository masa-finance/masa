import pytest
from masa_ai.tools.validator.trending_tweets import TrendingTweets

@pytest.fixture
def trending_tweets():
    return TrendingTweets()

def test_fetch_trending_topic(trending_tweets):
    """Test the fetch method of TrendingTweets."""
    results = trending_tweets.fetch()
    for result in results:
        print(result)
    assert len(results) > 0, "Expected at least one trending topic"
