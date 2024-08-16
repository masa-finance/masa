import os
import subprocess
import sys
import yaml

def create_folder_structure(base_path):
    folders = [
        os.path.join(base_path, 'data'),
        os.path.join(base_path, 'logs'),
        os.path.join(base_path, 'configs'),
        os.path.join(base_path, 'output'),
        os.path.join(base_path, 'masa'),
        os.path.join(base_path, 'masa', 'retrieve'),
        os.path.join(base_path, 'masa', 'structure'),
        os.path.join(base_path, 'masa', 'augment'),
        os.path.join(base_path, 'masa', 'ecosystem'),
        os.path.join(base_path, 'masa', 'qc'),
        os.path.join(base_path, 'masa', 'utils')
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

    # Create __init__.py files
    init_folders = [
        os.path.join(base_path, 'masa'),
        os.path.join(base_path, 'masa', 'retrieve'),
        os.path.join(base_path, 'masa', 'structure'),
        os.path.join(base_path, 'masa', 'augment'),
        os.path.join(base_path, 'masa', 'ecosystem'),
        os.path.join(base_path, 'masa', 'qc'),
        os.path.join(base_path, 'masa', 'utils')
    ]

    for folder in init_folders:
        init_file = os.path.join(folder, '__init__.py')
        open(init_file, 'a').close()
        print(f"Created file: {init_file}")

    # Create other necessary files
    files_to_create = [
        os.path.join(base_path, 'masa', 'config.py'),
        os.path.join(base_path, 'masa', 'main.py'),
        os.path.join(base_path, 'masa', 'retrieve', 'retrieve_base.py'),
        os.path.join(base_path, 'masa', 'retrieve', 'retrieve_twitter.py'),
        os.path.join(base_path, 'masa', 'structure', 'structure_base.py'),
        os.path.join(base_path, 'masa', 'structure', 'structure_to_parquet.py'),
        os.path.join(base_path, 'masa', 'structure', 'structure_to_csv.py'),
        os.path.join(base_path, 'masa', 'structure', 'structure_to_json.py'),
        os.path.join(base_path, 'masa', 'augment', 'augment_base.py'),
        os.path.join(base_path, 'masa', 'augment', 'augment_summarize.py'),
        os.path.join(base_path, 'masa', 'augment', 'augment_metadata.py'),
        os.path.join(base_path, 'masa', 'ecosystem', 'chunking.py'),
        os.path.join(base_path, 'masa', 'ecosystem', 'embedding.py'),
        os.path.join(base_path, 'masa', 'ecosystem', 'vector_db.py'),
        os.path.join(base_path, 'masa', 'ecosystem', 'saas_services.py'),
        os.path.join(base_path, 'masa', 'qc', 'logging.py'),
        os.path.join(base_path, 'masa', 'qc', 'error_handler.py'),
        os.path.join(base_path, 'masa', 'qc', 'data_validation.py'),
        os.path.join(base_path, 'masa', 'utils', 'helper_functions.py'),
    ]

    for file in files_to_create:
        open(file, 'a').close()
        print(f"Created file: {file}")

def create_conda_environment(yaml_path):
    env_name = get_env_name(yaml_path)
    subprocess.run(['conda', 'env', 'create', '-f', yaml_path])
    print(f"Created conda environment: {env_name}")
    return env_name

def install_requirements(env_name):
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
    with open(yaml_path, 'r') as file:
        env_config = yaml.safe_load(file)
    return env_config['name']

def main():
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