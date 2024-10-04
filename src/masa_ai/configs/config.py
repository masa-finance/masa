"""
Configuration module for the MASA project.

This module uses Dynaconf to manage configuration settings for the MASA project.
It provides functionality to load settings from files, environment variables,
and validate the configuration.
"""

import os
from pathlib import Path
from dynaconf import Dynaconf, Validator
from ..constants import CONFIG_DIR

def get_config_files():
    settings_file = CONFIG_DIR / 'settings.yaml'
    secrets_file = CONFIG_DIR / '.secrets.yaml'
    return str(settings_file), str(secrets_file)

settings_file, secrets_file = get_config_files()

global_settings = Dynaconf(
    envvar_prefix="MASA",
    settings_files=[settings_file, secrets_file],
    environments=True,
    load_dotenv=True,
    merge_enabled=True,
    env_switcher='ENV_FOR_DYNACONF',
    env=os.environ.get('ENV_FOR_DYNACONF', 'default'),
    settings_file_for_write=settings_file,  # Specify the settings file for writing
    validators=[
        Validator('twitter.BASE_URL', must_exist=True, when=Validator('twitter.BASE_URL_LOCAL', must_exist=False)),
        Validator('twitter.BASE_URL_LOCAL', must_exist=True, when=Validator('twitter.BASE_URL', must_exist=False)),
        Validator('request_manager.STATE_FILE', must_exist=True),
        Validator('request_manager.QUEUE_FILE', must_exist=True),
        Validator('logging.COLOR_ENABLED', is_type_of=bool, default=True)
    ]
)


def initialize_config():
    """
    Initialize the global settings using Dynaconf.
    
    This function loads environment variables and initializes the Dynaconf settings.
    It sets the default data directory to the 'data' subdirectory of the current
    working directory if not specified.
    
    Returns:
        Dynaconf: The initialized and validated global settings object.
    """
    if not global_settings.get('data_storage.DATA_DIRECTORY'):
        global_settings.set(
            'data_storage.DATA_DIRECTORY',
            os.path.join(os.getcwd(), 'data')
        )
    else:
        data_dir = global_settings.get('data_storage.DATA_DIRECTORY')
        global_settings.set(
            'data_storage.DATA_DIRECTORY',
            os.path.abspath(data_dir)
        )
    global_settings.validators.validate()
    return global_settings

def get_project_root() -> Path:
    """
    Get the project root directory.

    This function returns the path to the project root directory by referencing
    the .project_root file.

    Returns:
        Path: The path to the project root directory.
    """
    return Path(__file__).resolve().parent.parent.parent

def get_config_path(filename: str) -> Path:
    """
    Get the configuration file path.

    This function constructs the path to a configuration file located in the
    'configs' directory within the project.

    Args:
        filename (str): The name of the configuration file.

    Returns:
        Path: The path to the configuration file.
    """
    return CONFIG_DIR / filename
