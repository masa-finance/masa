import os
import subprocess

def update_docs():
   
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run sphinx-apidoc
    subprocess.run(["sphinx-apidoc", "-f", "-o", "docs/source/modules", "masa"])

    # Build the documentation
    os.chdir("docs")
    subprocess.run(["make", "clean"])
    subprocess.run(["make", "html"])

if __name__ == "__main__":
    update_docs()
