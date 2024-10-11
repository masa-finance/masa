# CHANGELOG

## Unreleased

### Breaking

* refactor!: Rename &#39;retriever&#39; to &#39;scraper&#39; and update CLI commands

- Replaced &#39;retriever&#39; with &#39;scraper&#39; across the codebase
- Renamed `XTwitterRetriever` to `XTwitterScraper`
- Updated CLI commands:
  - `masa-ai-cli --docs` is now `masa-ai-cli docs`
  - `masa-ai-cli --data` is now `masa-ai-cli data`
- Modified documentation and examples to reflect the changes

**BREAKING CHANGE**: The term &#39;retriever&#39; has been replaced with &#39;scraper&#39;, and CLI commands have been updated. Users must update their configurations and scripts to use the new class names and command syntax. ([`1c0913f`](https://github.com/masa-finance/masa/commit/1c0913fbb3f0311bb48f1f0ddb264069e7c2cd03))

### Build

* build: update release process and configuration

- Add &#39;build&#39; dependency to &#39;test-release&#39; and &#39;release&#39; targets in `Makefile`.
- Update `test-release` command to specify Test PyPI repository URL directly.
- Configure `semantic_release` with `current_version` and `branch` in `pyproject.toml`.
- Upgrade `pywin32` to version `307` in `poetry.lock`. ([`983fc8b`](https://github.com/masa-finance/masa/commit/983fc8bd5e713831bafd466201b4de00c2bb2985))

* build(makefile): Update Makefile to support PyPI and TestPyPI installations

- Remove `install` and `dev-install` targets
- Add `install-pypi` and `install-testpypi` targets in `MAKEFILE`
- Define `PYPI_REPOSITORY` and `TEST_PYPI_REPOSITORY` variables for repository management ([`6ed6635`](https://github.com/masa-finance/masa/commit/6ed6635d5259c5167436cbd726e7dba8edf50ed3))

* build: migrate project to Poetry for package management

- Replace setuptools with Poetry in `pyproject.toml`
- Update `Makefile` to use Poetry commands
- Remove obsolete files:
  - `.DS_Store`
  - Bumpversion configuration
  - `anaconda.yml`
  - `requirements.in`
- Configure `semantic-release` for automated versioning and changelog generation
- Update `README.md` and documentation with new usage instructions ([`7ce400b`](https://github.com/masa-finance/masa/commit/7ce400bdbf550c01e769540ef11f06ca1e7c0cc2))

### Chore

* chore(tests): ports validation to pytest ([`5a84d50`](https://github.com/masa-finance/masa/commit/5a84d50c86a089335fa23677e966748d207d118b))

* chore: removes requirements files, ports to poetry, migrates test to tests folder ([`730c129`](https://github.com/masa-finance/masa/commit/730c129697e9769eb1cb1213407789d3fd89f998))

* chore(env): add requirements and conda file for easy env setup ([`1e291f1`](https://github.com/masa-finance/masa/commit/1e291f10e98bf1dc929cd5bf5af96616a0f8a7d4))

* chore(docs): update doc strings ([`92494a6`](https://github.com/masa-finance/masa/commit/92494a6e3d8aed434a8fefe9c410a27b2d0159e0))

* chore: minor cleaning in config setting ([`1fad0c8`](https://github.com/masa-finance/masa/commit/1fad0c834785b4ea1c2da2173308b304eb88dcff))

* chore(deps): bump `rich` from 13.9.1 to 13.9.2 ([`a7e4d6a`](https://github.com/masa-finance/masa/commit/a7e4d6a1b25a6a5344f83049dd97861bf2242a43))

### Documentation

* docs: Improve documentation structure and content

- Modify `conf.py` in `src/masa_ai/docs/source/` to adjust Sphinx configurations
- Update `README.md` to include `logs/`, `data/`, and `examples/` directories
- Remove outdated `Contributing` and `License` sections from `README.md`
- Update `modules.rst` and `index.rst` to reflect new documentation structure ([`1441061`](https://github.com/masa-finance/masa/commit/144106181bfce00d1274379bc3b8422f9700aa03))

### Feature

* feat(tests): working validation tests ([`0986b96`](https://github.com/masa-finance/masa/commit/0986b9698cf9a3042eab3e5c6ee2355fa3d5d821))

* feat: updates validation to include created_at ([`7c5e22a`](https://github.com/masa-finance/masa/commit/7c5e22abcd300dabed0d7704f886928ce22849b3))

* feat(validator): enhance main function and improve test coverage

- Refactor main function in validator/main.py to accept command-line arguments
- Add argparse for better CLI handling
- Modify main function to return a boolean result
- Update test_validate_tweet.py to use the new main function in tests
- Improve test suite organization with a separate main function
- Enhance logging and error handling in tests ([`ba7c8fc`](https://github.com/masa-finance/masa/commit/ba7c8fc25641a4c9efa449c77a51ac690e20ee8f))

* feat(validator): Refactor and enhance TweetValidator module

- Update __init__.py to import and expose necessary modules and constants
- Refactor validate_tweet.py to use config file for constants and improve error handling
- Enhance test_validate_tweet.py with more comprehensive test cases and improved logging
- Remove redundant code and improve overall structure of the validator module

This commit improves the modularity, testability, and maintainability of the
TweetValidator functionality. ([`6f7922e`](https://github.com/masa-finance/masa/commit/6f7922e43d902c07e1192bb9bd7459f1b7b56439))

* feat(validator): implement TweetValidator class for fetching tweet data

This commit introduces a new TweetValidator class in the validate_tweet.py file,
which provides functionality to fetch and validate tweet data from Twitter&#39;s API.

Key changes:
- Add TweetValidator class with methods to:
  - Initialize a session with necessary headers
  - Obtain a guest token for authentication
  - Generate a client transaction ID
  - Fetch tweet data using the Twitter GraphQL API
- Implement error handling and logging throughout the class
- Add a main function to demonstrate usage of the TweetValidator

Technical details:
- Use requests library for HTTP operations
- Implement guest token authentication flow
- Utilize Twitter&#39;s GraphQL API endpoint for fetching tweet data
- Add comprehensive logging using the loguru library
- Include necessary headers and parameters for API requests

This implementation allows for more robust tweet validation and data retrieval,
which will be useful for various tweet-related operations in the project. ([`b77c501`](https://github.com/masa-finance/masa/commit/b77c50156ce44751b51e712b71b6118623a55203))

* feat(cli): add &#39;list-requests&#39; and &#39;clear-requests&#39; commands for request management

- Add `list-requests` command to display current requests filtered by status
- Add `clear-requests` command to cancel queued or in-progress requests by IDs
- Update `masa_ai/cli.py` with new CLI commands
- Add `list_requests` and `clear_requests` methods to `Masa` class
- Extend `RequestManager` and `StateManager` to support listing and clearing requests
- Update README and usage documentation to include new commands ([`46a4913`](https://github.com/masa-finance/masa/commit/46a4913cd71cf8ac586cf872afbb1b91a00002b8))

* feat(cli): enhance &#39;process&#39; command to accept various input types

- The `process` command now accepts input as a JSON file path, JSON string, list of requests, or a single request.
- Improved input parsing logic to handle different input types.
- Added colored output messages using `click.style` for improved user experience.
- Enhanced logging in CLI commands using `masa.qc_manager` for better traceability. ([`a823ff4`](https://github.com/masa-finance/masa/commit/a823ff4571a6a631a31f8e217d3745b583b3808c))

* feat(cli): refactor CLI using Click and add config management commands

- Refactored the CLI to use Click for improved command handling and readability.
- Added new `config` subcommands: `config get &lt;key&gt;` and `config set &lt;key&gt; &lt;value&gt;` for managing configuration in `settings.yaml`.
- Updated existing commands (`process`, `docs`, `data`) to align with Click&#39;s command structure.
- Modified `Masa` class to include `get_config` and `set_config` methods for configuration management.
- Updated `README.md` and documentation to reflect the new CLI commands and usage examples. ([`02d6794`](https://github.com/masa-finance/masa/commit/02d6794c61abadb8a2873a21f651cb7a6397cfa3))

* feat(data-storage): add filename sanitization and make data directory configurable

- data is now stored in the current working directory but can be configured to be pinned to a particular location by adding a DATA_DIRECTORY in settings.yml.  It should be able to handle absolute or relative paths.
- Added a `sanitize_filename` method to the `DataStorage` class to ensure filenames are safe and compliant across different file systems.
- Updated data directory handling to use `global_settings.data_storage.DATA_DIRECTORY`, allowing users to specify custom data directories via settings.
- Removed hardcoded data directory paths from `constants.py` and updated references in other modules to use the new configurable settings.

This improves flexibility in specifying data storage locations and enhances file safety when saving data. ([`8bb838e`](https://github.com/masa-finance/masa/commit/8bb838e10630f70811e8b00b4eb4cb1bb493e9ae))

### Fix

* fix: logging cleanup ([`71dc52c`](https://github.com/masa-finance/masa/commit/71dc52c0c4be63bff51e4924a4633e8d371c3783))

* fix: logging and cleanup! ([`e50161a`](https://github.com/masa-finance/masa/commit/e50161ac12e10b3b0a2d468399afa5c2a1a11793))

* fix: formats created at correctly, from date string to timestamp in seconds ([`d4feb50`](https://github.com/masa-finance/masa/commit/d4feb50f75c5f4b34b99d94b93a669f0a4941264))

* fix: adds make test-validation command for ease and simplifies logs ([`39c0205`](https://github.com/masa-finance/masa/commit/39c0205ff8b83573c8960b34d5bd30b0de991896))

* fix(test): adds correct args ([`dcbb185`](https://github.com/masa-finance/masa/commit/dcbb185599a586c4c2b5cc41c159d0107d4a9283))

* fix(dependencies): Downgrade Sphinx and NumPy versions for compatibility

- Set `sphinx` version to `&lt;8.0.0` in `pyproject.toml`
- Set `numpy` version to `&lt;2.0.0` in `pyproject.toml`
- Update `poetry.lock` to reflect the version changes ([`8638427`](https://github.com/masa-finance/masa/commit/8638427e510a466b2c8f644e44e37b3877cad365))

### Refactor

* refactor(core): update &#39;process_requests&#39; methods to handle diverse inputs

- Modified `process_requests` in `masa.py` to accept various input types and handle them accordingly.
- Updated `RequestManager.process_requests` to accept a list of requests instead of a file path.
- Refactored methods to read requests from variables rather than files. ([`5f25d73`](https://github.com/masa-finance/masa/commit/5f25d738539a146942ec41c5360f940ef6cf6ed6))

