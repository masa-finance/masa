import os
import webbrowser
import sys
from pathlib import Path

def open_docs(page=None):
    """Open the documentation in the default web browser."""
    # Get the path to the docs directory
    docs_path = Path(__file__).resolve().parent
    
    # The HTML files are typically in the 'build/html' directory
    html_path = docs_path / 'build' / 'html'

    if page:
        file_path = html_path / f"{page}.html"
    else:
        file_path = html_path / 'index.html'

    if file_path.exists():
        webbrowser.open(file_path.as_uri())
    else:
        print(f"Error: Documentation file not found: {file_path}")
        print("Please ensure the documentation has been built correctly.")

if __name__ == "__main__":
    page = sys.argv[1] if len(sys.argv) > 1 else None
    open_docs(page)
