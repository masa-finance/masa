import psycopg2
from masa_tools.qc.logging import Logger
from masa_tools.qc.error_handler import ErrorHandler

class DatabaseConnection:
    """
    A class for handling database connections and operations.
    """

    def __init__(self, host, port, database, user, password):
        """
        Initialize the DatabaseConnection instance.

        :param host: The hostname or IP address of the database server.
        :type host: str
        :param port: The port number of the database server.
        :type port: int
        :param database: The name of the database to connect to.
        :type database: str
        :param user: The username for authentication.
        :type user: str
        :param password: The password for authentication.
        :type password: str
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.logger = Logger("DatabaseConnection")
        self.error_handler = ErrorHandler(self.logger)

    @ErrorHandler.handle_error
    def connect(self):
        """
        Connect to the database.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.logger.log_info("Connected to the database successfully.")
        except psycopg2.Error as e:
            self.error_handler.raise_error("DatabaseError", f"Error connecting to the database: {str(e)}")

    @ErrorHandler.handle_error
    def execute_query(self, query, params=None):
        """
        Execute a SQL query.

        :param query: The SQL query to execute.
        :type query: str
        :param params: The parameters to pass to the query (optional).
        :type params: tuple
        :return: The result of the query.
        :rtype: list
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                self.connection.commit()
                self.logger.log_info(f"Query executed successfully: {query}")
                return result
        except psycopg2.Error as e:
            self.connection.rollback()
            self.error_handler.raise_error("DatabaseError", f"Error executing query: {str(e)}")

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.logger.log_info("Disconnected from the database.")