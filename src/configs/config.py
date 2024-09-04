"""
Configuration module for the MASA project.

This module uses Dynaconf to manage configuration settings for the MASA project.
It provides functionality to load settings from files, environment variables,
and validate the configuration.
"""

import os
from dynaconf import Dynaconf, Validator

global_settings = Dynaconf(
    envvar_prefix="MASA",
    settings_files=['configs/settings.yaml'],
    environments=True,
    load_dotenv=True,
    dotenv_path="configs/.env",
    merge_enabled=True,
    validators=[
        Validator('twitter.BASE_URL', must_exist=True, when=Validator('twitter.BASE_URL_LOCAL', must_exist=False)),
        Validator('twitter.BASE_URL_LOCAL', must_exist=True, when=Validator('twitter.BASE_URL', must_exist=False)),
        Validator('request_manager.STATE_FILE', must_exist=True),
        Validator('request_manager.QUEUE_FILE', must_exist=True)
    ]
)

def initialize_config():
    """
    Initialize the global settings using Dynaconf.
    
    This function loads environment variables from the .env file and initializes
    the Dynaconf settings using the specified configuration files and environment.
    It also validates the presence of required settings.

    Returns:
        Dynaconf: The initialized and validated global settings object.
    """
    global_settings.validators.validate()
    return global_settings