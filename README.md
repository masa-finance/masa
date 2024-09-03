# MASA Project

MASA is a project for data retrieval, quality control, and orchestration. It currently provides tools to retrieve data from Twitter using the Masa Oracle Node API, with plans to expand to other data sources and functionalities in the future.

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
   from masa.orchestration import RequestManager

   # Initialize the RequestManager
   request_manager = RequestManager()

   # Define a request
   request = {
       "retriever": "XTwitterRetriever",
       "endpoint": "data/twitter/tweets/recent",
       "params": {
           "query": "#AI lang:en",
           "count": 100
       }
   }

   # Process the request
   request_manager.process_requests([request])
   ```

## Configuration

The project uses YAML files for configuration:

- `configs/settings.yaml`: Main configuration file containing settings for Twitter API, request management, and logging.
- `configs/.secrets.yaml`: (Optional) File for storing sensitive information like API keys. Not currently in use.

The `settings.yaml` file is loaded using Dynaconf, which allows for easy environment-based configuration management.

## Advanced Twitter Search

The Masa Oracle Node API provides advanced search capabilities for retrieving Twitter data. Some of the available search options include:

- Hashtag Search: `#hashtag`
- Mention Search: `@username`
- From User Search: `from:username`
- Keyword Exclusion: `-keyword`
- OR Operator: `term1 OR term2`
- Geo-location Based Search: `geocode:latitude,longitude,radius`
- Language-Specific Search: `lang:language_code`

For more details, refer to the [Masa Oracle Twitter Docs](https://developers.masa.ai/docs/masa-oracle/oracle-node/twitter-data#advanced-search).

## Project Structure

- `masa/`: Main package directory
  - `configs/`: Configuration files
  - `connections/`: API connection handlers
  - `masa_tools/`: Core functionality modules
    - `qc/`: Quality control tools
    - `retrieve/`: Data retrieval tools
    - `utils/`: Utility functions
  - `orchestration/`: Request management and processing

## Dependencies

Key dependencies include:

- Data processing: numpy, pandas
- API interaction: requests
- Configuration: dynaconf
- Quality control: colorlog
- Natural Language Processing: langchain, openai
- Data visualization: matplotlib, streamlit

For a full list of dependencies, refer to `environment.yml` and `requirements.txt`.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started, including documentation best practices.

## Documentation

For detailed documentation, including API reference and advanced usage, please run `python view_docs.py` from the root directory of the project. This will open the Sphinx-generated documentation in your default web browser.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
