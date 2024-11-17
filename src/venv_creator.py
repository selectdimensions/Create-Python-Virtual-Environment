import os
import subprocess
import glob
import sys
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union


class VenvCreator:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == 'windows'
        self.is_linux = self.os_type in ['linux', 'darwin']
        self.python_installations: List[str] = []
        self.username = self.get_current_username()
        self.dependencies_folder: Optional[str] = None

    def set_dependencies_folder(self, folder_path: str) -> bool:
        """Set the dependencies folder path"""
        folder_path = os.path.expanduser(folder_path)
        if os.path.exists(folder_path):
            self.dependencies_folder = folder_path
            return True
        return False

    def find_dependencies(self) -> List[str]:
        """Find all dependency files in the dependencies folder"""
        if not self.dependencies_folder:
            return []
        
        dependency_files = []
        extensions = ['.whl', '.tar.gz', '.zip']
        for ext in extensions:
            dependency_files.extend(glob.glob(os.path.join(self.dependencies_folder, f'*{ext}')))
        return sorted(dependency_files)

    def install_local_dependencies(self, venv_path: str) -> Optional[bool]:
        """Install dependencies from local folder"""
        if not self.dependencies_folder:
            return None

        pip_path = self._get_pip_path(venv_path)
        dependencies = self.find_dependencies()

        if not dependencies:
            print("No dependency files found in the specified folder.")
            return False

        try:
            print("\nInstalling local dependencies...")
            for dep in dependencies:
                dep_name = os.path.basename(dep)
                print(f"Installing {dep_name}")
                result = subprocess.run(
                    [pip_path, 'install', dep],
                    check=True,
                    capture_output=True,
                    text=True
                )
                if result.stderr:
                    print(f"Warning during installation: {result.stderr}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing local dependencies: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False

    def get_current_username(self) -> Optional[str]:
        """Get current username based on OS"""
        return os.getenv('USERNAME' if self.is_windows else 'USER')

    def _get_pip_path(self, venv_path: str) -> str:
        """Get the pip executable path for the virtual environment"""
        return os.path.join(
            venv_path,
            'Scripts' if self.is_windows else 'bin',
            'pip' + ('.exe' if self.is_windows else '')
        )

    def find_python_installations(self) -> List[str]:
        """Find Python installations based on OS"""
        return self._find_windows_python() if self.is_windows else self._find_linux_python()

    def _find_windows_python(self) -> List[str]:
        """Find Python installations on Windows"""
        installations_with_versions: List[Tuple[str, str, Tuple[int, ...]]] = []
        search_paths = [
            f"C:\\Users\\{self.username}\\AppData\\Local\\Programs\\Python\\Python*\\python.exe",
            "C:\\Program Files\\Python*\\python.exe",
            "C:\\Program Files (x86)\\Python*\\python.exe"
        ]
        
        for search_path in search_paths:
            for path in glob.glob(search_path):
                version = self.get_python_version(path)
                try:
                    version_numbers = version.replace("Python ", "").split(".")
                    version_tuple = tuple(int(num) for num in version_numbers)
                    installations_with_versions.append((path, version, version_tuple))
                except (ValueError, AttributeError):
                    continue

        return [installation[0] for installation in 
                sorted(installations_with_versions, key=lambda x: x[2])]

    def _find_linux_python(self) -> List[str]:
        """Find Python installations on Linux/Unix"""
        search_paths = [
            "/usr/bin/python3*",
            "/usr/local/bin/python3*",
            f"/home/{self.username}/.local/bin/python3*"
        ]

        python_installations = set()
        for path_pattern in search_paths:
            for path in glob.glob(path_pattern):
                if os.path.isfile(path) and not os.path.islink(path):
                    python_installations.add(path)

        return sorted(python_installations)

    def get_python_version(self, python_path: str) -> str:
        """Get Python version for a given Python executable"""
        try:
            result = subprocess.run(
                [python_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except (subprocess.SubprocessError, OSError):
            return "Version unknown"

    def create_venv(self, python_path: str, venv_path: str) -> bool:
        """Create virtual environment using specified Python installation"""
        try:
            result = subprocess.run(
                [python_path, '-m', 'venv', venv_path],
                check=True,
                capture_output=True,
                text=True
            )
            if result.stderr:
                print(f"Warning during venv creation: {result.stderr}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False

    def install_requirements(self, venv_path: str, requirements_path: Optional[str] = None) -> Optional[bool]:
        """Install requirements if requirements.txt exists"""
        if not requirements_path or not os.path.exists(requirements_path):
            return None

        project_root = os.path.dirname(requirements_path)
        temp_requirements = os.path.join(project_root, 'temp_requirements.txt')

        try:
            missing_files = []
            with open(requirements_path, 'r') as original:
                with open(temp_requirements, 'w') as temp:
                    for line in original:
                        line = line.strip()
                        if line.startswith('dependencies/'):
                            absolute_path = os.path.abspath(os.path.join(project_root, line))
                            if not os.path.exists(absolute_path):
                                missing_files.append(line)
                                print(f"Warning: Required file not found: {line}")
                                print(f"Expected location: {absolute_path}")
                            elif os.path.getsize(absolute_path) == 0:
                                print(f"Warning: File exists but is empty: {line}")
                                missing_files.append(line)
                            else:
                                temp.write(f"{absolute_path}\n")
                        else:
                            temp.write(f"{line}\n")

            if missing_files:
                print("\nMissing or invalid dependency files:")
                for file in missing_files:
                    print(f"- {file}")
                return False

            pip_path = self._get_pip_path(venv_path)
            print("\nInstalling requirements...")
            result = subprocess.run(
                [pip_path, 'install', '-r', temp_requirements],
                check=True,
                capture_output=True,
                text=True
            )
            if result.stderr:
                print(f"Warnings during installation: {result.stderr}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            return False
        except Exception as e:
            print(f"Unexpected error during requirements installation: {e}")
            return False
        finally:
            if os.path.exists(temp_requirements):
                os.remove(temp_requirements)

    def get_project_details(self) -> Dict[str, str]:
        """Get project details from user"""
        project_details: Dict[str, str] = {}

        project_details['name'] = input("\nEnter project name: ").strip()

        while True:
            project_path = os.path.expanduser(input("Enter full project path: ").strip().strip('"'))
            if os.path.exists(project_path):
                project_details['path'] = project_path
                break
            create_dir = input("Directory doesn't exist. Create it? (y/n): ").lower()
            if create_dir == 'y':
                try:
                    os.makedirs(project_path)
                    project_details['path'] = project_path
                    break
                except OSError as e:
                    print(f"Error creating directory: {e}")

        while True:
            venv_name = input("Enter virtual environment name (e.g., venv, .venv): ").strip()
            if venv_name:
                project_details['venv_name'] = venv_name
                break
            print("Virtual environment name cannot be empty.")

        if input("Do you want to install dependencies from a local folder? (y/n): ").lower() == 'y':
            while True:
                deps_path = os.path.expanduser(input("Enter dependencies folder path: ").strip().strip('"'))
                if self.set_dependencies_folder(deps_path):
                    project_details['dependencies_path'] = deps_path
                    break
                print("Invalid dependencies folder path. Please try again.")

        requirements_path = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            project_details['requirements_path'] = requirements_path
            print(f"Found requirements.txt at: {requirements_path}")
        elif input("No requirements.txt found. Create one? (y/n): ").lower() == 'y':
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

    def print_activation_instructions(self, project_path: str, venv_name: str) -> None:
        """Print OS-specific activation instructions"""
        print("\nTo activate the virtual environment:")
        
        activation_cmd = f"source {venv_name}/bin/activate"
        if self.is_windows:
            activation_cmd = f"{venv_name}\\Scripts\\activate"

        print(f"cd {project_path}")
        print(activation_cmd)

        print("\nUseful commands:")
        print("pip list            - Show installed packages")
        print("pip freeze         - List installed packages in requirements format")
        print("pip check          - Verify dependencies have compatible versions")
        print("deactivate         - Exit virtual environment")

    def run(self) -> None:
        """Main execution method"""
        print(f"\n=== Python Virtual Environment Setup ({self.os_type.capitalize()}) ===")

        installations = self.find_python_installations()
        if not installations:
            print("No Python installations found!")
            return

        print("\nFound Python installations:")
        for i, path in enumerate(installations, 1):
            version = self.get_python_version(path)
            print(f"{i}. {path} - {version}")

        while True:
            try:
                choice = int(input("\nSelect Python installation (enter number): ")) - 1
                if 0 <= choice < len(installations):
                    selected_python = installations[choice]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

        project_details = self.get_project_details()
        venv_path = os.path.join(project_details['path'], project_details['venv_name'])

        if os.path.exists(venv_path):
            if input(f"\nVirtual environment already exists at {venv_path}. Overwrite? (y/n): ").lower() == 'y':
                shutil.rmtree(venv_path)
            else:
                print("Operation cancelled.")
                return

        print(f"\nCreating virtual environment using {selected_python}")
        print(f"Location: {venv_path}")

        if self.create_venv(selected_python, venv_path):
            print("\nVirtual environment created successfully!")

            if self.dependencies_folder:
                result = self.install_local_dependencies(venv_path)
                if result:
                    print("Local dependencies installed successfully!")
                elif result is False:
                    print("Failed to install local dependencies.")

            if 'requirements_path' in project_details:
                result = self.install_requirements(venv_path, project_details['requirements_path'])
                if result:
                    print("Requirements installed successfully!")
                elif result is False:
                    print("Failed to install requirements.")

            self.print_activation_instructions(project_details['path'], project_details['venv_name'])
        else:
            print("\nFailed to create virtual environment.")


def main():
    venv_creator = VenvCreator()
    venv_creator.run()


if __name__ == "__main__":
    main()