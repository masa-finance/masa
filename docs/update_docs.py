from pathlib import Path
import subprocess
import os

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

    # Run the `sphinx-apidoc` command to generate the API documentation
    subprocess.run(["sphinx-apidoc", "-f", "-o", str(current_dir / "source/modules"), str(src_masa_path)])
    
    # Run the `make clean` command to clean the previous build files
    subprocess.run(["make", "clean"])
    
    # Run the `make html` command to build the HTML documentation
    subprocess.run(["make", "html"])

if __name__ == "__main__":
    # Call the `update_docs()` function when this script is run directly
    update_docs()