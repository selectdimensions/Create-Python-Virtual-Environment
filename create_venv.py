"""
I WANT TO ADD ALL OF THESE BUT I KNOW THIS IS A HUGE LEAP
Add logging functionality for better debugging
Include a way to specify Python version requirements
Add support for pip.conf/pip.ini configuration
Include option to upgrade pip in new environments
Add support for conda environments
"""
import os
import subprocess
import glob
import sys
import platform
import shutil
from pathlib import Path


class VenvCreator:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type in ['linux', 'darwin']  # darwin is macOS
        self.python_installations = []
        self.username = self.get_current_username()
        self.dependencies_folder = None

    def set_dependencies_folder(self, folder_path):
        """Set the dependencies folder path"""
        if os.path.exists(folder_path):
            self.dependencies_folder = folder_path
            return True
        return False

    def find_dependencies(self):
        """Find all dependency files in the dependencies folder"""
        if not self.dependencies_folder:
            return []
        
        dependency_files = []
        for ext in ['.whl', '.tar.gz', '.zip']:
            dependency_files.extend(glob.glob(os.path.join(self.dependencies_folder, f'*{ext}')))
        return dependency_files

    def install_local_dependencies(self, venv_path):
        """Install dependencies from local folder"""
        if not self.dependencies_folder:
            return None

        pip_path = os.path.join(venv_path, 'Scripts' if self.is_windows else 'bin', 'pip' + ('.exe' if self.is_windows else ''))
        dependencies = self.find_dependencies()

        if not dependencies:
            print("No dependency files found in the specified folder.")
            return False

        try:
            print("\nInstalling local dependencies...")
            for dep in dependencies:
                print(f"Installing {os.path.basename(dep)}")
                subprocess.run([pip_path, 'install', dep], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing local dependencies: {e}")
            return False

    def get_current_username(self):
        """Get current username based on OS"""
        if self.is_windows:
            return os.getenv('USERNAME')
        return os.getenv('USER')

    def find_python_installations(self):
        """Find Python installations based on OS"""
        if self.is_windows:
            return self._find_windows_python()
        return self._find_linux_python()

    def _find_windows_python(self):
        """Find Python installations on Windows"""
        installations_with_versions = []
        
        # Search in AppData location
        appdata_path = f"C:\\Users\\{self.username}\\AppData\\Local\\Programs\\Python\\Python*\\python.exe"
        program_files_paths = [
            "C:\\Program Files\\Python*\\python.exe",
            "C:\\Program Files (x86)\\Python*\\python.exe"
        ]
        
        # Collect all potential paths
        all_paths = []
        all_paths.extend(glob.glob(appdata_path))
        for path in program_files_paths:
            all_paths.extend(glob.glob(path))

        # Create list with version information for sorting
        for path in all_paths:
            version = self.get_python_version(path)
            try:
                # Extract version numbers from string like "Python 3.10.11"
                version_numbers = version.replace("Python ", "").split(".")
                version_tuple = tuple(int(num) for num in version_numbers)
                installations_with_versions.append((path, version, version_tuple))
            except Exception:
                continue

        # Sort by version tuple
        sorted_installations = sorted(installations_with_versions, key=lambda x: x[2])
        # Return only the paths in sorted order
        return [installation[0] for installation in sorted_installations]

    def _find_linux_python(self):
        """Find Python installations on Linux/Unix"""
        python_installations = []

        # Common Linux Python locations
        linux_paths = [
            "/usr/bin/python3*",
            "/usr/local/bin/python3*",
            f"/home/{self.username}/.local/bin/python3*"
        ]

        for path in linux_paths:
            found_paths = glob.glob(path)
            # Filter out symbolic links and keep only actual executables
            for p in found_paths:
                if os.path.isfile(p) and not os.path.islink(p):
                    python_installations.append(p)

        return sorted(set(python_installations))  # Remove duplicates

    def get_python_version(self, python_path):
        """Get Python version for a given Python executable"""
        try:
            result = subprocess.run([python_path, '--version'], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return "Version unknown"

    def create_venv(self, python_path, venv_path):
        """Create virtual environment using specified Python installation"""
        try:
            subprocess.run([python_path, '-m', 'venv', venv_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return False

    def install_requirements(self, venv_path, requirements_path=None):
        """Install requirements if requirements.txt exists"""
            # This version:
            # Checks if each dependency file exists before attempting installation
            # Maintains a list of missing files
            # Verifies that existing files are not empty
            # Provides detailed error messages showing:
            # Which files are missing
            # The expected location of missing files
            # Only proceeds with installation if all required files are present
            # Handles both general exceptions and specific pip installation errors
            # Provides more detailed feedback about the installation process

        if not requirements_path or not os.path.exists(requirements_path):
            return None

        # Get the project root directory (where requirements.txt is located)
        project_root = os.path.dirname(requirements_path)

        # Create a temporary requirements file with absolute paths
        temp_requirements = os.path.join(project_root, 'temp_requirements.txt')

        try:
            missing_files = []
            with open(requirements_path, 'r') as original:
                with open(temp_requirements, 'w') as temp:
                    for line in original:
                        line = line.strip()
                        if line.startswith('dependencies/'):
                            # Convert relative path to absolute path
                            relative_path = line
                            absolute_path = os.path.abspath(os.path.join(project_root, line))

                            # Check if file exists
                            if not os.path.exists(absolute_path):
                                missing_files.append(relative_path)
                                print(f"Warning: Required file not found: {relative_path}")
                                print(f"Expected location: {absolute_path}")
                            else:
                                # Verify if it's a valid file
                                if os.path.getsize(absolute_path) == 0:
                                    print(f"Warning: File exists but appears to be empty: {relative_path}")
                                temp.write(f"{absolute_path}\n")
                        else:
                            temp.write(f"{line}\n")

            if missing_files:
                print("\nMissing dependency files:")
                for file in missing_files:
                    print(f"- {file}")
                return False

            pip_path = os.path.join(venv_path, 'Scripts' if self.is_windows else 'bin', 'pip' + ('.exe' if self.is_windows else ''))

            print("\nAll dependency files found. Installing requirements...")
            subprocess.run([pip_path, 'install', '-r', temp_requirements], check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during requirements installation: {e}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(temp_requirements):
                os.remove(temp_requirements)

    def get_project_details(self):
        """Get project details from user"""
        project_details = {}

        # Get project name
        project_details['name'] = input("\nEnter project name: ").strip()

        # Get project path
        while True:
            project_path = input("Enter full project path: ").strip().strip('"')
            if os.path.exists(project_path):
                project_details['path'] = project_path
                break
            create_dir = input("Directory doesn't exist. Create it? (y/n): ").lower()
            if create_dir == 'y':
                try:
                    os.makedirs(project_path)
                    project_details['path'] = project_path
                    break
                except Exception as e:
                    print(f"Error creating directory: {e}")

        # Get virtual environment name
        while True:
            venv_name = input("Enter virtual environment name (e.g., venv, .venv, project-env): ").strip()
            if venv_name:
                project_details['venv_name'] = venv_name
                break
            print("Virtual environment name cannot be empty.")

        # Ask about dependencies folder
        use_deps = input("Do you want to install dependencies from a local folder? (y/n): ").lower()
        if use_deps == 'y':
            while True:
                deps_path = input("Enter dependencies folder path: ").strip().strip('"')
                if self.set_dependencies_folder(deps_path):
                    project_details['dependencies_path'] = deps_path
                    break
                print("Invalid dependencies folder path. Please try again.")

        # Handle requirements.txt
        requirements_path = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            project_details['requirements_path'] = requirements_path
            print(f"Found requirements.txt at: {requirements_path}")
        else:
            create_req = input("No requirements.txt found. Create one? (y/n): ").lower()
            if create_req == 'y':
                project_details['create_requirements'] = True
                print("\nEnter package names (one per line, press Enter twice when done):")
                packages = []
                while True:
                    package = input().strip()
                    if not package:
                        break
                    packages.append(package)
                if packages:
                    with open(requirements_path, 'w') as f:
                        f.write('\n'.join(packages))
                    project_details['requirements_path'] = requirements_path

        return project_details

    def print_activation_instructions(self, project_path, venv_name):
        """Print OS-specific activation instructions"""
        print("\nTo activate the virtual environment:")

        if self.is_windows:
            print(f"cd {project_path}")
            print(f"{venv_name}\\Scripts\\activate")
        else:
            print(f"cd {project_path}")
            print(f"source {venv_name}/bin/activate")

        print("\nAdditional commands:")
        print("pip list - Show installed packages")
        print("pip freeze > requirements.txt - Update requirements file")
        print("deactivate - Exit virtual environment")

    def run(self):
        """Main execution method"""
        print(f"\n=== Python Virtual Environment Setup ({self.os_type.capitalize()}) ===")

        # Find Python installations
        installations = self.find_python_installations()
        if not installations:
            print("No Python installations found!")
            return

        # Display found Python installations in sorted order
        print("\nFound Python installations:")
        for i, path in enumerate(installations, 1):
            version = self.get_python_version(path)
            print(f"{i}. {path} - {version}")

        # Get user selection for Python version
        while True:
            try:
                choice = int(input("\nSelect Python installation (enter number): ")) - 1
                if 0 <= choice < len(installations):
                    selected_python = installations[choice]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        # Get project details
        project_details = self.get_project_details()

        # Create virtual environment path
        venv_path = os.path.join(project_details['path'], project_details['venv_name'])

        # Check if venv already exists
        if os.path.exists(venv_path):
            overwrite = input(f"\nVirtual environment already exists at {venv_path}. Overwrite? (y/n): ").lower()
            if overwrite == 'y':
                shutil.rmtree(venv_path)
            else:
                print("Operation cancelled.")
                return

        # Create virtual environment
        print(f"\nCreating virtual environment using {selected_python}")
        print(f"Location: {venv_path}")

        if self.create_venv(selected_python, venv_path):
            print("\nVirtual environment created successfully!")

            # Install local dependencies if specified
            if self.dependencies_folder:
                result = self.install_local_dependencies(venv_path)
                if result:
                    print("Local dependencies installed successfully!")
                elif result is False:
                    print("Failed to install local dependencies.")

            # Install requirements if they exist
            if 'requirements_path' in project_details:
                result = self.install_requirements(venv_path, project_details['requirements_path'])
                if result:
                    print("Requirements installed successfully!")
                elif result is False:
                    print("Failed to install requirements.")

            # Print activation instructions
            self.print_activation_instructions(project_details['path'], project_details['venv_name'])
        else:
            print("\nFailed to create virtual environment.")

def main():
    venv_creator = VenvCreator()
    venv_creator.run()

if __name__ == "__main__":
    main()
