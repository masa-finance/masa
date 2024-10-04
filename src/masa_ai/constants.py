"""
Constants module for the MASA project.

This module defines constant paths used throughout the project.
"""

import os
from pathlib import Path

# Define package root
PACKAGE_ROOT = Path(__file__).parent.resolve()
"""Path: The root directory of the MASA package."""

# Define config directory
CONFIG_DIR = PACKAGE_ROOT / 'configs'
"""Path: The directory where configuration files are stored."""

