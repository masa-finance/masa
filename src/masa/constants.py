import os
from pathlib import Path

# Define package root
PACKAGE_ROOT = Path(__file__).parent.resolve()
"""Path: The root directory of the MASA package."""

# Define config directory
CONFIG_DIR = PACKAGE_ROOT / 'configs'
"""Path: The directory where configuration files are stored."""

# Define data directory
DATA_DIR = PACKAGE_ROOT / 'data'
"""Path: The directory where data files are stored."""
