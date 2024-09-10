"""
MASA:

Decentralized Data Retrieval and Processing Framework

Key components:
- Retrieval: Fetch data from various sources
- Quality Control: Validate data and handle errors

Other components (Augmentation, Structuring, Ecosystem integration) are
currently in development and will be added in future releases.

"""

from importlib import import_module

def lazy_import(name):
    return import_module(f'.{name}', __name__)

configs = lazy_import('configs')
tools = lazy_import('tools')
connections = lazy_import('connections')
orchestration = lazy_import('orchestration')


__all__ = [
    'tools',
    'configs',
    'connections',
    'orchestration'
]

__version__ = '0.1.11'
"""str: Current version of the MASA package."""