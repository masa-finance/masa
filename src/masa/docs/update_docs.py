import os
import subprocess

def update_docs():
    """
    Update the documentation for the MASA project.

    This function performs the following steps:
    1. Changes the current working directory to the directory containing this script.
    2. Runs the `sphinx-apidoc` command to generate the API documentation from the `masa` package.
    3. Changes the current working directory to the `docs` directory.
    4. Runs the `make clean` command to clean the previous build files.
    5. Runs the `make html` command to build the HTML documentation.
    """
    
    # Change the current working directory to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run the `sphinx-apidoc` command to generate the API documentation from the `masa` package
    subprocess.run(["sphinx-apidoc", "-f", "-o", "docs/source/modules", "masa"])
    
    # Run the `make clean` command to clean the previous build files
    subprocess.run(["make", "clean"])
    
    # Run the `make html` command to build the HTML documentation
    subprocess.run(["make", "html"])

if __name__ == "__main__":
    # Call the `update_docs()` function when this script is run directly
    update_docs()
