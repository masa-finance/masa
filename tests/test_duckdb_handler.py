"""
Tests for the DuckDBHandler class in the MASA project.

This module contains unit tests for the DuckDBHandler class,
specifically testing both synchronous and asynchronous database operations.

Run these tests with pytest.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from masa_ai.tools.database.duckdb_handler import DuckDBHandler
from masa_ai.tools.database.models.entities.request import Request
from masa_ai.tools.database.models.entities.tweet import Tweet
from masa_ai.tools.database.models.entities.tweet_stats import TweetStats

@pytest.fixture
def mock_qc_manager():
    """Create a mock QCManager instance."""
    qc_manager = MagicMock()
    qc_manager.log_info = MagicMock()
    qc_manager.log_error = MagicMock()
    qc_manager.log_warning = MagicMock()
    return qc_manager

@pytest.fixture
def temp_db_handler(mock_qc_manager):
    """Create a DuckDBHandler instance with a temporary database file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        handler = DuckDBHandler(str(db_path), mock_qc_manager)
        handler.connect()
        yield handler
        handler.disconnect()

@pytest.fixture
def sample_request():
    """Create a sample request for testing."""
    return {
        'request_id': 'test_request_1',
        'scraper': 'XTwitterScraper',
        'endpoint': 'data/twitter/tweets/recent',
        'params': {
            'query': 'test query',
            'count': 10
        },
        'priority': 1,
        'status': 'pending'  # Optional, will use default if not provided
    }

@pytest.fixture
def sample_tweets():
    """Create sample tweet data."""
    return [
        {
            'id': '1',
            'created_at': '2024-01-01T00:00:00Z',
            'text': 'Test tweet 1',
            'user': {
                'id': 'user1',
                'name': 'Test User 1',
                'username': 'testuser1'
            },
            'conversation_id': 'conv1',
            'likes': 10,
            'retweets': 5,
            'replies': 2,
            'views': 100,
            'hashtags': ['test'],
            'mentions': [{'id': 'user2', 'username': 'testuser2'}],
            'urls': ['https://example.com'],
            'photos': []
        },
        {
            'id': '2',
            'created_at': '2024-01-01T00:01:00Z',
            'text': 'Test tweet 2',
            'user': {
                'id': 'user2',
                'name': 'Test User 2',
                'username': 'testuser2'
            },
            'conversation_id': 'conv2',
            'likes': 20,
            'retweets': 8,
            'replies': 3,
            'views': 200,
            'hashtags': ['test2'],
            'mentions': [],
            'urls': [],
            'photos': []
        }
    ]

def test_connect_disconnect(temp_db_handler):
    """Test database connection and disconnection."""
    assert temp_db_handler.engine is not None
    assert temp_db_handler.Session is not None
    
    temp_db_handler.disconnect()
    assert temp_db_handler.engine is None
    assert temp_db_handler.Session is None

