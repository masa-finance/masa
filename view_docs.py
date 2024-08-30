import os
import webbrowser

def open_docs():
    docs_path = os.path.join(os.path.dirname(__file__), 'docs', 'build', 'html', 'index.html')
    if os.path.exists(docs_path):
        webbrowser.open('file://' + os.path.realpath(docs_path))
    else:
        print("Documentation not found. Please build it first using 'cd docs && make html'")

if __name__ == "__main__":
    open_docs()
