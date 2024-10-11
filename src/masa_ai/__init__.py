"""
MASA: Masa AI Software Architecture

This package serves as the core of the MASA project, providing essential components
for data retrieval, quality control, and orchestration. The framework is designed
to be modular and extensible, allowing for future enhancements and integrations.

Key Components:
- Retrieval: Fetch data from various sources.
- Quality Control: Validate data and handle errors.
- Orchestration: Manage the overall processing of requests.

Note:
Other components such as Augmentation, Structuring, and Ecosystem Integration are
currently in development and will be added in future releases.

"""

from importlib import import_module
from importlib.metadata import version

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

__version__ = "0.2.3"
