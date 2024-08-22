from orchestration import RequestManager
from configs.config import XTwitterConfig

def main(requests_list):
    config = XTwitterConfig().get_config()
    request_manager = RequestManager(config)

    # Resume any incomplete requests from previous runs
    request_manager.resume_incomplete_requests()

    # Add new requests to the queue
    for request in requests_list:
        request_manager.add_request(request)

    # Process all requests (both resumed and new)
    request_manager.process_requests()

if __name__ == '__main__':
    requests_list = [
        {
            'retriever': 'XTwitterRetriever',
            'endpoint': 'data/twitter/tweets/recent',
            'params': {
                'query': '#KamalaHarris',
                'count': 50
            }
        },
        {
            'retriever': 'XTwitterRetriever',
            'endpoint': 'data/twitter/tweets/recent',
            'params': {
                'query': '@brendanplayford',
                'count': 50
            }
        }
    ]

    main(requests_list)