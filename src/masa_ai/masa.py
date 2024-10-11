"""
Main entry point for the MASA application.

This module provides the main functionality to process requests, view documentation, or list scraped data.
It initializes the necessary components and handles both programmatic and command-line interfaces.

Usage:
    As a library: from masa_ai import Masa
    As a CLI: masa-ai-cli <command> [options]

Commands:
- process: Process all requests (both resumed and new)
- docs: Rebuild and view the documentation
- data: List the scraped data files
- config get <key>: Get the value of a configuration key
- config set <key> <value>: Set the value of a configuration key
"""

import os
import sys
import subprocess
from typing import Optional, Union, List
from pathlib import Path
import json

class Masa:
    def __init__(self):
        from .configs.config import initialize_config, global_settings
        from .tools.qc.qc_manager import QCManager
        from .orchestration.request_manager import RequestManager
        
        initialize_config()
        self.global_settings = global_settings
        self.qc_manager = QCManager()
        self.qc_manager.log_debug("Initialized QCManager", context="Masa")
        
        try:
            self.request_manager = RequestManager()
            self.qc_manager.log_debug("Initialized RequestManager", context="Masa")
        except Exception as e:
            self.qc_manager.log_error(f"Error initializing RequestManager: {str(e)}", error_info=e, context="Masa")
            raise

    def process_requests(self, requests: Optional[Union[str, dict, list, Path]] = None) -> None:
        """
        Process requests from a JSON file, a list of requests, or a single request.

        Args:
            requests (Optional[Union[str, dict, list, Path]]): Path to the JSON file containing requests,
                                                               a list of requests, or a single request.
                                                               If None, process existing requests.
        """
        if requests is None:
            # Handle the case where no requests are provided
            self.qc_manager.log_info("No input provided. Processing existing requests.", context="Masa")
            self.request_manager.process_requests()
            self.qc_manager.log_info("Processing existing requests.", context="Masa")
            return

        elif isinstance(requests, (str, Path)):
            # If the input is a string or Path, assume it's a path to a JSON file
            self.qc_manager.log_debug(f"Processing requests from file: {requests}", context="Masa")
            with open(requests, 'r') as file:
                requests = json.load(file)
        elif isinstance(requests, dict):
            # If the input is a single request, wrap it in a list
            requests = [requests]
        elif not isinstance(requests, list):
            self.qc_manager.log_error("Invalid input for requests.", context="Masa")
            raise ValueError("Invalid input for requests.")

        self.qc_manager.log_debug(f"Processing {len(requests)} new requests", context="Masa")
        self.request_manager.process_requests(requests)
        self.qc_manager.log_info("Processing all requests", context="Masa")

    def view_docs(self, page: Optional[str] = None) -> None:
        """
        View documentation for the specified page or the main documentation.
        Always rebuilds the documentation before viewing.

        Args:
            page (str, optional): The name of the documentation page to view.
        """
        try:
            # Get the path to the masa package
            masa_path = Path(__file__).resolve().parent

            # Always rebuild the documentation
            self.qc_manager.log_info("Rebuilding documentation...", context="Masa")
            subprocess.run([sys.executable, str(masa_path / "docs" / "update_docs.py")], check=True, cwd=masa_path)

            # View the documentation
            view_docs_args = [sys.executable, str(masa_path / "docs" / "view_docs.py")]
            if page:
                view_docs_args.append(page)
            subprocess.run(view_docs_args, check=True, cwd=masa_path)

        except subprocess.CalledProcessError as e:
            self.qc_manager.log_error(f"Error: {e}", context="Masa")
            self.qc_manager.log_error("Please ensure the masa package is correctly installed and the documentation files are present.", context="Masa")

    def list_scraped_data(self) -> None:
        """
        List all scraped data files, organized within their subfolders.

        This method retrieves the data directory from the configuration settings
        and lists all files within that directory and its subdirectories.

        Raises:
            FileNotFoundError: If the data directory does not exist.
        """
        # Get the data directory from global settings
        data_directory = self.global_settings.get('data_storage.DATA_DIRECTORY')
        data_folder = Path(data_directory)

        # Check if the data folder exists
        if not data_folder.exists():
            self.qc_manager.log_error(f"No data folder found at {data_folder}", context="Masa")
            return

        self.qc_manager.log_info("Scraped data files:", context="Masa")
        for root, dirs, files in os.walk(data_folder):
            # Calculate the indentation level based on the depth from the data folder
            level = len(Path(root).relative_to(data_folder).parts)
            indent = ' ' * 4 * level
            self.qc_manager.log_info(f"{indent}{os.path.basename(root)}/", context="Masa")
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                self.qc_manager.log_info(f"{sub_indent}{file}", context="Masa")

        # Check if the data folder is empty
        if not any(data_folder.iterdir()):
            self.qc_manager.log_info("The data folder is empty.", context="Masa")

    def get_config(self, key: str):
        """
        Get the value of a configuration key using Dynaconf.

        Args:
            key (str): Configuration key in dot notation (e.g., 'twitter.BASE_URL').

        Returns:
            The value of the configuration key.
        """
        self.qc_manager.log_debug(f"Getting configuration for key: {key}", context="Masa")
        return self.global_settings.get(key)

    def set_config(self, key: str, value):
        """
        Set the value of a configuration key with appropriate type conversion.

        Args:
            key (str): Configuration key in dot notation.
            value: The value to set (string from CLI input).
        """
        # Attempt to convert the value to the correct type
        current_value = self.global_settings.get(key)
        if isinstance(current_value, bool):
            value = value.lower() in ('true', '1', 'yes')
        elif isinstance(current_value, int):
            value = int(value)
        elif isinstance(current_value, float):
            value = float(value)

        self.qc_manager.log_debug(
            f"Setting configuration for key: {key} to value: {value}",
            context="Masa"
        )
        self.global_settings.set(key, value)

    def list_requests(self, statuses: Optional[List[str]] = None) -> None:
        """
        List all requests, optionally filtering by their status.

        Args:
            statuses (List[str], optional): List of statuses to filter requests.
                                            If None, lists 'queued' and 'in_progress' requests.
        """
        if statuses is None:
            statuses = ['queued', 'in_progress']
        elif statuses == ['all']:
            statuses = ['queued', 'in_progress', 'completed', 'failed', 'cancelled']

        self.qc_manager.log_debug("Delegating request listing to RequestManager", context="Masa")
        self.request_manager.list_requests(statuses)

    def clear_requests(self, request_ids: Optional[List[str]] = None) -> None:
        """
        Clear queued or in-progress requests by changing their status to 'cancelled'.

        Args:
            request_ids (List[str], optional): List of request IDs to clear.
                                           If None, clears all queued or in-progress requests.
        """
        self.qc_manager.log_debug("Delegating request clearing to RequestManager", context="Masa")
        self.request_manager.clear_requests(request_ids)

