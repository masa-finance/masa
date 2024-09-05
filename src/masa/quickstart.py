"""
Quickstart script for setting up the MASA project environment.

This script automates the process of creating the necessary folder structure,
setting up a Conda environment, and installing required packages for the MASA project.

Usage:
    python quickstart.py

The script performs the following tasks:
1. Checks if Anaconda is installed.
2. Creates the folder structure for the MASA project.
3. Creates a new Conda environment using the provided environment.yml file.
4. Installs required packages in the Conda environment.

Note: This script should be run from the root directory of the MASA project.
"""

import os
import subprocess
import sys
import yaml

def check_anaconda_installed():
    """
    Check if Anaconda is installed on the system.

    :return: True if Anaconda is installed, False otherwise.
    :rtype: bool
    """
    try:
        subprocess.run(['conda', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Anaconda is installed.")
        return True
    except FileNotFoundError:
        print("Anaconda is not installed. Please install Anaconda and try again.")
        sys.exit(1)

def create_conda_environment(yaml_path):
    """
    Create a new conda environment using the provided YAML file.

    :param yaml_path: The path to the YAML file containing the environment configuration.
    :type yaml_path: str
    :return: The name of the created conda environment.
    :rtype: str
    """
    env_name = get_env_name(yaml_path)
    subprocess.run(['conda', 'env', 'create', '-f', yaml_path])
    print(f"Created conda environment: {env_name}")
    return env_name

def install_requirements(env_name):
    """
    Install the required packages in the specified conda environment.

    :param env_name: The name of the conda environment.
    :type env_name: str
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

    :param yaml_path: The path to the YAML file containing the environment configuration.
    :type yaml_path: str
    :return: The name of the conda environment.
    :rtype: str
    """
    with open(yaml_path, 'r') as file:
        env_config = yaml.safe_load(file)
    return env_config['name']

def main():
    """
    Main function to set up the MASA project environment.

    This function orchestrates the checking of Anaconda installation,
    creation of the folder structure, Conda environment setup, and package installation.
    """
    if not check_anaconda_installed():
        print("Anaconda is not installed. Please install Anaconda and try again.")
        sys.exit(1)

    base_path = os.getcwd()
    yaml_path = os.path.join(base_path, 'environment.yml')
    
    # Create and update conda environment
    env_name = create_conda_environment(yaml_path)
    install_requirements(env_name)
    
    print("\nSetup complete!")
    print(f"The conda environment {env_name} has been created and configured.")
    print("\nYou can start using the masa package.")
    print(f"To activate the conda environment, run:\nconda activate {env_name}")

if __name__ == "__main__":
    main()