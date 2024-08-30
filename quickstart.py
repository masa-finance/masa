"""
Quickstart script for setting up the MASA project environment.

This script automates the process of creating the necessary folder structure,
setting up a Conda environment, and installing required packages for the MASA project.

Usage:
    python quickstart.py

The script performs the following tasks:
1. Creates the folder structure for the MASA project.
2. Creates a new Conda environment using the provided environment.yml file.
3. Installs required packages in the Conda environment.

Note: This script should be run from the root directory of the MASA project.
"""

import os
import subprocess
import sys
import yaml

def create_folder_structure(base_path):
    """
    Create the necessary folder structure for the MASA project.

    Args:
        base_path (str): The base path where the folders will be created.
    """
    folders = [
        os.path.join(base_path, 'data'),
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # Create example .secrets.yaml file
    secrets_file = os.path.join(base_path, 'configs', '.secrets.yaml')
    if not os.path.exists(secrets_file):
        with open(secrets_file, 'w') as file:
            file.write("""twitter:
  API_KEY: "your_twitter_api_key"
  API_SECRET: "your_twitter_api_secret"
""")
        print(f"Created example file: {secrets_file}")

def create_conda_environment(yaml_path):
    """
    Create a new conda environment using the provided YAML file.

    Args:
        yaml_path (str): The path to the YAML file containing the environment configuration.

    Returns:
        str: The name of the created conda environment.
    """
    env_name = get_env_name(yaml_path)
    subprocess.run(['conda', 'env', 'create', '-f', yaml_path])
    print(f"Created conda environment: {env_name}")
    return env_name

def install_requirements(env_name):
    """
    Install the required packages in the specified conda environment.

    Args:
        env_name (str): The name of the conda environment.
    """
    # Activate the conda environment and update conda packages
    activate_cmd = f"conda activate {env_name} && conda env update -f environment.yml"
    if os.name == 'nt':  # Windows
        subprocess.run(activate_cmd, shell=True)
    else:  # Unix-based systems
        subprocess.run(['bash', '-c', f'source activate {env_name} && conda env update -f environment.yml'])
    print(f"Updated conda environment: {env_name}")

    # The pip packages from requirements.txt will be installed automatically
    # due to the reference in environment.yml

def get_env_name(yaml_path):
    """
    Get the name of the conda environment from the YAML file.

    Args:
        yaml_path (str): The path to the YAML file containing the environment configuration.

    Returns:
        str: The name of the conda environment.
    """
    with open(yaml_path, 'r') as file:
        env_config = yaml.safe_load(file)
    return env_config['name']

def main():
    """
    Main function to set up the MASA project environment.

    This function orchestrates the creation of the folder structure,
    Conda environment setup, and package installation.
    """
    base_path = os.getcwd()
    yaml_path = os.path.join(base_path, 'environment.yml')
    
    create_folder_structure(base_path)
    
    # Create and update conda environment
    env_name = create_conda_environment(yaml_path)
    install_requirements(env_name)
    
    print("\nSetup complete!")
    print(f"To activate the conda environment, run:\nconda activate {env_name}")
    print("\nAfter activation, you can start using the masa package.")

if __name__ == "__main__":
    main()