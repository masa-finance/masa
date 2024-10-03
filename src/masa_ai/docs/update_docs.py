from pathlib import Path
import subprocess
import os
import shutil
import logging
import colorlog


handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def check_dependencies():
    """
    Check if Sphinx is installed.

    Returns:
        bool: True if Sphinx is installed, False otherwise.
    """
    try:
        subprocess.run(["sphinx-build", "--version"], check=True)
    except FileNotFoundError:
        logger.error("Sphinx is not installed or not found in the PATH.")
        return False
    return True

def clean_previous_build():
    """
    Clean previous Sphinx build files.

    This function runs the `make clean` command to remove previous build files.
    """
    logger.info("Cleaning previous build files...")
    subprocess.run(["make", "clean"], check=True, capture_output=True)

def build_html():
    """
    Build HTML documentation using Sphinx.

    This function runs the `make html` command to generate the HTML documentation.
    If an error occurs, the output and error messages are logged for debugging.

    Raises:
        subprocess.CalledProcessError: If the `make html` command fails.
    """
    logger.info("Building HTML documentation...")
    result = subprocess.run(["make", "html"], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Error building HTML documentation:")
        logger.error(result.stdout)
        logger.error(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, result.args)
    else:
        logger.info("HTML documentation built successfully.")

def generate_api_docs(src_masa_path, modules_dir):
    """
    Generate API documentation using Sphinx apidoc.

    Args:
        src_masa_path (Path): Path to the source directory of the MASA project.
        modules_dir (Path): Path to the directory where the generated documentation will be stored.
    """
    for module_path in src_masa_path.iterdir():
        if module_path.is_dir() and not module_path.name.startswith("__") and module_path.name != "docs":
            relative_path = module_path.relative_to(src_masa_path)
            output_path = modules_dir / relative_path
            output_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Generating API documentation for '{relative_path}'...")

            # Run sphinx-apidoc command with `--tocfile index` to generate `index.rst`
            subprocess.run([
                "sphinx-apidoc",
                "-f",
                "-o", str(output_path),
                str(module_path),
                "--separate",
                "-H", "Masa AI" if relative_path.name == "masa_ai" else relative_path.name.capitalize(),
                "-e",
                "--tocfile", "index"  # Ensures that `index.rst` is used instead of `modules.rst`
            ], check=True, capture_output=True)

def update_docs():
    """
    Update the documentation for the MASA project.

    This function performs the following steps:
    1. Changes the current working directory to the directory containing this script.
    2. Runs the `sphinx-apidoc` command to generate the API documentation from the `src/masa_ai` package.
    3. Runs the `make clean` command to clean the previous build files.
    4. Runs the `make html` command to build the HTML documentation.
    """
    # Get the current file's directory (docs directory)
    current_dir = Path(__file__).resolve().parent
    os.chdir(current_dir)

    # Update the src_masa_path calculation
    src_masa_path = current_dir.parent  # This points to the masa_ai directory
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