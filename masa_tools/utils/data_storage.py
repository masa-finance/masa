import os
from datetime import datetime

class DataStorage:
    def __init__(self):
        """
        Initialize the DataStorage.
        """
        self.base_directory = 'data'

    def save_data(self, data, source, query):
        """
        Save the retrieved data to a file in a structured directory within the 'data' directory.

        :param data: The data to be saved.
        :param source: The source of the data (e.g., 'xtwitter').
        :param query: The query used to retrieve the data.
        """
        # Create the directory structure within the 'data' directory
        directory = os.path.join(self.base_directory, source)
        os.makedirs(directory, exist_ok=True)

        # Generate a unique filename based on the query and current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{query}_{timestamp}.json"

        # Save the data to a file
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w') as file:
            file.write(data)

        print(f"Data saved to: {file_path}")