"""
Setup configuration for the MASA package.

This script specifies the package metadata, dependencies, and entry points
for the MASA (Multi-Agent System Architecture) project. It uses setuptools
to define the package structure and requirements.

The MASA package includes tools for data retrieval, quality control, and
various utilities for building multi-agent systems.
"""

from setuptools import setup, find_packages, Command
import os

class ViewDocsCommand(Command):
    description = 'View the documentation in the default web browser'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import webbrowser
        docs_path = os.path.join(os.path.dirname(__file__), 'docs', 'build', 'html', 'index.html')
        if os.path.exists(docs_path):
            webbrowser.open('file://' + os.path.realpath(docs_path))
        else:
            print("Documentation not found. Please build it first using 'cd docs && make html'")

setup(
    name='masa',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Core dependencies
        'pyyaml',
        'requests',
        'numpy',
        'pandas',
        'python-dotenv',
        'tqdm',
        'colorlog',
        'dynaconf',

        # Data processing and machine learning
        'scikit-learn',
        'torch',
        'transformers',

        # Web and API
        'streamlit',
        'streamlit-extras',
        'TikTokApi',

        # Language models and AI
        'langchain',
        'langchain_community',
        'langchain-openai',
        'langchainhub',
        'langchain-ollama',
        'openai',
        'tiktoken',
        'nomic[local]',
        'ollama',

        # Vector databases and embeddings
        'pinecone-client[grpc]',

        # Visualization and notebooks
        'matplotlib',
        'jupyter',
        'notebook',
        'ipykernel',

        # Documentation
        'sphinx',
        'sphinx_rtd_theme',
        'recommonmark',
        'myst-parser',

        # Database
        'psycopg2',

        # Miscellaneous
        'feedparser',
        'tavily-python',
        'langgraph',
        'assemblyai',
        'pytube',
    ],
    entry_points={
        'console_scripts': [
            'masa=masa.masa:main',
        ],
    },
    cmdclass={
        'view_docs': ViewDocsCommand,
    },
)