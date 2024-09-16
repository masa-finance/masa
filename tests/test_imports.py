import pytest
import importlib
import sys
from pathlib import Path

# Add the masa directory to the Python path
masa_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(masa_path))

def get_all_modules(package_path):
    modules = []
    for py_file in package_path.rglob('*.py'):
        if py_file.name == '__init__.py':
            module_name = str(py_file.parent).replace('/', '.').replace('\\', '.')
        else:
            module_name = str(py_file.with_suffix('')).replace('/', '.').replace('\\', '.')
        
        if module_name.startswith('masa.'):
            modules.append(module_name)
    return modules

all_modules = get_all_modules(masa_path / 'masa')

@pytest.mark.parametrize("module_name", all_modules)
def test_import(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError as e:
        pytest.fail(f"Failed to import {module_name}: {e}")
