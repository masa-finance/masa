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

    def get_env_var(self, key):
        """
        Get the value of the specified environment variable.
        
        :param key: The name of the environment variable.
        :type key: str
        :return: The value of the environment variable.
        :rtype: str
        :raises KeyError: If the environment variable is not found.
        """
        value = os.getenv(key)
        if value is None:
            raise KeyError(f"Environment variable '{key}' not found.")
        return value


class XTwitterConfig(Config):
    """Configuration class for Twitter retriever."""

    def load_yaml_configs(self):
        """Load configurations from YAML files."""
        twitter_config_path = os.path.join(os.path.dirname(__file__), 'twitter_retriever_config.yaml')
        self.twitter_config = self.load_yaml_file(twitter_config_path)

    def load_env_configs(self):
        """Load configurations from environment variables."""
        self.twitter_env_config = {
            'TWITTER_TIMEOUT': int(os.getenv('TWITTER_TIMEOUT', 30)),
            'TWITTER_MAX_RETRIES': int(os.getenv('TWITTER_MAX_RETRIES', 3)),
            'TWITTER_RETRY_DELAY': int(os.getenv('TWITTER_RETRY_DELAY', 960))
        }

    def get_config(self):
        """Get the Twitter configuration.

        :return: Merged dictionary of YAML and environment configurations.
        """
        return {**self.twitter_config, **self.twitter_env_config}


def load_configs():
    """Load all configurations.

    :return: Dictionary containing configurations for each retriever.
    """
    return {
        'twitter': XTwitterConfig().get_config(),
    }