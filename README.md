# MASA Project Setup

This project uses a combination of Conda and pip to manage dependencies and create a virtual environment.

## Prerequisites

Before setting up the project, ensure that you have the following installed:

- Anaconda or Miniconda: The project relies on Conda for managing the virtual environment. You can download Anaconda or Miniconda from the official website: [https://www.anaconda.com/products/individual](https://www.anaconda.com/products/individual)

## Setup Instructions

1. Clone the repository to your local machine.

2. Navigate to the project directory.

3. Run the following command to initialize the project:

   ```bash
   masa-init
   ```

   This command will create the necessary folder structure, set up the Conda environment, and install the required dependencies.

4. Once the initialization is complete, activate the Conda environment by running:

   ```bash
   conda activate masa
   ```

5. You are now ready to use the MASA package!

## Configuration Files

The project setup is defined in the following configuration files:

- `setup.py`: Specifies the package details, dependencies, and entry points for the MASA package.
- `init_script.py`: Contains the initialization script that sets up the project structure and creates the Conda environment.
- `environment.yml`: Defines the Conda environment and its dependencies.
- `requirements.txt`: Lists the additional Python packages required by the project.

Make sure to review these files if you need to modify the project setup or dependencies.

## Additional Notes

- The project requires Python 3.12, which will be installed in the Conda environment.
- The initialization script will create a Conda environment named `masa` based on the specifications in `environment.yml`.
- The required Python packages listed in `requirements.txt` will be automatically installed during the initialization process.

If you encounter any issues during the setup or have any questions, please refer to the project documentation or contact the project maintainers.
