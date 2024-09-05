import os
import webbrowser
import sys

def open_docs(page=None):
    """Open the documentation in the default web browser.

    :param page: The specific page to open. If None, opens the index page.
    :type page: str, optional
    """
    docs_path = os.path.join(os.path.dirname(__file__), 'build', 'html') 
    if page:
        file_path = os.path.join(docs_path, f"{page}.html")
    else:
        file_path = os.path.join(docs_path, 'index.html')

    if os.path.exists(file_path):
        webbrowser.open('file://' + os.path.realpath(file_path))
    else:
        print(f"Documentation not found. Please build it first by runnning `python docs/update_docs.py`") 
        if page:
            print(f"Also, make sure the page '{page}' exists in the documentation.")

if __name__ == "__main__":
    page = sys.argv[1] if len(sys.argv) > 1 else None
    open_docs(page)
