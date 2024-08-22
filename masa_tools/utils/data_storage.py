import os
import json
from datetime import datetime
from ..qc.logging import Logger
from ..qc.error_handler import ErrorHandler

class DataStorage:
    def __init__(self):
        """
        Initialize the DataStorage.
        """
        self.base_directory = 'data'
        self.logger = Logger("DataStorage")
        self.error_handler = ErrorHandler(self.logger)

    def get_file_path(self, source, query):
        """
        Get the file path for a specific source and query.

        :param source: The source of the data (e.g., 'xtwitter').
        :param query: The query used to retrieve the data.
        :return: The file path for the data.
        """ 
        directory = os.path.join(self.base_directory, source)
        os.makedirs(directory, exist_ok=True)
        filename = f"{query}.json"
        return os.path.join(directory, filename)

    @ErrorHandler.handle_error
    def save_data(self, data, source, query):
        """
        Save the retrieved data to a file in a structured directory within the 'data' directory.

        :param data: The data to be saved.
        :param source: The source of the data (e.g., 'xtwitter').
        :param query: The query used to retrieve the data.
        """
        file_path = self.get_file_path(source, query)
        
        try:
            with open(file_path, 'r+') as file:
                existing_data = json.load(file)
                existing_data['tweets'].extend(json.loads(data))
                file.seek(0)
                json.dump(existing_data, file, indent=4)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.log_warning(f"Creating new data file: {file_path}")
            initial_data = {
                'tweets': json.loads(data),
                'query': query,
                'source': source,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            with open(file_path, 'w') as file:
                json.dump(initial_data, file, indent=4)

        self.logger.log_info(f"Data saved to: {file_path}")