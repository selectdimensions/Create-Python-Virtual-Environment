# VenvCreator: Python Virtual Environment Setup Tool

## Overview
`VenvCreator` is a Python script designed to simplify the creation and management of virtual environments across different operating systems (Windows, Linux, and macOS). This tool helps users find their Python installations, create a virtual environment, and install dependencies specified in a `requirements.txt` file.

## Features
- Automatically detects Python installations on the user's system.
- Supports creating virtual environments with user-defined names.
- Installs packages from a `requirements.txt` file if it exists or prompts the user to create one.
- Provides OS-specific instructions for activating the virtual environment.
- Handles existing virtual environments, allowing users to overwrite if desired.

## Requirements
- Python 3.x installed on your system.
- Access to the command line interface.

## Installation
1. Clone or download the repository containing the script.
2. Ensure you have Python 3.x installed on your machine.

## Usage
To run the script, execute the following command in your terminal or command prompt:

```bash
python venv_creator.py
```

### Steps
1. The script will automatically detect your operating system.
2. It will search for available Python installations.
3. You will be prompted to select a Python installation.
4. Provide project details, including project name, path, virtual environment name, and package requirements.
5. The script will create the virtual environment and install required packages if specified.
6. Finally, it will print instructions on how to activate the virtual environment.

## Functions

### `get_current_username()`
Retrieves the current username based on the operating system.

### `find_python_installations()`
Discovers available Python installations based on the user's operating system.

### `create_venv(python_path, venv_path)`
Creates a virtual environment using the specified Python executable.

### `install_requirements(venv_path, requirements_path)`
Installs packages listed in the `requirements.txt` file located at the specified path.

### `get_project_details()`
Prompts the user for project details, including project name, path, virtual environment name, and package requirements.

### `print_activation_instructions(project_path, venv_name)`
Displays instructions on how to activate the virtual environment based on the operating system.

### `run()`
The main execution method that orchestrates the entire process of setting up the virtual environment.

## Example Workflow
1. Run the script.
2. Select a Python installation from the list provided.
3. Enter the project name and path. If the path does not exist, you will have the option to create it.
4. Specify a name for the virtual environment.
5. If a `requirements.txt` file is found, it will be used to install dependencies; otherwise, you can create one by entering package names.
6. Follow the printed instructions to activate your virtual environment.

## Notes
- Ensure you have the necessary permissions to create directories and install packages.
- If the virtual environment already exists, you will be prompted to overwrite or cancel the operation.

## Contributing
Contributions are welcome! If you have suggestions or improvements, please submit a pull request or open an issue in the repository.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any questions or support, please reach out to the maintainer via the project's GitHub page.
```
