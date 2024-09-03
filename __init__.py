"""
MASA:

Decentralized Data Retrieval and Processing Framework

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
from . import orchestration
__all__ = [
    'tools',
    'configs',
    'connections',
    'main',
    'requests',
    'orchestration'
]

__version__ = '0.1.0'
"""str: Current version of the MASA package."""