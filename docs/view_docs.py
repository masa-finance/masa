import os
import webbrowser
import sys
import subprocess

def build_docs():
    """Build the documentation using update_docs.py"""
    update_docs_path = os.path.join(os.path.dirname(__file__), 'update_docs.py')
    subprocess.run([sys.executable, update_docs_path])

def open_docs(page=None):
    """Open the documentation in the default web browser."""
    docs_path = os.path.join(os.path.dirname(__file__), 'build', 'html') 
    if page:
        file_path = os.path.join(docs_path, f"{page}.html")
    else:
        file_path = os.path.join(docs_path, 'index.html')

    if not os.path.exists(file_path):
        print("Documentation not found. Building docs...")
        build_docs()
    
    if os.path.exists(file_path):
        webbrowser.open('file://' + os.path.realpath(file_path))
    else:
        print(f"Error: Documentation build failed or {file_path} not found.")
        print("Please run 'python docs/update_docs.py' manually and check for errors.")

if __name__ == "__main__":
    page = sys.argv[1] if len(sys.argv) > 1 else None
    open_docs(page)
