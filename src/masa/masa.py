"""
Main entry point for the MASA application.

This module provides the main functionality to process requests or view documentation.
It initializes the necessary components and handles the command-line interface.

Usage:
    python masa.py <action> [path_to_requests_json]
    
    Actions:
    - 'process': Process all requests (both resumed and new)
    - '--docs [page_name]': View the documentation for the specified page
"""

import sys
from configs.config import initialize_config
from tools.qc.qc_manager import QCManager
from orchestration.request_manager import RequestManager
import json
import subprocess

def main(action, json_file_path=None):
    """
    Main function to process requests or retrieve request history.

    Args:
        action (str): The action to perform. Either 'process' or 'request_history'.
        json_file_path (str, optional): Path to the JSON file containing requests. Required for 'process' action.

    Raises:
        Exception: If there's an error during initialization or processing.

    Returns:
        None
    """
    try:
        initialize_config()
        
        qc_manager = QCManager()
        qc_manager.log_debug("Initialized QCManager", context="Masa")
        
        try:
            request_manager = RequestManager()
            qc_manager.log_debug("Initialized RequestManager", context="Masa")
        except Exception as e:
            qc_manager.log_error(f"Error initializing RequestManager: {str(e)}", error_info=e, context="Masa")
            raise

        try:
            if action == 'process':
                qc_manager.log_debug(f"Processing requests from file: {json_file_path}", context="Masa")
                request_manager.process_requests(json_file_path)
                qc_manager.log_info("Processing all requests", context="Masa")
            else:
                print("Invalid action. Allowable options are:")
                print("- 'process': Process all requests (both resumed and new)")
                print("- '--docs [page_name]': View the documentation for the specified page (page_name is optional)")
                sys.exit(1)
        except KeyboardInterrupt:
            qc_manager.log_info("Keyboard interrupt received. Exiting gracefully...", context="Masa")
            sys.exit(0)
    except Exception as e:
        qc_manager.log_error(f"An error occurred during initialization: {str(e)}", error_info=e, context="Masa")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <action> [path_to_requests_json]")
        print("Actions: 'process' or '--docs [page_name]'")
        sys.exit(1)

    action = sys.argv[1]

    if action == '--docs':
        page = sys.argv[2] if len(sys.argv) > 2 else None
        subprocess.run([sys.executable, 'docs/view_docs.py', page] if page else [sys.executable, 'docs/view_docs.py'])
    else:
        json_file_path = sys.argv[2] if len(sys.argv) == 3 else None
        try:
            main(action, json_file_path)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received. Stopping procecess...")
            sys.exit(0)