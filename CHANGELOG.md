# CHANGELOG

## Unreleased

### Breaking

* refactor!: Rename 'retriever' to 'scraper' and update CLI commands

- Replaced 'retriever' with 'scraper' across the codebase
- Renamed `XTwitterRetriever` to `XTwitterScraper`
- Updated CLI commands:
  - `masa-ai-cli --docs` is now `masa-ai-cli docs`
  - `masa-ai-cli --data` is now `masa-ai-cli data`
- Modified documentation and examples to reflect the changes

**BREAKING CHANGE**: The term 'retriever' has been replaced with 'scraper', and CLI commands have been updated. Users must update their configurations and scripts to use the new class names and command syntax. ([`1c0913f`](https://github.com/masa-finance/masa/commit/1c0913fbb3f0311bb48f1f0ddb264069e7c2cd03))

### Build System

* build: update release process and configuration

- Add 'build' dependency to 'test-release' and 'release' targets in `Makefile`.
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

### Chores

* chore(deps): update debugpy to 1.8.7, numpy to 2.1.2, and python-semantic-release to 9.10.1

- **Dependencies:**
  - Updated `debugpy` from `1.8.6` to `1.8.7`.
  - Updated `numpy` from `1.26.4` to `2.1.2`.
  - Updated `python-semantic-release` from `9.10.0` to `9.10.1`.
  - Changed `numpy` dependency in `pyproject.toml` to `>=2.0.1`.

- **Configuration:**
  - Modified query parameters in `src/masa_ai/examples/request_list.json`:
    - Changed `#EPL` to `#theoffice`.
    - Changed `@elonmusk` to `@jakegyllenhaal`.
    - Changed `#COYS` to `#football`.

- **Code Enhancements:**
  - In `src/masa_ai/masa.py`, updated the `Masa` class to include additional request statuses:
    - Added `completed`, `failed`, and `cancelled` to the statuses list. ([`1d17a5b`](https://github.com/masa-finance/masa/commit/1d17a5b41b3472ee10e1339216e14eb6c11e7693))

* chore(version): updates version ([`d62b649`](https://github.com/masa-finance/masa/commit/d62b64957e1421a29d6ab524c60df84ea4f83637))

* chore(release): release version 0.2.2

- Bumped version to `0.2.2` in `pyproject.toml` and `src/masa_ai/__init__.py` ([`e158984`](https://github.com/masa-finance/masa/commit/e158984a7c426c2894c3e2769debf0e35dad0933))

* chore(release): release version 0.2.1

- Updated `CHANGELOG.md` with recent changes, including features, fixes, chores, and documentation updates.
- Bumped version to `0.2.1` in `pyproject.toml` and `src/masa_ai/__init__.py`. ([`e5dc6cf`](https://github.com/masa-finance/masa/commit/e5dc6cf3d3a401f5a38187b449a6a7a4f871cc7a))

* chore: updated version, pyproject.toml, changelog ([`f00f51b`](https://github.com/masa-finance/masa/commit/f00f51b61b35bdbc339d70de103422d364ec1729))

* chore(tests): ports validation to pytest ([`5a84d50`](https://github.com/masa-finance/masa/commit/5a84d50c86a089335fa23677e966748d207d118b))

* chore: removes requirements files, ports to poetry, migrates test to tests folder ([`730c129`](https://github.com/masa-finance/masa/commit/730c129697e9769eb1cb1213407789d3fd89f998))

* chore(env): add requirements and conda file for easy env setup ([`1e291f1`](https://github.com/masa-finance/masa/commit/1e291f10e98bf1dc929cd5bf5af96616a0f8a7d4))

* chore(docs): update doc strings ([`92494a6`](https://github.com/masa-finance/masa/commit/92494a6e3d8aed434a8fefe9c410a27b2d0159e0))

* chore: minor cleaning in config setting ([`1fad0c8`](https://github.com/masa-finance/masa/commit/1fad0c834785b4ea1c2da2173308b304eb88dcff))

* chore(deps): bump `rich` from 13.9.1 to 13.9.2 ([`a7e4d6a`](https://github.com/masa-finance/masa/commit/a7e4d6a1b25a6a5344f83049dd97861bf2242a43))

### Documentation

* docs: updated validator docs ([`58725f2`](https://github.com/masa-finance/masa/commit/58725f25543961aed792da565a02245d569b3df0))

* docs: updated docs to reflect new validator module ([`3828aff`](https://github.com/masa-finance/masa/commit/3828aff4408ed188cba510f745c8c454aa9f1901))

* docs: Improve documentation structure and content

- Modify `conf.py` in `src/masa_ai/docs/source/` to adjust Sphinx configurations
- Update `README.md` to include `logs/`, `data/`, and `examples/` directories
- Remove outdated `Contributing` and `License` sections from `README.md`
- Update `modules.rst` and `index.rst` to reflect new documentation structure ([`1441061`](https://github.com/masa-finance/masa/commit/144106181bfce00d1274379bc3b8422f9700aa03))

### Features

* feat: adds hashtags to validation ([`03e6a39`](https://github.com/masa-finance/masa/commit/03e6a396186886289d227bb84841fd3f96820e27))

* feat: adds text validation and additional testing ([`c113f43`](https://github.com/masa-finance/masa/commit/c113f4323f84563262aa071db7be9336f29bd1fa))

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
which provides functionality to fetch and validate tweet data from Twitter's API.

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
- Utilize Twitter's GraphQL API endpoint for fetching tweet data
- Add comprehensive logging using the loguru library
- Include necessary headers and parameters for API requests

This implementation allows for more robust tweet validation and data retrieval,
which will be useful for various tweet-related operations in the project. ([`b77c501`](https://github.com/masa-finance/masa/commit/b77c50156ce44751b51e712b71b6118623a55203))

* feat(cli): add 'list-requests' and 'clear-requests' commands for request management

- Add `list-requests` command to display current requests filtered by status
- Add `clear-requests` command to cancel queued or in-progress requests by IDs
- Update `masa_ai/cli.py` with new CLI commands
- Add `list_requests` and `clear_requests` methods to `Masa` class
- Extend `RequestManager` and `StateManager` to support listing and clearing requests
- Update README and usage documentation to include new commands ([`46a4913`](https://github.com/masa-finance/masa/commit/46a4913cd71cf8ac586cf872afbb1b91a00002b8))

* feat(cli): enhance 'process' command to accept various input types

- The `process` command now accepts input as a JSON file path, JSON string, list of requests, or a single request.
- Improved input parsing logic to handle different input types.
- Added colored output messages using `click.style` for improved user experience.
- Enhanced logging in CLI commands using `masa.qc_manager` for better traceability. ([`a823ff4`](https://github.com/masa-finance/masa/commit/a823ff4571a6a631a31f8e217d3745b583b3808c))

* feat(cli): refactor CLI using Click and add config management commands

- Refactored the CLI to use Click for improved command handling and readability.
- Added new `config` subcommands: `config get <key>` and `config set <key> <value>` for managing configuration in `settings.yaml`.
- Updated existing commands (`process`, `docs`, `data`) to align with Click's command structure.
- Modified `Masa` class to include `get_config` and `set_config` methods for configuration management.
- Updated `README.md` and documentation to reflect the new CLI commands and usage examples. ([`02d6794`](https://github.com/masa-finance/masa/commit/02d6794c61abadb8a2873a21f651cb7a6397cfa3))

* feat(data-storage): add filename sanitization and make data directory configurable

- data is now stored in the current working directory but can be configured to be pinned to a particular location by adding a DATA_DIRECTORY in settings.yml.  It should be able to handle absolute or relative paths.
- Added a `sanitize_filename` method to the `DataStorage` class to ensure filenames are safe and compliant across different file systems.
- Updated data directory handling to use `global_settings.data_storage.DATA_DIRECTORY`, allowing users to specify custom data directories via settings.
- Removed hardcoded data directory paths from `constants.py` and updated references in other modules to use the new configurable settings.

This improves flexibility in specifying data storage locations and enhances file safety when saving data. ([`8bb838e`](https://github.com/masa-finance/masa/commit/8bb838e10630f70811e8b00b4eb4cb1bb493e9ae))

### Fixes

* fix: adds name ([`9e41174`](https://github.com/masa-finance/masa/commit/9e41174f78efd7bfc8bd22ae909275b4d6aa4d7f))

* fix: success message ([`6197fdb`](https://github.com/masa-finance/masa/commit/6197fdbe3ac549d0266e2aa4a707796bcd3b255d))

* fix: validator import ([`5b212c1`](https://github.com/masa-finance/masa/commit/5b212c14234a6a520e2dfd48b4b3ae961a9f6c1a))

* fix: logging cleanup ([`71dc52c`](https://github.com/masa-finance/masa/commit/71dc52c0c4be63bff51e4924a4633e8d371c3783))

* fix: logging and cleanup! ([`e50161a`](https://github.com/masa-finance/masa/commit/e50161ac12e10b3b0a2d468399afa5c2a1a11793))

* fix: formats created at correctly, from date string to timestamp in seconds ([`d4feb50`](https://github.com/masa-finance/masa/commit/d4feb50f75c5f4b34b99d94b93a669f0a4941264))

* fix: adds make test-validation command for ease and simplifies logs ([`39c0205`](https://github.com/masa-finance/masa/commit/39c0205ff8b83573c8960b34d5bd30b0de991896))

* fix(test): adds correct args ([`dcbb185`](https://github.com/masa-finance/masa/commit/dcbb185599a586c4c2b5cc41c159d0107d4a9283))

* fix(dependencies): Downgrade Sphinx and NumPy versions for compatibility

- Set `sphinx` version to `<8.0.0` in `pyproject.toml`
- Set `numpy` version to `<2.0.0` in `pyproject.toml`
- Update `poetry.lock` to reflect the version changes ([`8638427`](https://github.com/masa-finance/masa/commit/8638427e510a466b2c8f644e44e37b3877cad365))

### Refactoring

* refactor(core): update 'process_requests' methods to handle diverse inputs

- Modified `process_requests` in `masa.py` to accept various input types and handle them accordingly.
- Updated `RequestManager.process_requests` to accept a list of requests instead of a file path.
- Refactored methods to read requests from variables rather than files. ([`5f25d73`](https://github.com/masa-finance/masa/commit/5f25d738539a146942ec41c5360f940ef6cf6ed6))

### Unknown

* Merge pull request #11 from masa-finance/feat--hashtags-validation

feat: hashtag validation ([`84b8565`](https://github.com/masa-finance/masa/commit/84b85657d2a24a2a6a1334918801bbc01bba371b))

* Merge branch 'main' into feat--hashtags-validation ([`4a4f2bd`](https://github.com/masa-finance/masa/commit/4a4f2bda309b24de7db5359fd516a37be81e21a9))

* Merge pull request #10 from masa-finance/fix--text-validation

feat: adds text validation and additional testing ([`b664086`](https://github.com/masa-finance/masa/commit/b664086d9a5f184eb33ee1e441ae87885793e1b7))

* Merge pull request #9 from masa-finance/fix--imports-for-validator

fix: validator import ([`f8158fe`](https://github.com/masa-finance/masa/commit/f8158fe59ddcf8e41a37f8956e6c3b9ef5ad27cc))

* Merge pull request #8 from masa-finance/dev

Merging Dev to Main for Release ([`ffc881a`](https://github.com/masa-finance/masa/commit/ffc881a3c1b872f3f70ce3b1502db4d5cf7bd5ae))

* Merge branch 'main' into dev ([`9c086fa`](https://github.com/masa-finance/masa/commit/9c086fa9909bb3db23be9bfeccf2ece4a1d498ac))

* Rename MAKEFILE to Makefile ([`ec319bd`](https://github.com/masa-finance/masa/commit/ec319bd38fe02ab23d20c4973e23d99a10e5abaf))

* Merge pull request #6 from masa-finance/dev

SDK: Quality of Life Improvements ([`013ea3c`](https://github.com/masa-finance/masa/commit/013ea3cffb7f294f9c953812491a1e6ed4a357b2))

* Merge pull request #7 from masa-finance/faet-twitter-post-scraper-tweet-validator

feat(validator): Implement Tweet Validation Tool ([`9aa0c03`](https://github.com/masa-finance/masa/commit/9aa0c038df102821709c7bcb1b142f0fb12c7fdf))

* Create README.md ([`105e1cd`](https://github.com/masa-finance/masa/commit/105e1cd40dff0354195ea130a2cea24b7fc9adbc))

* Merge pull request #5 from masa-finance/chore/naming_conventions_and_other_cleanup

Chore/naming conventions and other cleanup (default data storage, cli usage, filename sanitization) ([`a5dcf92`](https://github.com/masa-finance/masa/commit/a5dcf92bf8297db4fe3043d2da2f06e2ec5d489a))

* Merge pull request #4 from masa-finance/feat/poetry-implementation

Feat/poetry implementation ([`7cf27d3`](https://github.com/masa-finance/masa/commit/7cf27d31b03cc1d05927729d85a814fe03872a2d))


## v0.1.2 (2024-09-26)

### Unknown

* Bump version: 0.1.1 → 0.1.2 ([`98c7f48`](https://github.com/masa-finance/masa/commit/98c7f4870114aeeb161c655a1ebd1193a84e69f1))

* Bump version: 0.1.0 → 0.1.1 and fixed some naming ([`7078c05`](https://github.com/masa-finance/masa/commit/7078c050bd81c8efa0ebcbc960169fc0541658d7))


## v0.1.1 (2024-09-25)

### Chores

* chore: modified name format psycopg[binary]

updated version for pypi ([`dcb331e`](https://github.com/masa-finance/masa/commit/dcb331ebb19e13c3b329753e7a24258b074a20ae))

* chore: updated bumpversion config to new path ([`42faa67`](https://github.com/masa-finance/masa/commit/42faa670cc9a7d3ddbd0d983cd016b86966313b0))

* chore: updated bump version ([`843f4af`](https://github.com/masa-finance/masa/commit/843f4af7cd735cea71319d34835916d529a01e9a))

* chore: added instructions for dependency modification ([`2ec3333`](https://github.com/masa-finance/masa/commit/2ec33335477c9c68d04d78f5c4b07e2369390115))

* chore: refactored project to accomodate name change to masa-ai ([`c6c82c3`](https://github.com/masa-finance/masa/commit/c6c82c34a07695fd68c15376754e45ceb9f18fcf))

### Documentation

* docs: fixed naming issue ([`86f23b1`](https://github.com/masa-finance/masa/commit/86f23b1dd00354ae77d8e337315f188992668cd5))

* docs: update README.md and init.py ([`ed80cea`](https://github.com/masa-finance/masa/commit/ed80cea4eb7d90ec8b1c79c71e3d91925742f75d))

* docs: format change ([`21aa41e`](https://github.com/masa-finance/masa/commit/21aa41eaa9f629aebf050c9ab4f188b61050bee0))

### Unknown

* Bump version: 0.1.0 → 0.1.1 ([`31a8f29`](https://github.com/masa-finance/masa/commit/31a8f2949ae21638e4b1b9fbd2db1160f6b70978))

* Bump version: 0.1.0 → 0.1.1 ([`c02306a`](https://github.com/masa-finance/masa/commit/c02306a3727d9670fd7e5d06428b079542614cf2))

* Merge pull request #2 from masa-finance/dependency_fix

chore: added instructions for dependency modification ([`5344336`](https://github.com/masa-finance/masa/commit/5344336dd6759118ba4369fdbe0933bef3f753a8))

* Update .gitignore to reflect new directory structure

- Updated paths from `src/masa/` to `src/masa_ai/` to match the new directory structure.
- Ensured all files and subdirectories within `src/masa_ai/data/` are ignored.
- Added rules to ignore `.duckdb` files and `.cursorrules`.
- Consolidated and removed duplicate entries for `src/masa_ai.egg-info/` and `.DS_Store`. ([`5d60619`](https://github.com/masa-finance/masa/commit/5d60619ae012ea3edd4d60fa8441107a020c8dad))

* updated .gitignore to exclude data and state files ([`b8ac8e0`](https://github.com/masa-finance/masa/commit/b8ac8e0cab358bd273b3edfd025bad6e73a9a448))

* Update version number for PyPI release ([`5fb50c7`](https://github.com/masa-finance/masa/commit/5fb50c7512c973cd819e4a531eb9c42a3da6e602))

* Merge pull request #1 from masa-finance/feat/v0.1

v0.1.0 - Masa SDK Foundation ([`4186c0a`](https://github.com/masa-finance/masa/commit/4186c0a5e9f37937e09f2fc27e832f0fdfbaad95))


## v0.1.25 (2024-09-16)

### Documentation

* docs: Updated readme

Added more precise information about using the package in it's current state. ([`2a97009`](https://github.com/masa-finance/masa/commit/2a97009a367d8cc2e315230d0fa3a9c472521325))

### Unknown

* Bump version: 0.1.24 → 0.1.25 ([`1049050`](https://github.com/masa-finance/masa/commit/1049050e449ef30f0a70ee2b4be3df699bf33cb4))


## v0.1.24 (2024-09-16)

### Unknown

* Bump version: 0.1.23 → 0.1.24 ([`d11679d`](https://github.com/masa-finance/masa/commit/d11679d4bbb6ea59e506b69b0dee8f623ac7706a))


## v0.1.23 (2024-09-16)

### Unknown

* Bump version: 0.1.22 → 0.1.23 ([`6545d14`](https://github.com/masa-finance/masa/commit/6545d14c73d33630d8faa252f45cff28a585af29))


## v0.1.22 (2024-09-16)

### Chores

* chore: Modified .gitignore ([`27a8215`](https://github.com/masa-finance/masa/commit/27a8215dcc087b14db130ce22ddd6e397d0efa12))

### Unknown

* Bump version: 0.1.21 → 0.1.22 ([`06792aa`](https://github.com/masa-finance/masa/commit/06792aa88d3e5daef539a5f84862b4d20e5de197))

* removed egg files from github cache ([`089b8a0`](https://github.com/masa-finance/masa/commit/089b8a0290c45b19d714b8aaa293d26d8584209e))


## v0.1.21 (2024-09-13)

### Documentation

* docs: modified docs location and scripts for whl ([`6b46191`](https://github.com/masa-finance/masa/commit/6b46191b02bfa73978cf3378f23c88e7c223f0bd))

### Unknown

* Bump version: 0.1.20 → 0.1.21 ([`04986d4`](https://github.com/masa-finance/masa/commit/04986d49e508c571b318937e5b4ab474690db362))


## v0.1.20 (2024-09-13)

### Documentation

* docs: moved docs into package

This will allow them to be included in .whl and accessed locally. ([`41baad9`](https://github.com/masa-finance/masa/commit/41baad9f9908c56334c802a54e689a284c6db2af))

### Unknown

* Bump version: 0.1.19 → 0.1.20 ([`245bdf6`](https://github.com/masa-finance/masa/commit/245bdf6528ded145ee460dd7b4d1f22f0a3e43b2))


## v0.1.19 (2024-09-13)

### Documentation

* docs: add docs to final pkg ([`1df308c`](https://github.com/masa-finance/masa/commit/1df308c8d6487409060c003445c3e6e782d8cdd8))

### Unknown

* Bump version: 0.1.18 → 0.1.19 ([`6fe7098`](https://github.com/masa-finance/masa/commit/6fe70985f016080d168bceafc9f805c21c8f01d1))


## v0.1.18 (2024-09-13)

### Chores

* chore: Refactor project structure

- Update project metadata in pyproject.toml
- Clean up .gitignore
- restructured project to comply with PyPI standards ([`5fdc42a`](https://github.com/masa-finance/masa/commit/5fdc42afe27d59160465a56f0ee746ff864077c2))

* chore: refactor codebase for pypi upload ([`3ce4b23`](https://github.com/masa-finance/masa/commit/3ce4b23c99d3ed774b9c1fec9472c399ca050610))

* chore: renamed init_script to quickstart, updated readme ([`dc3ade0`](https://github.com/masa-finance/masa/commit/dc3ade07153131e7c03c68abb3a84f411d158de7))

### Documentation

* docs: bump version and update documentation

added automatic version bump for specific make commands and fixed docs for initial release. ([`381e931`](https://github.com/masa-finance/masa/commit/381e931e3e8cf2101b9a2f53f61db3c1e4afd98c))

* docs: Update documentation

Update CONTRIBUTING.md with new command for updating docs
Update README.md with:
Revised quickstart instructions
Fixed links to contributing guidelines and license
Regenerate distribution files (wheel and tar.gz)
Update masa.egg-info with revised files
Simplify docs index.rst
Fix relative path in docs readme.rst ([`66a9631`](https://github.com/masa-finance/masa/commit/66a9631a21e2deadc14e65d1e8254609c0241b20))

* docs: updated docs throughout codebase

Docs should comply with Sphinx standards ([`e028e7d`](https://github.com/masa-finance/masa/commit/e028e7d7d4d342660fd26364664ffb4932aadc37))

* docs: add docs action comment ([`41ba307`](https://github.com/masa-finance/masa/commit/41ba30779d95338ce7f35bbdc26c80d5600478ea))

* docs: Enhance documentation and add CLI for viewing docs

The commit enhances the project's documentation and adds new features:
Update README.md to refer to the new Usage Guide in the docs
Expand docs/source/usage.rst with detailed instructions on:
Command line usage of the main script
Request format and examples
Handling of timeframes in XTwitterRetriever
Request processing flow
Retrieving request history
Modify main.py to support a new '--docs' action for viewing documentation
Allows specifying a specific page or defaulting to index.html
Runs view_docs.py script to open the docs in a web browser
Update view_docs.py to accept a page argument and handle cases when docs are not built
Minor update to orchestration/request_manager_state.json (progress tracking)
The changes aim to improve the user's understanding of the project's usage and make the documentation more accessible through the command line interface. ([`1a3b1e3`](https://github.com/masa-finance/masa/commit/1a3b1e3364481bccd1c22407230e11a57f8a67db))

* docs: clean-up, styling, generation ([`e709711`](https://github.com/masa-finance/masa/commit/e709711c75f6613c8c349eb525f7f922ffd8380d))

* docs:  added sphinx docs for codebase ([`0e5c6a5`](https://github.com/masa-finance/masa/commit/0e5c6a532c8cc7dd4dfc1bc42e0b5706c4634e2c))

### Features

* feat: Refactored project structure and updated documentation

- Added 'notebooks' to .gitignore
- Updated installation instructions and added new CLI actions
- Improved documentation build process and contributing guidelines
- Removed outdated distribution files and metadata
- Updated project version to 0.1.11 and dependencies
- Refactored modules for better organization and import paths
- Updated configuration settings and file paths
- Removed unnecessary documentation files
- Added functionality to MASA module for processing requests and viewing docs
- Improved error handling, logging, and file path handling
- Refactored tools package and removed unnecessary modules
- Updated Twitter API request parameters in request_list.json ([`a859dff`](https://github.com/masa-finance/masa/commit/a859dff703261f3844d9b1b7abf73ca284572d6f))

* feat: Enhance quickstart and logging setup for documentation building

Changes:
Update quickstart.py:
Add check for Anaconda installation before proceeding with setup
Improve docstrings and type hints for functions
Enhance output messages for clarity
Update logging_config.py:
Add handling for documentation building environment
Use NullHandler when building docs to avoid generating log files
Ensure log directory exists before creating file handler
Update QCManager and XTwitterRetriever docstrings:
Specify full import paths for type hints in docstrings
Add environment variable 'BUILDING_DOCS' in conf.py
Remove update_docs.py and open_docs.py scripts ([`88a7c45`](https://github.com/masa-finance/masa/commit/88a7c455b580fa7b2e32beff82285e362375d744))

* feat: enhance request processing and error handling

Summary of changes:
Added inline comments and improved logging throughout the codebase for better traceability and debugging
Refactored RequestManager to load state first, then update with new requests from file, and finally initialize the queue
Updated Queue to load active requests from state manager instead of all requests
Improved error handling in RequestRouter and added validation for missing request ID and parameters
Refactored StateManager to lazy load state and added methods to retrieve active requests and check if a request exists
Updated request_list.json with new date ranges for testing
Enhanced XTwitterRetriever to handle date ranges more robustly, respect DEFAULT_TIMEFRAME_MONTHS setting, and process requests day by day ([`6a02740`](https://github.com/masa-finance/masa/commit/6a02740779655444b2eddcb150d7fc2153dbdd28))

* feat: Enhance XTwitter retrieval and error handling

- Update XTwitter base URL in settings to point to a specific IP address
- Add success wait time configuration for XTwitter connection
- Modify tweet retrieval queries in request list to have shorter date ranges
- Refactor error handling:
  - Add custom error handlers support in QCManager and ErrorHandler
  - Simplify error handling decorators
  - Remove success wait time handling from RetryPolicy (moved to XTwitterConnection)
- Enhance logging in XTwitterRetriever:
  - Add more debug logging for better visibility into the retrieval process
  - Log API response content for debugging
  - Wrap key methods with error handling decorator
- Add pause after each successful API call in XTwitterConnection
- Add inline comments to explain the purpose of code changes

These enhancements improve the robustness and observability of the XTwitter retrieval process. The retrieval queries are adjusted to have shorter date ranges per request. Error handling is simplified and allows for custom exception handlers. Logging is improved to aid in debugging and monitoring. A pause is added after each successful API call to avoid hitting rate limits. ([`492b642`](https://github.com/masa-finance/masa/commit/492b642c546744b2e7e4f2a8b5d7ef9cdf273bb4))

* feat: Refactor queue management and improve logging

- Load queue from state on initialization and clear old queue file
- Update request state to 'queued' when adding to queue
- Prevent duplicate requests from being added to the queue
- Add method to get summary of current queue with request details
- Log queue summary at start of request processing
- Remove status checks when adding requests, rely on queue to handle
- Add method to get all requests state from StateManager
- Pass request ID to retriever for logging ([`7d8f127`](https://github.com/masa-finance/masa/commit/7d8f127837f54b8993e1f261c679573bbe08f583))

* feat: Refactor queue loading to avoid duplicates and improve logging

- Split queue loading into separate methods for state and file
- When loading from file, check if request is already in queue to avoid duplicates
- Directly add to memory queue when loading from state instead of calling add()
- Improve logging messages and levels for queue loading
- Log total requests in queue after loading is complete ([`2f3f697`](https://github.com/masa-finance/masa/commit/2f3f697067417c3670f5d09208124b90946cc45c))

* feat: enhance logging and state tracking

- Update .gitignore to ignore logs directory and rename state file
- Log full request details in state manager on completion or failure
- Refactor get_all_requests_status to use stored request details
- Add inline comments to document key changes ([`813d5e7`](https://github.com/masa-finance/masa/commit/813d5e7ba5406f45db9f613957c388aae4a3a40c))

* feat: Enhance logging configuration and output

- Update logging settings in configs/settings.yaml to include:
  - Colored log output
  - Separate log levels for console and file handlers
- Implement logging_config module (tools/qc/logging_config.py):
  - Set up loggers based on global settings
  - Add console and file handlers with configurable log levels and formatting
- Improve logging in request_manager and retrieve_xtwitter modules:
  - Log more informative messages at appropriate levels
  - Include request progress percentage in tweets retrieval
  - Optimize tweet response handling and state updates
- Update request manager state file with latest progress timestamp

These changes enhance the logging capabilities by allowing configurable log settings,
providing more useful log output, and optimizing the logging in key modules. The colored
console output and separate log levels for console/file improve readability and flexibility. ([`ddfbcea`](https://github.com/masa-finance/masa/commit/ddfbcead5c96d1e3380c8a473028a7f449b35712))

* feat: Add date range support and default timeframe for Twitter queries

- Added DEFAULT_TIMEFRAME_MONTHS setting to specify default query timeframe
- Updated request_manager_state.json with new requests containing date ranges
- Modified request_list.json to include since and until dates in queries
- Implemented _extract_date_range method in XTwitterRetriever to parse date range from query
-If no date range provided, use default timeframe from DEFAULT_TIMEFRAME_MONTHS setting
- Clean up the query by removing the extracted date range parameters
- Update progress tracking to use extracted date range ([`fb47b29`](https://github.com/masa-finance/masa/commit/fb47b29f21c2d277c36056934f5aab2a0f636b50))

* feat: Enhance documentation, error handling, and request management

Documentation:
- Update README with instructions to view Sphinx docs locally
- Improve module documentation in Sphinx docs
- Add new modules to Sphinx docs TOC

Error Handling:
- Use QCManager's error handling decorator in XTwitterConnection
- Add success handling in RetryPolicy
- Remove redundant error handling from XTwitterRetriever

Request Management:
- Add new requests to request_list.json
- Update request_manager_state.json with new requests
- Simplify tweet retrieval process in XTwitterRetriever
- Initialize retrievers using get_retriever method in RequestRouter

Code Cleanup:
- Update relative imports in Sphinx docs
- Remove unused imports and variables
- Add type hints for QCManager in docstrings ([`d2fca2c`](https://github.com/masa-finance/masa/commit/d2fca2cf31d807a68b4741a9cd292b8e1af156f7))

* feat: Enhance retry logic, error handling, and queue persistence

- Update settings to remove unnecessary comments
- Add RateLimitException to handle rate limiting errors
- Improve error handling and logging in API connections
- Refactor RetryPolicy for better readability and fix off-by-one issues
- Use tqdm.auto instead of tqdm for better notebook compatibility
- Add more detailed logging in XTwitterRetriever
- Implement queue persistence using a JSON file
  - Load queue from file on initialization
  - Save queue to file after each modification
- Store request details in state instead of original request
- Improve request processing flow in RequestManager
- Fix minor typos and improve code comments

The changes focus on enhancing the retry logic to handle rate limiting
and other API errors more effectively. The QCManager is used to log
warnings and errors with appropriate context.

The Queue class is updated to persist its state using a JSON file. This
ensures that the queue can be restored even if the application restarts.

The RequestManager processing flow is streamlined, and the StateManager
is updated to store request details instead of the original request.

Additional logging statements and code comments are added to improve
overall code clarity and maintainability. ([`569710a`](https://github.com/masa-finance/masa/commit/569710a75c628d832f122751f7533f1b83047044))

* feat: playing with the retry manager and error propagation ([`e785348`](https://github.com/masa-finance/masa/commit/e785348b9630a039846003d0b39c71d12cfefbf0))

* feat: fully refactored for separation of concerns

Function, working out catching 429s ([`abddf05`](https://github.com/masa-finance/masa/commit/abddf05077b8270f3c87eb118beb19d966c8d85b))

* feat: refactored config, error handling, and logging

and changed the codebase to accomodate those changes ([`072fb03`](https://github.com/masa-finance/masa/commit/072fb0326f09ca1e24eafa4fddf92a759291f3aa))

* feat: streamlined logging ([`462fb66`](https://github.com/masa-finance/masa/commit/462fb66e82219dcac42e5086d56f60a7179fc945))

* feat: updating retry policies and error handling re 504s (broken) ([`3403f62`](https://github.com/masa-finance/masa/commit/3403f62a760d853b742032ce6d141405cd6a43b4))

* feat: cleaned up queue functionality, ordering, logging

Also broke out debugging functionality to accept a flag for debugging statements. ([`ab2e4d9`](https://github.com/masa-finance/masa/commit/ab2e4d95aff4fba503fd5b51360aaeeccff1bdd7))

* feat: made config more robust ([`f9cda10`](https://github.com/masa-finance/masa/commit/f9cda10c7595601a0bb35b0b27d8a25791e521d2))

* feat: working POC ([`7f91d54`](https://github.com/masa-finance/masa/commit/7f91d54030b11fb1a6a4f8b2db1dec1b3bd029eb))

* feat: added singleton classes, modified retry policy, added command line prompts ([`8b34e39`](https://github.com/masa-finance/masa/commit/8b34e390ff2c68beb9ebdc4416bb31e7a09d9a79))

* feat: separated concerns for x connection and x retriever

Also added some documentation to several files ([`898b130`](https://github.com/masa-finance/masa/commit/898b1300987e8dfea325cdba3ee0cdd987e53191))

* feat: added an orchestration component

This orchestration component will handle the state of the application, queueing new requests, and routing the request to the right applications. ([`afe0e98`](https://github.com/masa-finance/masa/commit/afe0e98ba39004b1bdb070d04d3ddb9a431a6220))

* feat: updated twitter retriever, separated concern

1. Separated concerns for state management, data storage, request routing, and retrieving tweets.
2. Working on ensuring application-wide state persistence ([`55e8372`](https://github.com/masa-finance/masa/commit/55e83729dbd16a43b3e5c939cd07b812eeab0ad0))

* feat: cleaned package imports, added request router ([`3a81cf8`](https://github.com/masa-finance/masa/commit/3a81cf89f25e1905f756025aa0f43be574a3e287))

* feat: added init files, moved main.py, updated README.md ([`21b2cdc`](https://github.com/masa-finance/masa/commit/21b2cdc12ea50fdb75e2ff731c5e1713c0350efc))

* feat: modified error handler, refactored api connections

Changed api_connections to be more general and moved twitter specific connection details to xtwitter

Added state_manager and data storage classes to handle state and storage of requests ([`990de83`](https://github.com/masa-finance/masa/commit/990de837b63b12fff4b886e03a1cda81b5fca7b0))

* feat: added config class and renamed masa to masa_tools ([`683bb16`](https://github.com/masa-finance/masa/commit/683bb16456fdbc229ff4fc3b6116aac8e8904171))

* feat: modified api_connection, added subclass placeholders

modified api_connection class and added subclass placeholders for x, discord, and telegram. Updated the documentation accordingly ([`b393c6c`](https://github.com/masa-finance/masa/commit/b393c6ca71d2c6e5cb03a82634031b4f32855506))

* feat: added generic connection classes (api and database)

Also made the requirements alphabetical ([`09f7a90`](https://github.com/masa-finance/masa/commit/09f7a9039c71871170b1fd4e1b01c3914ad4264a))

* feat: ported over hf functionality for refactor ([`f8cc84a`](https://github.com/masa-finance/masa/commit/f8cc84af54330b8bb1a056a1353be013e2f9e709))

* feat: added base error handling and logging ([`63675f5`](https://github.com/masa-finance/masa/commit/63675f5943be67e878c4cef9f95704fc2e354f4a))

* feat: added Sphinx documentation functionality

added base docs and some instructions around usage ([`2d1c2ce`](https://github.com/masa-finance/masa/commit/2d1c2ced2e6c42f2c3237e948dbd68d8b39703a3))

### Unknown

* Bump version: 0.1.17 → 0.1.18 ([`d0d0d24`](https://github.com/masa-finance/masa/commit/d0d0d2434439c92dc69952178192736b02496669))

* Update pyproject.toml ([`aa50b0d`](https://github.com/masa-finance/masa/commit/aa50b0d81fead8eb421839ee18797701a079f94a))

* update .bumpversion.cfg ([`4ba98db`](https://github.com/masa-finance/masa/commit/4ba98dbca64d0ba6f57e500349ab483f83dd12a3))

* Enhance documentation and project structure

- Update project dependencies and version in pyproject.toml
- Improve README with updated usage instructions and project details
- Restructure documentation generation process in update_docs.py
  - Recursively generate API docs for all modules
  - Add logging and error handling
  - Ensure Sphinx is installed before generating docs
- Modify masa.py to use relative path for docs directory
- Update .gitignore to exclude additional files
- Regenerate project metadata files (PKG-INFO, SOURCES.txt, requires.txt) ([`b099904`](https://github.com/masa-finance/masa/commit/b099904d1c5e9c01218bb9357517b7dc421412ff))

* doc: enhance docs to resolve rendering issues

- Reorganize CONTRIBUTING.md for clarity and add code style guidelines
- Update README.md with improved installation and usage instructions
- Rename MASA to Masa throughout the project for consistency
- Restructure documentation files and update table of contents
- Automate documentation rebuilding when viewing through CLI
- Remove manual installation steps from README
- Update project dependencies in pyproject.toml
- Improve inline documentation in .rst files
- Remove unused installation.rst file
- Refactor view_docs.py to remove manual build step
- Bump version to 0.1.12 in pyproject.toml ([`a0e4967`](https://github.com/masa-finance/masa/commit/a0e4967caa61f632b55cd889e0ae8b7a859c8c29))

* bug: fixed progress bar issues ([`a252832`](https://github.com/masa-finance/masa/commit/a252832b685ff11e7048c50492eba1fc73250235))

* added init_script, setup.py, and updated README.md

The folder structure is temporary to ensure the init script functioned properly.  The README explains the current state of the set-up.  Also made the environment.yml and requirements.txt more parsimonious ([`9ead544`](https://github.com/masa-finance/masa/commit/9ead5442e5d1001c45e83bef5b8c44129458123c))

* init commit ([`0a09baa`](https://github.com/masa-finance/masa/commit/0a09baa55e21580502b79bf30dade8ee7855e497))

* Initial commit ([`f109678`](https://github.com/masa-finance/masa/commit/f109678df4a0b40e92a7e1d869ecb0c214cd92ef))
