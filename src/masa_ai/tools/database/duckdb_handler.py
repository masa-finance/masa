import json
import asyncio
import duckdb
from typing import Any, Dict, List, Optional

from masa_ai.tools.database.abstract_database_handler import AbstractDatabaseHandler


class DuckDBHandler(AbstractDatabaseHandler):
    """Concrete implementation of AbstractDatabaseHandler for DuckDB.
    
    This class handles all database operations using DuckDB as the backend.
    It implements the full AbstractDatabaseHandler interface with both
    synchronous and asynchronous methods.
    """

    def __init__(self, database_path: str, qc_manager: 'QCManager'):
        """Initialize DuckDBHandler with database path and QC manager.

        Args:
            database_path (str): Path to the DuckDB database file
            qc_manager (QCManager): Quality control manager for logging
        """
        self.database_path = database_path
        self.connection = None
        self.qc_manager = qc_manager

    def connect(self) -> None:
        """Establish synchronous connection to DuckDB database."""
        self.connection = duckdb.connect(self.database_path)
        self._initialize_tables()

    async def connect_async(self) -> None:
        """Establish asynchronous connection to DuckDB database."""
        self.connection = await asyncio.to_thread(duckdb.connect, self.database_path)
        await self._initialize_tables_async()

    def disconnect(self) -> None:
        """Close synchronous database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    async def disconnect_async(self) -> None:
        """Close asynchronous database connection."""
        if self.connection:
            await asyncio.to_thread(self.connection.close)
            self.connection = None

    def _initialize_tables(self) -> None:
        """Initialize required database tables synchronously."""
        tables = self._get_table_definitions()
        for table in tables:
            self.connection.execute(table)

    async def _initialize_tables_async(self) -> None:
        """Initialize required database tables asynchronously."""
        tables = self._get_table_definitions()
        for table in tables:
            await asyncio.to_thread(self.connection.execute, table)

    def _get_table_definitions(self) -> List[str]:
        """Get SQL table definitions.

        Returns:
            List[str]: List of CREATE TABLE statements
        """
        return [
            """
            CREATE TABLE IF NOT EXISTS requests (
                request_id VARCHAR PRIMARY KEY,
                status VARCHAR,
                params JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id VARCHAR,
                request_id VARCHAR,
                created_at TIMESTAMP,
                text TEXT,
                user_id VARCHAR,
                user_name VARCHAR,
                PRIMARY KEY (tweet_id, request_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tweet_stats (
                request_id VARCHAR PRIMARY KEY,
                total_tweets INTEGER DEFAULT 0,
                api_call_count INTEGER DEFAULT 0,
                total_response_time DOUBLE DEFAULT 0,
                unique_workers JSON DEFAULT '[]'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR,
                message TEXT,
                context VARCHAR DEFAULT '',
                error_info JSON DEFAULT NULL
            )
            """
        ]

    def add_request(self, request: Dict[str, Any]) -> None:
        """Add new request to database synchronously."""
        insert_query = """
        INSERT INTO requests (request_id, status, params)
        VALUES (?, ?, ?)
        """
        try:
            params = (request['request_id'], request['status'], json.dumps(request['params']))
            self.connection.execute(insert_query, params)
            self.qc_manager.log_info(f"Added request {request['request_id']}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to add request: {e}", context="DuckDBHandler")
            raise

    async def add_request_async(self, request: Dict[str, Any]) -> None:
        """Add new request to database asynchronously."""
        insert_query = """
        INSERT INTO requests (request_id, status, params)
        VALUES (?, ?, ?)
        """
        try:
            params = (request['request_id'], request['status'], json.dumps(request['params']))
            await asyncio.to_thread(self.connection.execute, insert_query, params)
            self.qc_manager.log_info(f"Added request {request['request_id']}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to add request: {e}", context="DuckDBHandler")
            raise

    def update_request_status(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update request status synchronously."""
        update_query = """
        UPDATE requests
        SET status = ?, last_updated = CURRENT_TIMESTAMP
        WHERE request_id = ?
        """
        try:
            self.connection.execute(update_query, (status, request_id))
            self.qc_manager.log_info(f"Updated status of request {request_id} to {status}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to update request status: {e}", context="DuckDBHandler")
            raise

    async def update_request_status_async(self, request_id: str, status: str, progress: Dict[str, Any]) -> None:
        """Update request status asynchronously."""
        update_query = """
        UPDATE requests
        SET status = ?, last_updated = CURRENT_TIMESTAMP
        WHERE request_id = ?
        """
        try:
            await asyncio.to_thread(self.connection.execute, update_query, (status, request_id))
            self.qc_manager.log_info(f"Updated status of request {request_id} to {status}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to update request status: {e}", context="DuckDBHandler")
            raise

    def get_request_by_id(self, request_id: str) -> Dict[str, Any]:
        """Get request by ID synchronously."""
        select_query = "SELECT * FROM requests WHERE request_id = ?"
        try:
            result = self.connection.execute(select_query, (request_id,))
            row = result.fetchone()
            if row:
                columns = [desc[0] for desc in result.description]
                request_data = dict(zip(columns, row))
                request_data['params'] = json.loads(request_data['params'])
                return request_data
            return {}
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get request: {e}", context="DuckDBHandler")
            raise

    async def get_request_by_id_async(self, request_id: str) -> Dict[str, Any]:
        """Get request by ID asynchronously."""
        select_query = "SELECT * FROM requests WHERE request_id = ?"
        try:
            result = await asyncio.to_thread(self.connection.execute, select_query, (request_id,))
            row = result.fetchone()
            if row:
                columns = [desc[0] for desc in result.description]
                request_data = dict(zip(columns, row))
                request_data['params'] = json.loads(request_data['params'])
                return request_data
            return {}
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get request: {e}", context="DuckDBHandler")
            raise

    def get_all_requests(self) -> List[Dict[str, Any]]:
        """Get all requests synchronously."""
        select_query = "SELECT * FROM requests"
        try:
            result = self.connection.execute(select_query)
            rows = result.fetchall()
            columns = [desc[0] for desc in result.description]
            requests = []
            for row in rows:
                request = dict(zip(columns, row))
                request['params'] = json.loads(request['params'])
                requests.append(request)
            return requests
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get all requests: {e}", context="DuckDBHandler")
            raise

    async def get_all_requests_async(self) -> List[Dict[str, Any]]:
        """Get all requests asynchronously."""
        select_query = "SELECT * FROM requests"
        try:
            result = await asyncio.to_thread(self.connection.execute, select_query)
            rows = result.fetchall()
            columns = [desc[0] for desc in result.description]
            requests = []
            for row in rows:
                request = dict(zip(columns, row))
                request['params'] = json.loads(request['params'])
                requests.append(request)
            return requests
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get all requests: {e}", context="DuckDBHandler")
            raise

    def remove_request(self, request_id: str) -> None:
        """Remove request synchronously."""
        delete_query = "DELETE FROM requests WHERE request_id = ?"
        try:
            self.connection.execute(delete_query, (request_id,))
            self.qc_manager.log_info(f"Removed request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to remove request: {e}", context="DuckDBHandler")
            raise

    async def remove_request_async(self, request_id: str) -> None:
        """Remove request asynchronously."""
        delete_query = "DELETE FROM requests WHERE request_id = ?"
        try:
            await asyncio.to_thread(self.connection.execute, delete_query, (request_id,))
            self.qc_manager.log_info(f"Removed request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to remove request: {e}", context="DuckDBHandler")
            raise

    def enqueue_request(self, request_id: str, priority: int = 1) -> None:
        """Enqueue request synchronously."""
        update_query = """
        UPDATE requests 
        SET status = 'queued', last_updated = CURRENT_TIMESTAMP
        WHERE request_id = ?
        """
        try:
            self.connection.execute(update_query, (request_id,))
            self.qc_manager.log_info(f"Enqueued request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to enqueue request: {e}", context="DuckDBHandler")
            raise

    async def enqueue_request_async(self, request_id: str, priority: int = 1) -> None:
        """Enqueue request asynchronously."""
        update_query = """
        UPDATE requests 
        SET status = 'queued', last_updated = CURRENT_TIMESTAMP
        WHERE request_id = ?
        """
        try:
            await asyncio.to_thread(self.connection.execute, update_query, (request_id,))
            self.qc_manager.log_info(f"Enqueued request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to enqueue request: {e}", context="DuckDBHandler")
            raise

    def store_tweets(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets synchronously."""
        insert_query = """
        INSERT INTO tweets (tweet_id, request_id, created_at, text, user_id, user_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            for tweet in tweets:
                params = (
                    tweet['id'],
                    request_id,
                    tweet['created_at'],
                    tweet['text'],
                    tweet['user']['id'],
                    tweet['user']['name']
                )
                self.connection.execute(insert_query, params)
            self.qc_manager.log_info(f"Stored {len(tweets)} tweets for request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to store tweets: {e}", context="DuckDBHandler")
            raise

    async def store_tweets_async(self, tweets: List[Dict[str, Any]], request_id: str) -> None:
        """Store tweets asynchronously."""
        insert_query = """
        INSERT INTO tweets (tweet_id, request_id, created_at, text, user_id, user_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            for tweet in tweets:
                params = (
                    tweet['id'],
                    request_id,
                    tweet['created_at'],
                    tweet['text'],
                    tweet['user']['id'],
                    tweet['user']['name']
                )
                await asyncio.to_thread(self.connection.execute, insert_query, params)
            self.qc_manager.log_info(f"Stored {len(tweets)} tweets for request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to store tweets: {e}", context="DuckDBHandler")
            raise

    def update_stats(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update tweet statistics synchronously."""
        try:
            select_query = "SELECT * FROM tweet_stats WHERE request_id = ?"
            result = self.connection.execute(select_query, (request_id,))
            current_stats = result.fetchone()

            if current_stats:
                columns = [desc[0] for desc in result.description]
                stats_dict = dict(zip(columns, current_stats))
                unique_workers = set(json.loads(stats_dict['unique_workers']))
                unique_workers.add(worker_id)

                update_query = """
                UPDATE tweet_stats 
                SET total_tweets = total_tweets + ?,
                    api_call_count = api_call_count + 1,
                    total_response_time = total_response_time + ?,
                    unique_workers = ?
                WHERE request_id = ?
                """
                params = (new_tweets, response_time, json.dumps(list(unique_workers)), request_id)
            else:
                update_query = """
                INSERT INTO tweet_stats (request_id, total_tweets, api_call_count, total_response_time, unique_workers)
                VALUES (?, ?, 1, ?, ?)
                """
                params = (request_id, new_tweets, response_time, json.dumps([worker_id]))

            self.connection.execute(update_query, params)
            self.qc_manager.log_info(f"Updated stats for request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to update stats: {e}", context="DuckDBHandler")
            raise

    async def update_stats_async(self, request_id: str, new_tweets: int, response_time: float, worker_id: str) -> None:
        """Update tweet statistics asynchronously."""
        try:
            select_query = "SELECT * FROM tweet_stats WHERE request_id = ?"
            result = await asyncio.to_thread(self.connection.execute, select_query, (request_id,))
            current_stats = result.fetchone()

            if current_stats:
                columns = [desc[0] for desc in result.description]
                stats_dict = dict(zip(columns, current_stats))
                unique_workers = set(json.loads(stats_dict['unique_workers']))
                unique_workers.add(worker_id)

                update_query = """
                UPDATE tweet_stats 
                SET total_tweets = total_tweets + ?,
                    api_call_count = api_call_count + 1,
                    total_response_time = total_response_time + ?,
                    unique_workers = ?
                WHERE request_id = ?
                """
                params = (new_tweets, response_time, json.dumps(list(unique_workers)), request_id)
            else:
                update_query = """
                INSERT INTO tweet_stats (request_id, total_tweets, api_call_count, total_response_time, unique_workers)
                VALUES (?, ?, 1, ?, ?)
                """
                params = (request_id, new_tweets, response_time, json.dumps([worker_id]))

            await asyncio.to_thread(self.connection.execute, update_query, params)
            self.qc_manager.log_info(f"Updated stats for request {request_id}", context="DuckDBHandler")
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to update stats: {e}", context="DuckDBHandler")
            raise

    def get_stats(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics synchronously."""
        select_query = "SELECT * FROM tweet_stats WHERE request_id = ?"
        try:
            result = self.connection.execute(select_query, (request_id,))
            row = result.fetchone()
            if row:
                columns = [desc[0] for desc in result.description]
                stats = dict(zip(columns, row))
                stats['unique_workers'] = json.loads(stats['unique_workers'])
                return stats
            return {}
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get stats: {e}", context="DuckDBHandler")
            raise

    async def get_stats_async(self, request_id: str) -> Dict[str, Any]:
        """Get tweet statistics asynchronously."""
        select_query = "SELECT * FROM tweet_stats WHERE request_id = ?"
        try:
            result = await asyncio.to_thread(self.connection.execute, select_query, (request_id,))
            row = result.fetchone()
            if row:
                columns = [desc[0] for desc in result.description]
                stats = dict(zip(columns, row))
                stats['unique_workers'] = json.loads(stats['unique_workers'])
                return stats
            return {}
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get stats: {e}", context="DuckDBHandler")
            raise

    def log_message(self, level: str, message: str, context: str = "", error_info: Any = None) -> None:
        """Log message synchronously."""
        insert_query = """
        INSERT INTO logs (level, message, context, error_info)
        VALUES (?, ?, ?, ?)
        """
        try:
            error_json = json.dumps(error_info) if error_info else None
            self.connection.execute(insert_query, (level, message, context, error_json))
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to log message: {e}", context="DuckDBHandler")
            raise

    async def log_message_async(self, level: str, message: str, context: str = "", error_info: Any = None) -> None:
        """Log message asynchronously."""
        insert_query = """
        INSERT INTO logs (level, message, context, error_info)
        VALUES (?, ?, ?, ?)
        """
        try:
            error_json = json.dumps(error_info) if error_info else None
            await asyncio.to_thread(self.connection.execute, insert_query, (level, message, context, error_json))
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to log message: {e}", context="DuckDBHandler")
            raise

    def get_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get logs synchronously."""
        try:
            if level:
                select_query = "SELECT * FROM logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?"
                result = self.connection.execute(select_query, (level, limit))
            else:
                select_query = "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?"
                result = self.connection.execute(select_query, (limit,))

            rows = result.fetchall()
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in rows]
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get logs: {e}", context="DuckDBHandler")
            raise

    async def get_logs_async(self, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get logs asynchronously."""
        try:
            if level:
                select_query = "SELECT * FROM logs WHERE level = ? ORDER BY timestamp DESC LIMIT ?"
                result = await asyncio.to_thread(self.connection.execute, select_query, (level, limit))
            else:
                select_query = "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?"
                result = await asyncio.to_thread(self.connection.execute, select_query, (limit,))

            rows = result.fetchall()
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in rows]
        except duckdb.Error as e:
            self.qc_manager.log_error(f"Failed to get logs: {e}", context="DuckDBHandler")
            raise
