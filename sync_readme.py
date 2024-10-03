def sync_readme():
    """
    Synchronize README files between the top-level directory and the package directory.

    Copies the README.md file from the top-level directory to the package directory to ensure that the
    package contains the most recent documentation when uploaded or built.

    """
    import shutil
    import os

    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define source and destination paths
    source = os.path.join(script_dir, 'README.md')
    destination = os.path.join(script_dir, 'src', 'masa_ai', 'docs', 'source', 'README.md')

    # Check if the source file exists
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")

    # Copy the README.md file
    shutil.copy2(source, destination)

    # Notify that the files have been synchronized
    print(f"Synchronized {source} to {destination}")

if __name__ == '__main__':
    sync_readme()