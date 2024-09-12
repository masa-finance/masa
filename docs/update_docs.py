from pathlib import Path
import subprocess
import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)

def check_dependencies():
    """
    Check if Sphinx is installed.

    Returns:
        bool: True if Sphinx is installed, False otherwise.
    """
    try:
        subprocess.run(["sphinx-build", "--version"], check=True)
    except FileNotFoundError:
        logging.error("Sphinx is not installed or not found in the PATH.")
        return False
    return True

def clean_previous_build():
    """
    Clean previous Sphinx build files.

    This function runs the `make clean` command to remove previous build files.
    """
    logging.info("Cleaning previous build files...")
    subprocess.run(["make", "clean"], check=True)

def build_html():
    """
    Build HTML documentation using Sphinx.

    This function runs the `make html` command to generate the HTML documentation.
    """
    logging.info("Building HTML documentation...")
    subprocess.run(["make", "html"], check=True)

def generate_api_docs(src_masa_path, modules_dir):
    """
    Generate API documentation using Sphinx apidoc.

    Args:
        src_masa_path (Path): Path to the source directory of the MASA project.
        modules_dir (Path): Path to the directory where the generated documentation will be stored.
    """
    for module_path in src_masa_path.rglob("*"):
        if module_path.is_dir() and not module_path.name.startswith("__"):
            relative_path = module_path.relative_to(src_masa_path)
            output_path = modules_dir / relative_path
            output_path.mkdir(parents=True, exist_ok=True)

            logging.info(f"Generating API documentation for '{relative_path}'...")

            # Run sphinx-apidoc command with `--tocfile index` to generate `index.rst`
            subprocess.run([
                "sphinx-apidoc",
                "-f",
                "-o", str(output_path),
                str(module_path),
                "--separate",
                "-H", relative_path.name.capitalize(),
                "-e",
                "--tocfile", "index"  # Ensures that `index.rst` is used instead of `modules.rst`
            ], check=True)

def update_docs():
    """
    Update the documentation for the MASA project.

    This function performs the following steps:
    1. Changes the current working directory to the directory containing this script.
    2. Runs the `sphinx-apidoc` command to generate the API documentation from the `src/masa` package.
    3. Runs the `make clean` command to clean the previous build files.
    4. Runs the `make html` command to build the HTML documentation.
    """
    # Get the current file's directory
    current_dir = Path(__file__).resolve().parent

    # Change the current working directory to the directory containing this script
    os.chdir(current_dir)

    # Get the path to the src/masa directory
    src_masa_path = current_dir.parent / 'src' / 'masa'
    modules_dir = current_dir / "source/modules"

    # Clear existing modules directory
    if modules_dir.exists():
        shutil.rmtree(modules_dir)
    modules_dir.mkdir(parents=True, exist_ok=True)

    # Generate documentation recursively for all modules
    generate_api_docs(src_masa_path, modules_dir)
    clean_previous_build()
    build_html()

if __name__ == "__main__":
    if check_dependencies():
        update_docs()