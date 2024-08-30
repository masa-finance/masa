"""
MASA: Multi-Agent System Architecture

This package provides a framework for building and managing multi-agent systems.
It currently includes tools for data retrieval and quality control, with more
features in development.

Key components:
- Retrieval: Fetch data from various sources
- Quality Control: Validate data and handle errors

Other components (Augmentation, Structuring, Ecosystem integration) are
currently in development and will be added in future releases.

"""

from . import tools
from . import configs
from . import connections
from . import main
from . import requests

__all__ = [
    'tools',
    'configs',
    'connections',
    'main',
    'requests'
]

__version__ = '0.1.0'
"""str: Current version of the MASA package."""