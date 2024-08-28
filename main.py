import sys
from orchestration.request_manager import RequestManager
from configs.config import initialize_config, get_settings
from masa_tools.qc.qc_manager import QCManager

qc_manager = QCManager()

def main(action, json_file_path=None):
    try:
        # Initialize configurations
        initialize_config()
        
        # Now we can safely get our settings
        settings = get_settings()
        
        request_manager = RequestManager()

        if action == 'process':
            qc_manager.log_debug(f"Processing requests from file: {json_file_path}", context="Main")
            request_manager.process_requests(json_file_path)
            qc_manager.log_info("Processing all requests", context="Main")
        elif action == 'request_history':
            all_requests_status = request_manager.get_all_requests_status()
            print(json.dumps(all_requests_status, indent=4))
        else:
            print("Invalid action. Allowable options are:")
            print("- 'process': Process all requests (both resumed and new)")
            print("- 'request_history': Get a history of all requests")
            sys.exit(1)
    except Exception as e:
        qc_manager.log_error(f"An error occurred during initialization: {str(e)}", context="Main")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python main.py <action> [path_to_requests_json]")
        print("Actions: 'process' or 'request_history'")
        sys.exit(1)

    action = sys.argv[1]
    json_file_path = sys.argv[2] if len(sys.argv) == 3 else None
    main(action, json_file_path)