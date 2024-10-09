from pathlib import Path
import pkg_resources
from ...constants import CONFIG_DIR

def get_package_root() -> Path:
    """
    Get the root directory of the package.

    This function retrieves the root directory of the 'masa_ai' package using
    pkg_resources.

    :return: Path to the root directory of the package
    :rtype: Path
    """
    return Path(pkg_resources.resource_filename('masa_ai', ''))

PROJECT_ROOT = get_package_root()
CONFIG_DIR = PROJECT_ROOT / 'configs'
LOGS_DIR = PROJECT_ROOT / 'logs'
ORCHESTRATION_DIR = PROJECT_ROOT / 'orchestration'

def get_config_path(filename: str) -> Path:
    """
    Get the path for a configuration file within the configs directory.

    :param filename: Name of the configuration file
    :type filename: str
    :return: Full path to the configuration file
    :rtype: Path
    """
    return CONFIG_DIR / filename

def get_log_path(filename: str = 'masa_ai.log') -> Path:
    """
    Get the path for a log file within the logs directory.

    :param filename: Name of the log file (default: 'masa_ai.log')
    :type filename: str
    :return: Full path to the log file
    :rtype: Path
    """
    log_dir = PROJECT_ROOT / 'logs'
    ensure_dir(log_dir)
    return log_dir / filename

def get_orchestration_path(filename: str) -> Path:
    """
    Get the path for an orchestration file within the orchestration directory.

    :param filename: Name of the orchestration file
    :type filename: str
    :return: Full path to the orchestration file
    :rtype: Path
    """
    return ORCHESTRATION_DIR / filename

def ensure_dir(directory: Path):
    """
    Ensure that a directory exists.

    This function creates the directory if it does not already exist.

    :param directory: Path to the directory
    :type directory: Path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_data_directory() -> Path:
    """
    Get the data directory from the global settings.

    :return: Path to the data directory.
    :rtype: Path
    """
    from ...configs.config import global_settings
    data_dir = global_settings.data_storage.DATA_DIRECTORY
    return Path(data_dir)

def get_data_path(filename: str) -> Path:
    """
    Get the path for a data file within the data directory.

    :param filename: Name of the data file.
    :type filename: str
    :return: Full path to the data file.
    :rtype: Path
    """
    data_dir = get_data_directory()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / filename
