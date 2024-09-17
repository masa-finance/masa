import sys
from masa_ai.masa import main as masa_main

def main():
    """
    The main entry point for the masa-ai-cli command.

    This function calls the `main` function from the `masa` module,
    passing any command-line arguments provided.

    :return: The exit status of the `main` function.
    """
    sys.exit(masa_main(*sys.argv[1:]))

if __name__ == '__main__':
    """
    Run the `main` function when this script is executed directly.
    """
    main()
