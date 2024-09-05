import os
import subprocess

def update_docs():
    """Update the documentation by running sphinx-apidoc and building the docs."""
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(docs_dir))

    # Run sphinx-apidoc
    subprocess.run(["sphinx-apidoc", "-f", "-o", os.path.join(docs_dir, "source", "modules"), os.path.join(project_root, "masa")])

    # Build the documentation using make
    subprocess.run(["make", "clean"], cwd=docs_dir)
    subprocess.run(["make", "html"], cwd=docs_dir)

if __name__ == "__main__":
    update_docs()
