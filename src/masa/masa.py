"""
Main entry point for the MASA application.

This module provides the main functionality to process requests, view documentation, or list scraped data.
It initializes the necessary components and handles both programmatic and command-line interfaces.

Usage:
    As a library: from masa import Masa
    As a CLI: python -m masa <action> [path_to_requests_json]
    
    Actions:
    - 'process': Process all requests (both resumed and new)
    - '--docs [page_name]': Rebuild and view the documentation for the specified page
    - '--data': List the scraped data files
"""

import sys
import subprocess
from typing import Optional
import os
import importlib.resources as resources
from pathlib import Path

class Masa:
    def __init__(self):
        from .configs.config import initialize_config
        from .tools.qc.qc_manager import QCManager
        from .orchestration.request_manager import RequestManager
        
        initialize_config()
        self.qc_manager = QCManager()
        self.qc_manager.log_debug("Initialized QCManager", context="Masa")
        
        try:
            self.request_manager = RequestManager()
            self.qc_manager.log_debug("Initialized RequestManager", context="Masa")
        except Exception as e:
            self.qc_manager.log_error(f"Error initializing RequestManager: {str(e)}", error_info=e, context="Masa")
            raise

    def process_requests(self, json_file_path: str) -> None:
        """
        Process requests from a JSON file.

        Args:
            json_file_path (str): Path to the JSON file containing requests.

        Raises:
            Exception: If there's an error during processing.
        """
        self.qc_manager.log_debug(f"Processing requests from file: {json_file_path}", context="Masa")
        self.request_manager.process_requests(json_file_path)
        self.qc_manager.log_info("Processing all requests", context="Masa")

    def view_docs(self, page: Optional[str] = None) -> None:
        """
        View documentation for the specified page or the main documentation.
        Always rebuilds the documentation before viewing.

        Args:
            page (str, optional): The name of the documentation page to view.
        """
        try:
            # Get the path to the docs directory
            docs_path = resources.files('masa').joinpath('../../docs')
            
            if not docs_path.exists():
                raise FileNotFoundError(f"Docs path not found: {docs_path}")

            view_docs_path = docs_path / 'view_docs.py'
            update_docs_path = docs_path / 'update_docs.py'

            if not view_docs_path.exists():
                raise FileNotFoundError(f"view_docs.py not found in {docs_path}")

            # Always rebuild the documentation
            print("Rebuilding documentation...")
            subprocess.run([sys.executable, str(update_docs_path)], check=True)

            # View the documentation
            cmd = [sys.executable, str(view_docs_path)]
            if page:
                cmd.append(page)
            subprocess.run(cmd, check=True)

        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Please ensure the masa package is correctly installed and the documentation files are present.")
        except subprocess.CalledProcessError:
            print("Error: Failed to build or view the documentation.")
            print("Please try running 'python -m masa.docs.update_docs' manually and check for errors.")

    def list_scraped_data(self) -> None:
        """
        List all scraped data files, organized within their subfolders.
        """
        # Get the absolute path to the masa package directory
        masa_dir = Path(__file__).resolve().parent

        # Construct the path to the data folder relative to the masa package directory
        data_folder = masa_dir / "data"

        # Check if the data folder exists
        if not data_folder.exists():
            print(f"No data folder found at {data_folder}")
            return

        self.qc_manager.log_info("Scraped data files:", context="Masa")
        for root, dirs, files in os.walk(data_folder):
            # Calculate the indentation level based on the depth of the current directory
            level = len(Path(root).relative_to(data_folder).parts)
            indent = ' ' * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                print(f"{sub_indent}{file}")

        # Check if the data folder is empty
        if not any(data_folder.iterdir()):
            self.qc_manager.log_info("The data folder is empty.", context="Masa")

def main(action: Optional[str] = None, arg: Optional[str] = None) -> int:
    """
    Main function to handle CLI operations.

    Args:
        action (str, optional): The action to perform. Either 'process', '--docs', or '--data'.
        arg (str, optional): Additional argument (json file path for 'process', page name for '--docs').

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        masa = Masa()
        
        if action == 'process':
            request_list_file = Path(arg) if arg else None
            masa.process_requests(request_list_file)
        elif action == '--docs':
            masa.view_docs(arg)
        elif action == '--data':
            masa.list_scraped_data()
        else:
            masa.qc_manager.log_error("Invalid action. Allowable options are:", context="Masa")
            masa.qc_manager.log_error("- 'process': Process all requests (both resumed and new)", context="Masa")
            masa.qc_manager.log_error("- '--docs [page_name]': View the documentation for the specified page (page_name is optional)", context="Masa")
            masa.qc_manager.log_error("- '--data': List the scraped data files", context="Masa")
            return 1
    except KeyboardInterrupt:
        # Handle keyboard interrupt gracefully
        masa.qc_manager.log_info("Keyboard interrupt received. Exiting gracefully...", context="Masa")
        return 130  # Exit code for keyboard interrupt
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m masa <action> [path_to_requests_json]")
        print("Actions: 'process' or '--docs [page_name]'")
        sys.exit(1)

    action = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(main(action, arg))