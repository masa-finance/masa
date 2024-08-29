"""
Configuration module for the MASA project.
"""

import os
from dynaconf import Dynaconf, Validator

global_settings = Dynaconf(
    envvar_prefix="MASA",
    settings_files=['configs/settings.yaml'],  # Specify the path to the settings file
    environments=True,  # Enable environment-specific settings
    load_dotenv=True,  # Load environment variables from .env file
    dotenv_path="configs/.env",  # Specify the path to the .env file
    merge_enabled=True,  # Merge settings from different sources
    validators=[
        Validator('twitter.BASE_URL', must_exist=True, when=Validator('twitter.BASE_URL_LOCAL', must_exist=False)),
        Validator('twitter.BASE_URL_LOCAL', must_exist=True, when=Validator('twitter.BASE_URL', must_exist=False)),
        Validator('request_manager.STATE_FILE', must_exist=True),
        Validator('request_manager.QUEUE_FILE', must_exist=True)
    ]
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
# `environments` = Enable environment-specific settings.
# `load_dotenv` = Load environment variables from .env file.
# `dotenv_path` = Specify the path to the .env file.
# `merge_enabled` = Merge settings from different sources.
# `validators` = Specify validation rules for settings.

def initialize_config():
    """
    Initialize the global settings using Dynaconf.
    
    This function loads environment variables from the .env file and initializes
    the Dynaconf settings using the specified configuration files and environment.
    It also validates the presence of required settings.
    """
    # Validate the settings
    global_settings.validators.validate()

    return global_settings