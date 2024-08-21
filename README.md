# MASA Project

MASA is a project for data retrieval, structuring, augmentation, and quality control. It provides tools to retrieve data from various sources, including Twitter, and perform advanced searches using the Masa Oracle Node API.

## Quick Start

1. Install the project:

   ```bash
   masa-init
   ```

2. Activate the environment:

   ```bash
   conda activate masa
   ```

3. Basic usage example:

   ```python
   from masa_tools.retrieve.retrieve_xtwitter import XTwitterRetriever
   from masa_tools.qc.logging import Logger
   from masa_tools.qc.error_handler import ErrorHandler
   from configs.config import XTwitterConfig

   def main(requests_list):
       logger = Logger(__name__)
       error_handler = ErrorHandler(logger)
       config = XTwitterConfig().get_config()

       retriever = XTwitterRetriever(logger, error_handler, config)

       for request in requests_list:
           if request['endpoint'] == '/data/tweets':
               retriever.retrieve_tweets(request['params'])

   if __name__ == '__main__':
       requests_list = [
           {
               'endpoint': '/data/tweets',
               'params': {
                   'query': '#Bitcoin',
                   'count': 10
               }
           },
           {
               'endpoint': '/data/tweets',
               'params': {
                   'query': '@brendanplayford',
                   'count': 20
               }
           }
       ]

       main(requests_list)
   ```

## Advanced Twitter Search

The Masa Oracle Node API provides advanced search capabilities for retrieving Twitter data. Some of the available search options include:

- Hashtag Search: Search for tweets containing specific hashtags using the syntax `#hashtag`.
- Mention Search: Search for tweets mentioning a specific user using the syntax `@username`.
- From User Search: Search for tweets posted by a specific user using the syntax `from:username`.
- Keyword Exclusion: Exclude tweets with certain keywords using the syntax `-keyword`.
- OR Operator: Combine multiple terms, where at least one must be present, using the syntax `term1 OR term2`.
- Geo-location Based Search: Search for tweets by users located within a certain radius of a given latitude and longitude using the syntax `geocode:latitude,longitude,radius`.
- Language-Specific Search: Search for tweets in a specific language using the syntax `lang:language_code`.

For more details on the available search options, refer to the [Masa Oracle Twitter Docs](https://developers.masa.ai/docs/masa-oracle/oracle-node/twitter-data#advanced-search).

## Documentation

For detailed documentation, including installation instructions, usage guide, and API reference, please visit our [full documentation](link-to-your-hosted-sphinx-docs).

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started, including documentation best practices.

## Configuration Files

- `setup.py`: Package details and dependencies
- `init_script.py`: Initialization script
- `environment.yml`: Conda environment definition
- `requirements.txt`: Additional Python packages

## Additional Information

For more detailed information about setup, configuration, and usage, please refer to our [full documentation](link-to-your-hosted-sphinx-docs).