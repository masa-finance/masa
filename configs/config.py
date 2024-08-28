import os
from dotenv import load_dotenv
from dynaconf import Dynaconf
from masa_tools.qc.qc_manager import QCManager


global_settings = None
qc_manager = QCManager()

def initialize_config():
    """
    Initialize the global settings using Dynaconf.
    
    This function loads environment variables from the .env file and initializes
    the Dynaconf settings using the specified configuration files and environment.
    It also validates the presence of required settings.
    """
    global global_settings
    
    # Load environment variables from .env file
    load_dotenv()

    # Initialize Dynaconf settings
    global_settings = Dynaconf(
        envvar_prefix="MASA",
        settings_files=['settings.yaml', '.secrets.yaml'],
        environments=True,
    )

    # Validate required settings are present
    required_settings = ['twitter.BASE_URL', 'request_manager.state_file', 'request_manager.queue_file']
    for setting in required_settings:
        if not global_settings.get(setting):
            qc_manager.log_error(f"Required setting '{setting}' is missing", context="Config")
            raise ValueError(f"Required setting '{setting}' is missing")

    qc_manager.log_info("Configurations initialized successfully.", context="Config")