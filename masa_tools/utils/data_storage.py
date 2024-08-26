import os
import json
from datetime import datetime
from masa_tools.qc.qc_manager import QCManager

class DataStorage:
    def __init__(self, base_directory='data'):
        self.base_directory = base_directory
        self.qc_manager = QCManager()

    def get_file_path(self, source, query, file_format='json'):
        directory = os.path.join(self.base_directory, source)
        os.makedirs(directory, exist_ok=True)
        filename = f"{query}.{file_format}"
        return os.path.join(directory, filename)

    def save_data(self, data, source, query, file_format='json'):
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
            self.qc_manager.log_error(f"Error saving data: {str(e)}", context="DataStorage")
            raise

    def _save_json(self, file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def _save_csv(self, file_path, data):
        # Implement CSV saving logic here
        pass