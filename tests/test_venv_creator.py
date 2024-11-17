"""
_summary_
"""
import os
import sys
import platform
import subprocess
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typing import List, Dict

# Import the VenvCreator class
from venv_creator import VenvCreator

class TestVenvCreator(unittest.TestCase):
    """
    _summary_
    """
    def setUp(self):
        """Set up test environment before each test"""
        self.venv_creator = VenvCreator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_requirements = os.path.join(self.temp_dir, 'requirements.txt')
        self.test_dependencies = os.path.join(self.temp_dir, 'dependencies')
        os.makedirs(self.test_dependencies)

    def tearDown(self):
        """Clean up test environment after each test"""
        shutil.rmtree(self.temp_dir)

    def create_test_wheel(self, name: str = "test_package-1.0-py3-none-any.whl"):
        """Helper method to create a dummy wheel file"""
        wheel_path = os.path.join(self.test_dependencies, name)
        with open(wheel_path, 'w') as f:
            f.write('dummy wheel file')
        return wheel_path

    def test_init(self):
        """Test initialization of VenvCreator"""
        self.assertEqual(self.venv_creator.os_type, platform.system().lower())
        self.assertEqual(self.venv_creator.is_windows, platform.system().lower() == 'windows')
        self.assertEqual(self.venv_creator.is_linux, platform.system().lower() in ['linux', 'darwin'])

    def test_set_dependencies_folder(self):
        """Test setting dependencies folder"""
        # Test with valid path
        self.assertTrue(self.venv_creator.set_dependencies_folder(self.test_dependencies))
        self.assertEqual(self.venv_creator.dependencies_folder, self.test_dependencies)

        # Test with invalid path
        invalid_path = os.path.join(self.temp_dir, 'nonexistent')
        self.assertFalse(self.venv_creator.set_dependencies_folder(invalid_path))

    def test_find_dependencies(self):
        """Test finding dependency files"""
        # Create test wheel files
        wheel1 = self.create_test_wheel("package1-1.0-py3-none-any.whl")
        wheel2 = self.create_test_wheel("package2-1.0-py3-none-any.whl")
        targz = os.path.join(self.test_dependencies, "package3-1.0.tar.gz")
        with open(targz, 'w') as f:
            f.write('dummy targz file')

        self.venv_creator.set_dependencies_folder(self.test_dependencies)
        dependencies = self.venv_creator.find_dependencies()
        
        self.assertEqual(len(dependencies), 3)
        self.assertIn(wheel1, dependencies)
        self.assertIn(wheel2, dependencies)
        self.assertIn(targz, dependencies)

    @patch('subprocess.run')
    def test_install_local_dependencies(self, mock_run):
        """Test installing local dependencies"""
        mock_run.return_value = MagicMock(stderr="", returncode=0)
        self.create_test_wheel()
        
        venv_path = os.path.join(self.temp_dir, 'venv')
        os.makedirs(venv_path)
        
        self.venv_creator.set_dependencies_folder(self.test_dependencies)
        result = self.venv_creator.install_local_dependencies(venv_path)
        
        self.assertTrue(result)
        mock_run.assert_called()

    def test_get_python_version(self):
        """Test getting Python version"""
        current_python = sys.executable
        version = self.venv_creator.get_python_version(current_python)
        self.assertIn('Python', version)

    @patch('subprocess.run')
    def test_create_venv(self, mock_run):
        """Test creating virtual environment"""
        mock_run.return_value = MagicMock(stderr="", returncode=0)
        
        venv_path = os.path.join(self.temp_dir, 'venv')
        result = self.venv_creator.create_venv(sys.executable, venv_path)
        
        self.assertTrue(result)
        mock_run.assert_called_once()

    def test_get_project_details(self):
        """Test getting project details with mocked input"""
        test_inputs = [
            'test_project',  # project name
            self.temp_dir,   # project path
            'venv',          # venv name
            'n',            # install dependencies?
            'n'             # create requirements.txt?
        ]
        
        with patch('builtins.input', side_effect=test_inputs):
            details = self.venv_creator.get_project_details()
        
        self.assertEqual(details['name'], 'test_project')
        self.assertEqual(details['path'], self.temp_dir)
        self.assertEqual(details['venv_name'], 'venv')

    @patch('subprocess.run')
    def test_install_requirements(self, mock_run):
        """Test installing requirements"""
        mock_run.return_value = MagicMock(stderr="", returncode=0)
        
        # Create test requirements file
        with open(self.test_requirements, 'w') as f:
            f.write('requests==2.26.0\ndjango==3.2.5')
        
        venv_path = os.path.join(self.temp_dir, 'venv')
        os.makedirs(venv_path)
        
        result = self.venv_creator.install_requirements(venv_path, self.test_requirements)
        
        self.assertTrue(result)
        mock_run.assert_called_once()

    def test_find_python_installations(self):
        """Test finding Python installations"""
        installations = self.venv_creator.find_python_installations()
        self.assertIsInstance(installations, list)
        if installations:
            self.assertTrue(all(os.path.exists(path) for path in installations))

    @patch('builtins.print')
    def test_print_activation_instructions(self, mock_print):
        """Test printing activation instructions"""
        project_path = "/test/path"
        venv_name = "venv"
        
        self.venv_creator.print_activation_instructions(project_path, venv_name)
        mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()