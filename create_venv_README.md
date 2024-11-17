# Python Virtual Environment Creator

A powerful and user-friendly tool for creating and managing Python virtual environments across Windows, Linux, and macOS platforms.

## Overview

The Python Virtual Environment Creator simplifies the process of setting up virtual environments for Python projects. It offers an interactive command-line interface that guides users through environment creation, package installation, and dependency management.

## Features

- **Cross-Platform Compatibility**: Works seamlessly on Windows, Linux, and macOS
- **Automatic Python Detection**: Finds installed Python versions in standard system locations
- **Interactive Setup Process**: User-friendly prompts guide you through the entire setup
- **Virtual Environment Management**: Creates and configures virtual environments
- **Package Management**:
  - Installs dependencies from requirements.txt
  - Supports local dependency installation (.whl, .tar.gz, .zip)
  - Creates new requirements.txt if needed
- **Flexible Configuration**: Customizable project paths and environment names

## Prerequisites

- Python 3.6 or higher
- Basic command-line knowledge
- Sufficient disk space for packages

## Installation

1. **Clone the Repository**:
   ```bash
   git clone [repository-url]
   cd [repository-name]
   ```

2. **Project Structure**:
   ```
   project_root/
   ├── venv_creator.py
   ├── requirements.txt (optional)
   └── dependencies/ (optional)
       ├── package1.whl
       ├── package2.tar.gz
       └── package3.zip
   ```

3. **Run the Script**:
   ```bash
   python venv_creator.py
   ```

## Usage

1. **Run the Tool**:
   - Execute the script
   - Select Python installation from detected versions
   - Follow interactive prompts

2. **Project Setup**:
   - Enter project name
   - Specify project path
   - Choose virtual environment name
   - Configure dependency options

3. **Final Directory Structure**:
   ```
   your_project/
   ├── venv/ (or chosen name)
   │   ├── Scripts/ (Windows)
   │   ├── bin/ (Linux/macOS)
   │   └── lib/
   ├── requirements.txt
   └── dependencies/
   ```

## Example Usage

```bash
=== Python Virtual Environment Setup (Windows) ===

Found Python installations:
1. C:\Users\Username\AppData\Local\Programs\Python\Python39\python.exe - Python 3.9.x
2. C:\Program Files\Python39\python.exe - Python 3.9.x

Select Python installation (enter number): 1

Enter project name: MyProject
Enter full project path: C:\path\to\project
Enter virtual environment name: venv

Creating virtual environment...
```

## Activation Instructions

### Windows
```bash
cd your_project_path
venv\Scripts\activate
```

### Linux/macOS
```bash
cd your_project_path
source venv/bin/activate
```

## Common Commands
- `pip list` - View installed packages
- `pip freeze > requirements.txt` - Save package list
- `deactivate` - Exit virtual environment

## Functions Overview

- **get_current_username**: Retrieves current username
- **find_python_installations**: Locates Python installations
- **create_venv**: Creates virtual environment
- **install_requirements**: Handles package installation
- **get_project_details**: Manages user input
- **print_activation_instructions**: Shows activation commands

## Troubleshooting

1. **Python Not Found**
   - Verify Python installation
   - Check system PATH
   - Use full Python path

2. **Permission Issues**
   - Run as administrator (Windows)
   - Use sudo (Linux/macOS)
   - Verify directory permissions

3. **Package Installation Fails**
   - Check internet connection
   - Verify package names
   - Review dependency conflicts

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for enhancements or bug fixes.

License
This is a private project created and maintained by Hezekiah Jenkins. All rights reserved.

Not intended for distribution or commercial use without explicit permission.

## Support

For issues or inquiries:
- Open an issue in the repository
- Contact the maintainer
- [Your contact information]

---

This tool aims to streamline Python virtual environment management across all platforms. For additional support or questions, please refer to the documentation or contact the development team.