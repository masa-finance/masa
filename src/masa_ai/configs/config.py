"""
Configuration module for the MASA project.

This module uses Dynaconf to manage configuration settings for the MASA project.
It provides functionality to load settings from files, environment variables,
and validate the configuration.
"""
import os
from pathlib import Path
import appdirs
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
        Validator('logging.COLOR_ENABLED', is_type_of=bool, default=True),
        Validator('data_storage.DATABASE_NAME', must_exist=True),
    ]
)


def initialize_config():
    """
    Initialize the global settings using Dynaconf.
    
    This function loads environment variables and initializes the Dynaconf settings.
    It sets up user-specific directories for data, cache, and config using appdirs.
    
    Returns:
        Dynaconf: The initialized and validated global settings object.
    """
    # Set up user-specific directories
    user_data_dir = Path(appdirs.user_data_dir("masa_ai"))
    user_cache_dir = Path(appdirs.user_cache_dir("masa_ai"))
    
    # Create directories if they don't exist
    user_data_dir.mkdir(parents=True, exist_ok=True)
    user_cache_dir.mkdir(parents=True, exist_ok=True)

    if not global_settings.get('data_storage.DATA_DIRECTORY'):
        global_settings.set('data_storage.DATA_DIRECTORY', str(user_data_dir))
        
    global_settings.set(
        'data_storage.DATABASE_PATH',
        str(user_data_dir / 'ddb.db')
    )
    
    # Set cache directory
    global_settings.set('data_storage.CACHE_DIRECTORY', str(user_cache_dir))
    
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
