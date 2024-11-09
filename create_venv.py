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
        python_installations = []
        
        # Search in AppData location
        appdata_path = f"C:\\Users\\{self.username}\\AppData\\Local\\Programs\\Python\\Python*\\python.exe"
        python_installations.extend(glob.glob(appdata_path))
        
        # Search in Program Files
        program_files_paths = [
            "C:\\Program Files\\Python*\\python.exe",
            "C:\\Program Files (x86)\\Python*\\python.exe"
        ]
        for path in program_files_paths:
            python_installations.extend(glob.glob(path))
        
        return python_installations

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
            result = subprocess.run([python_path, '--version'], 
                                  capture_output=True, 
                                  text=True)
            return result.stdout.strip()
        except Exception:
            return "Version unknown"

    def create_venv(self, python_path, venv_path):
        """Create virtual environment using specified Python installation"""
        try:
            subprocess.run([python_path, '-m', 'venv', venv_path], 
                          check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return False

    def install_requirements(self, venv_path, requirements_path=None):
        """Install requirements if requirements.txt exists"""
        if not requirements_path or not os.path.exists(requirements_path):
            return None

        pip_path = os.path.join(venv_path, 
                               'Scripts' if self.is_windows else 'bin',
                               'pip' + ('.exe' if self.is_windows else ''))
        
        try:
            print("\nInstalling requirements...")
            subprocess.run([pip_path, 'install', '-r', requirements_path], 
                         check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            return False

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
        
        # Display found Python installations
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