# Masa Project

Masa is a project for data retrieval, quality control, and orchestration. It currently provides tools to retrieve data from Twitter using the Masa Oracle Node API, with plans to expand to other data sources and functionalities in the future.

## Quick Start

1. Install the Masa package:

   ```bash
   pip install masa
   ```

2. Use the MASA CLI:

   ```bash
   masa-cli <action> [arguments]
   ```

   Available actions:
   - `process [path_to_requests_json]`: Process all requests (both resumed and new)
   - `--docs [page_name]`: Rebuild and view the documentation for the specified page
   - `--data`: List the scraped data files

   For example:

   ```bash
   masa-cli process /path/to/request_list.json
   masa-cli --docs usage
   masa-cli --data
   ```

3. For detailed usage instructions, please refer to the [Usage Guide](usage.rst).

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

For more details, refer to the [Masa Oracle Twitter Docs](xtwitter_advanced.rst).

## Project Structure

- `masa/`: Main package directory
  - `configs/`: Configuration files
  - `connections/`: API connection handlers
  - `tools/`: Core functionality modules
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

For a full list of dependencies, refer to `pyproject.toml`.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started, including documentation best practices.

## Documentation

The Masa project uses Sphinx to generate its documentation. The documentation is automatically rebuilt and viewed when using the `--docs` option with the `masa-cli` command.

To view the documentation:

```bash
masa-cli --docs [page_name]
```

This command will rebuild and view the documentation for the specified page.

## License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
