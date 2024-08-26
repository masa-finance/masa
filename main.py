import json
import sys
from orchestration.request_manager import RequestManager
from configs.config import XTwitterConfig
from masa_tools.qc.qc_manager import QCManager

qc_manager = QCManager()
# Use qc_manager throughout the file

def main(action, json_file_path=None):
    """
    Main function to process requests or get all requests statuses.

    :param action: Action to perform ('process' or 'status').
    :param json_file_path: Path to the JSON file containing requests (optional).
    """
    config = XTwitterConfig().get_config()
    qc_manager.debug(f"Config loaded: {config}", context="Main")
    request_manager = RequestManager(config)

    if action == 'process':
        # Process all requests (both resumed and new)
        qc_manager.debug(f"Processing requests from file: {json_file_path}", context="Main")
        request_manager.process_requests(json_file_path)
        qc_manager.log_info("Processing all requests", context="Main")
    elif action == 'request_history':
        # Get the status of all requests
        all_requests_status = request_manager.get_all_requests_status()
        print(json.dumps(all_requests_status, indent=4))
    else:
        # Print the allowable options
        print("Invalid action. Allowable options are:")
        print("- 'process': Process all requests (both resumed and new)")
        print("- 'request_history': Get a history of all requests")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python main.py <action> [path_to_requests_json]")
        print("Actions: 'process' or 'request_history'")
        sys.exit(1)

    action = sys.argv[1]
    json_file_path = sys.argv[2] if len(sys.argv) == 3 else None
    main(action, json_file_path)