"""
Data Storage module for the MASA project.

This module provides the DataStorage class, which handles saving data
to files in various formats, primarily JSON and CSV.
"""

import os
import json
from datetime import datetime
from tools.qc import qc_manager as qc

class DataStorage:
    """
    DataStorage class for handling file-based data storage operations.

    This class provides methods to save data in different formats and
    manage file paths for data storage.
    """

    def __init__(self, base_directory='data'):
        """
        Initialize the DataStorage class.

        Args:
            base_directory (str): The base directory for storing data files. Defaults to 'data'.
        """
        self.base_directory = base_directory
        self.qc_manager = qc.QCManager()

    def get_file_path(self, source, query, file_format='json'):
        """
        Get the file path for storing data.

        Args:
            source (str): The data source.
            query (str): The query associated with the data.
            file_format (str): The file format for storing the data. Defaults to 'json'.

        Returns:
            str: The file path.
        """
        directory = os.path.join(self.base_directory, source)
        os.makedirs(directory, exist_ok=True)
        filename = f"{query}.{file_format}"
        return os.path.join(directory, filename)

    def save_data(self, data, source, query, file_format='json'):
        """
        Save data to a file.

        Args:
            data: The data to be saved.
            source (str): The data source.
            query (str): The query associated with the data.
            file_format (str): The file format for storing the data. Defaults to 'json'.

        Raises:
            ValueError: If an unsupported file format is specified.
        """
        file_path = self.get_file_path(source, query, file_format)
        
        try:
            if file_format == 'json':
                self._save_json(file_path, data)
            elif file_format == 'csv':
                self._save_csv(file_path, data)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            self.qc_manager.log_info(f"Data saved to: {file_path}", context="DataStorage")
        except Exception as e:
            self.qc_manager.log_error(f"Error saving data: {str(e)}", error_info=e, context="DataStorage")
            raise

    def _save_json(self, file_path, data):
        """
        Save data to a JSON file.

        Args:
            file_path (str): The file path for saving the JSON data.
            data: The data to be saved as JSON.
        """
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _save_csv(self, file_path, data):
        """
        Save data to a CSV file.

        Args:
            file_path (str): The file path for saving the CSV data.
            data: The data to be saved as CSV.

        Note:
            This method is not implemented yet.
        """
        # Implement CSV saving logic here
        pass