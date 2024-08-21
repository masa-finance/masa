import os
from datetime import datetime

class DataStorage:
    def __init__(self, base_directory):
        """
        Initialize the DataStorage with the base directory.

        :param base_directory: The base directory where the data will be stored.
        """
        self.base_directory = base_directory

    def save_data(self, data, source, query):
        """
        Save the retrieved data to a file in a structured directory.

        :param data: The data to be saved.
        :param source: The source of the data (e.g., 'xtwitter').
        :param query: The query used to retrieve the data.
        """
        # Create the directory structure
        current_date = datetime.now().strftime('%Y-%m-%d')
        directory = os.path.join(self.base_directory, source, query, current_date)
        os.makedirs(directory, exist_ok=True)

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.json"

        # Save the data to a file
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w') as file:
            file.write(data)

        print(f"Data saved to: {file_path}")