import os
import yaml
from dotenv import load_dotenv

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
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

    def get_env_var(self, key, default=None):
        """
        Get the value of the specified environment variable.
        
        :param key: The name of the environment variable.
        :param default: The default value to return if the environment variable is not found.
        :return: The value of the environment variable or the default value.
        """
        return os.getenv(key, default)


class XTwitterConfig(Config):
    """Configuration class for Twitter retriever."""

    def load_yaml_configs(self):
        """Load configurations from YAML files."""
        twitter_config_path = os.path.join(os.path.dirname(__file__), 'twitter_retriever_config.yaml')
        self.twitter_config = self.load_yaml_file(twitter_config_path)

    def load_env_configs(self):
        """Load configurations from environment variables."""
        self.twitter_env_config = {
            'BASE_URL': os.getenv('BASE_URL', 'http://localhost:8080/api/v1/'),
            'TWITTER_TIMEOUT': int(os.getenv('TWITTER_TIMEOUT', 30)),
            'TWITTER_MAX_RETRIES': int(os.getenv('TWITTER_MAX_RETRIES', 3)),
            'TWITTER_RETRY_DELAY': int(os.getenv('TWITTER_RETRY_DELAY', 960))
        }

    def get_config(self, key=None):
        """Get the Twitter configuration.

        :param key: Optional key to retrieve a specific configuration value.
        :return: Merged dictionary of YAML and environment configurations, or a specific value if key is provided.
        """
        merged_config = {**self.twitter_config, **self.twitter_env_config}
        if key is not None:
            return merged_config.get(key)
        return merged_config

    def set(self, key, value):
        """Set a configuration value.

        :param key: The configuration key.
        :param value: The value to set.
        """
        if key in self.twitter_env_config:
            self.twitter_env_config[key] = value
        elif key in self.twitter_config:
            self.twitter_config[key] = value
        else:
            raise KeyError(f"Configuration key '{key}' not found.")

    def update(self, config_dict):
        """Update multiple configuration values.

        :param config_dict: A dictionary of configuration key-value pairs.
        """
        for key, value in config_dict.items():
            self.set(key, value)

    def reload_configs(self):
        """Reload configurations from YAML files and environment variables."""
        self.load_yaml_configs()
        self.load_env_configs()

def load_configs():
    """Load all configurations.

    :return: Dictionary containing configurations for each retriever.
    """
    return {
        'twitter': XTwitterConfig().get_config(),
    }