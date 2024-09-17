import os
from pathlib import Path
import pkg_resources
from ...constants import PACKAGE_ROOT, CONFIG_DIR, DATA_DIR

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
DATA_DIR = PROJECT_ROOT / 'data'
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

def get_data_path(filename: str) -> Path:
    """
    Get the path for a data file within the data directory.

    :param filename: Name of the data file
    :type filename: str
    :return: Full path to the data file
    :rtype: Path
    """
    return DATA_DIR / filename

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

# Environment variable for custom data directory
CUSTOM_DATA_DIR = os.environ.get('MASA_CUSTOM_DATA_DIR')
if CUSTOM_DATA_DIR:
    DATA_DIR = Path(CUSTOM_DATA_DIR).resolve()
