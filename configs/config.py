import os
import yaml
from dotenv import load_dotenv

class Config:
    """Base configuration class."""

    def __init__(self):
        """Initialize the Config class."""
        load_dotenv()  # Load environment variables from .env file
        self.load_yaml_configs()
        self.load_env_configs()

    def load_yaml_configs(self):
        """Load configurations from YAML files."""
        pass

    def load_env_configs(self):
        """Load configurations from environment variables."""
        pass

    def load_yaml_file(self, file_path):
        """Load configurations from a YAML file.

        :param file_path: Path to the YAML file.
        :return: Loaded YAML data.
        """
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)


class XTwitterConfig(Config):
    """Configuration class for Twitter retriever."""

    def load_yaml_configs(self):
        """Load configurations from YAML files."""
        self.twitter_config = self.load_yaml_file('twitter_retriever_config.yaml')

    def load_env_configs(self):
        """Load configurations from environment variables."""
        self.twitter_env_config = {
            'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
            'TWITTER_TIMEOUT': int(os.getenv('TWITTER_TIMEOUT', 30)),
            'TWITTER_MAX_RETRIES': int(os.getenv('TWITTER_MAX_RETRIES', 3)),
            'TWITTER_RETRY_DELAY': int(os.getenv('TWITTER_RETRY_DELAY', 960))
        }

    def get_config(self):
        """Get the Twitter configuration.

        :return: Merged dictionary of YAML and environment configurations.
        """
        return {**self.twitter_config, **self.twitter_env_config}


class DatabaseConfig(Config):
    """Configuration class for database."""

    def load_yaml_configs(self):
        """Load configurations from YAML files."""
        self.database_config = self.load_yaml_file('database_config.yaml')

    def load_env_configs(self):
        """Load configurations from environment variables."""
        self.database_env_config = {
            'DB_HOST': os.getenv('DB_HOST'),
            'DB_PORT': int(os.getenv('DB_PORT', 5432)),
            # Load other database-related env configs
        }

    def get_config(self):
        """Get the database configuration.

        :return: Merged dictionary of YAML and environment configurations.
        """
        return {**self.database_config, **self.database_env_config}


def load_configs():
    """Load all configurations.

    :return: Dictionary containing configurations for each retriever.
    """
    return {
        'twitter': TwitterConfig().get_config(),
        'database': DatabaseConfig().get_config()
    }