import os
from pathlib import Path

# Define package root
PACKAGE_ROOT = Path(__file__).parent.resolve()

# Define config directory
CONFIG_DIR = PACKAGE_ROOT / 'configs'

# Define data directory
DATA_DIR = PACKAGE_ROOT / 'data'
