import os
from pathlib import Path
import pkg_resources
from ...constants import PACKAGE_ROOT, CONFIG_DIR, DATA_DIR

def get_package_root():
    return Path(pkg_resources.resource_filename('masa', ''))

PROJECT_ROOT = get_package_root()
CONFIG_DIR = PROJECT_ROOT / 'configs'
DATA_DIR = PROJECT_ROOT / 'data'
LOGS_DIR = PROJECT_ROOT / 'logs'
ORCHESTRATION_DIR = PROJECT_ROOT / 'orchestration'

def get_config_path(filename: str) -> Path:
    return CONFIG_DIR / filename

def get_data_path(filename: str) -> Path:
    return DATA_DIR / filename

def get_log_path(filename: str = 'masa.log') -> Path:
    """
    Get the path for a log file within the logs directory.

    :param filename: Name of the log file (default: 'masa.log')
    :type filename: str
    :return: Full path to the log file
    :rtype: Path
    """
    log_dir = PROJECT_ROOT / 'logs'
    ensure_dir(log_dir)
    return log_dir / filename

def get_orchestration_path(filename: str) -> Path:
    return ORCHESTRATION_DIR / filename

def ensure_dir(directory):
    """Ensure that a directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)

# Environment variable for custom data directory
CUSTOM_DATA_DIR = os.environ.get('MASA_CUSTOM_DATA_DIR')
if CUSTOM_DATA_DIR:
    DATA_DIR = Path(CUSTOM_DATA_DIR).resolve()