@pytest.mark.asyncio
async def test_connect_disconnect_async(mock_qc_manager):
    """Test asynchronous database connection and disconnection."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_async.db"
        handler = DuckDBHandler(str(db_path), mock_qc_manager)
        
        await handler.connect_async()
        assert handler.engine is not None
        assert handler.Session is not None
        
        await handler.disconnect_async()
        assert handler.engine is None
        assert handler.Session is None

def test_add_request(temp_db_handler, sample_request):
    """Test adding a request synchronously."""
    temp_db_handler.add_request(sample_request)
    
    result = temp_db_handler.get_request_by_id(sample_request['request_id'])
    assert result['request_id'] == sample_request['request_id']
    assert result['status'] == sample_request['status']
    assert result['params'] == sample_request['params']

@pytest.mark.asyncio
async def test_add_request_async(temp_db_handler, sample_request):
    """Test adding a request asynchronously."""
    await temp_db_handler.add_request_async(sample_request)
    
    result = await temp_db_handler.get_request_by_id_async(sample_request['request_id'])
    assert result['request_id'] == sample_request['request_id']
    assert result['status'] == sample_request['status']
    assert result['params'] == sample_request['params']

def _convert_tweet_data(tweet_data: dict, request_id: int) -> dict:
    """
    Convert raw tweet data to the format expected by the Tweet model.
    
    Args:
        tweet_data: Raw tweet data from the API
        request_id: ID of the associated request
        
    Returns:
        dict: Formatted tweet data for model creation
    """
    return {
        'tweet_id': tweet_data['id'],
        'request_id': request_id,
        'text': tweet_data['text'],
        'user_id': tweet_data['user']['id'],
        'user_name': tweet_data['user']['name'],
        'username': tweet_data['user'].get('username', 'unknown'),  # Add default
        'conversation_id': tweet_data.get('conversation_id', tweet_data['id']),  # Use tweet_id as fallback
        'likes': tweet_data.get('likes', 0),
        'retweets': tweet_data.get('retweets', 0),
        'replies': tweet_data.get('replies', 0),
        'views': tweet_data.get('views', 0),
        'hashtags': tweet_data.get('hashtags', []),
        'mentions': tweet_data.get('mentions', []),
        'urls': tweet_data.get('urls', []),
        'photos': tweet_data.get('photos', []),
        'additional_fields': {}
    }

def test_store_and_get_tweets(temp_db_handler, sample_tweets, sample_request):
    """Test storing and retrieving tweets."""
    # Add request first
    temp_db_handler.add_request(sample_request)
    
    # Get the request to get its ID
    with temp_db_handler.Session() as session:
        request = session.query(Request).filter_by(
            request_id=sample_request['request_id']
        ).first()
        
        # Get or create stats
        stats = session.query(TweetStats).filter_by(
            request_id=sample_request['request_id']
        ).first()
        
        if not stats:
            stats = TweetStats(
                request_id=sample_request['request_id'],
                total_tweets=0,
                api_call_count=0,
                total_response_time=0.0,
                unique_workers=[]
            )
            session.add(stats)
        
        # Convert and store tweets
        formatted_tweets = [
            _convert_tweet_data(tweet, request.id) 
            for tweet in sample_tweets
        ]
        
        for tweet_data in formatted_tweets:
            tweet = Tweet(**tweet_data)
            session.add(tweet)
        
        # Update stats
        stats.total_tweets = len(formatted_tweets)
        
        session.commit()
    
    # Test stats are updated correctly
    stats_dict = temp_db_handler.get_stats(sample_request['request_id'])
    assert stats_dict['total_tweets'] == len(sample_tweets)
    
    # Verify tweets were stored correctly
    with temp_db_handler.Session() as session:
        stored_tweets = session.query(Tweet).filter_by(
            request_id=request.id
        ).all()
        assert len(stored_tweets) == len(sample_tweets)
        
        # Verify tweet content
        for stored, original in zip(stored_tweets, sample_tweets):
            assert stored.tweet_id == original['id']
            assert stored.text == original['text']
            assert stored.user_id == original['user']['id']

def test_update_stats(temp_db_handler, sample_request):
    """Test updating tweet statistics."""
    temp_db_handler.add_request(sample_request)
    temp_db_handler.update_stats(
        request_id=sample_request['request_id'],
        new_tweets=5,
        response_time=1.5,
        worker_id='worker1'
    )
    
    stats = temp_db_handler.get_stats(sample_request['request_id'])
    assert stats['total_tweets'] == 5
    assert stats['api_call_count'] == 1
    assert stats['total_response_time'] == 1.5
    assert 'worker1' in stats['unique_workers']

def test_error_handling(temp_db_handler, mock_qc_manager):
    """Test error handling in database operations."""
    with patch.object(temp_db_handler, 'Session') as mock_session_factory:
        # Create a mock session
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None  # Ensure exception propagates
        
        # Make session.add raise an exception
        def raise_error(*args, **kwargs):
            raise Exception("Database error")
        
        mock_session.add.side_effect = raise_error
        mock_session_factory.return_value = mock_session

        # Test that exception is raised and error is logged
        with pytest.raises(Exception) as exc_info:
            temp_db_handler.add_request({
                'request_id': 'test',
                'endpoint': 'test/endpoint',
                'params': {},
                'status': 'pending'
            })
        
        assert str(exc_info.value) == "Database error"
        mock_qc_manager.log_error.assert_called_once_with(
            "Error adding request: Database error"
        )

@pytest.mark.asyncio
async def test_concurrent_operations(temp_db_handler, sample_request):
    """Test concurrent database operations."""
    import asyncio
    
    async def update_status(status):
        await temp_db_handler.update_request_status_async(
            sample_request['request_id'],
            status,
            {'progress': 0}
        )
    
    # Add initial request
    await temp_db_handler.add_request_async(sample_request)
    
    # Perform concurrent status updates
    await asyncio.gather(
        update_status('running'),
        update_status('completed')
    )
    
    # Verify final state
    result = await temp_db_handler.get_request_by_id_async(sample_request['request_id'])
    assert result['status'] in ['running', 'completed'] 