def main(action: Optional[str] = None, arg: Optional[str] = None) -> int:
    """
    Main function to handle CLI operations.

    Args:
        action (str, optional): The action to perform. Either 'process', 'docs', or 'data'.
        arg (str, optional): Additional argument (JSON file path for 'process', page name for 'docs').

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    masa = Masa()
    try:
        if action == 'process':
            request_list_file = arg if arg else None
            masa.process_requests(request_list_file)
        elif action == 'docs':
            masa.view_docs(arg)
        elif action == 'data':
            masa.list_scraped_data()
        elif action == 'config get':
            value = masa.get_config(arg)
            print(f"{arg} = {value}", context="Masa")
        elif action == 'config set':
            key, value = arg.split(' ', 1)
            masa.set_config(key, value)
            print(f"Set {key} to {value}", context="Masa")
        elif action == 'list-requests':
            statuses = arg.split(',') if arg else None
            masa.list_requests(statuses)
        elif action == 'clear-requests':
            request_ids = arg.split(',') if arg else None
            masa.clear_requests(request_ids)
        else:
            masa.qc_manager.log_error("Invalid action. Allowable options are:", context="Masa")
            masa.qc_manager.log_error("- 'process': Process all requests (both resumed and new)", context="Masa")
            masa.qc_manager.log_error("- 'docs [page_name]': View the documentation for the specified page (page_name is optional)", context="Masa")
            masa.qc_manager.log_error("- 'data': List the scraped data files", context="Masa")
            masa.qc_manager.log_error("- 'config get <key>': Get the value of a configuration key", context="Masa")
            masa.qc_manager.log_error("- 'config set <key> <value>': Set the value of a configuration key", context="Masa")
            masa.qc_manager.log_error("- 'list-requests [statuses]': List requests filtered by statuses (comma-separated)", context="Masa")
            masa.qc_manager.log_error("- 'clear-requests [request_ids]': Clear queued or in-progress requests by IDs (comma-separated)", context="Masa")
            return 1
    except KeyboardInterrupt:
        # Handle keyboard interrupt gracefully
        masa.qc_manager.log_info("Keyboard interrupt received. Exiting gracefully...", context="Masa")
        return 130  # Exit code for keyboard interrupt
    except Exception as e:
        masa.qc_manager.log_error(f"An error occurred: {str(e)}", context="Masa")
        return 1
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: masa-cli <action> [path_to_requests_json]", context="Masa")
        print("Actions: 'process' or 'docs [page_name]'", context="Masa")
        sys.exit(1)

    action = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(main(action, arg))