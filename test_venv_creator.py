import pytest
import os
from create_venv import VenvCreator

@pytest.fixture
def venv_creator():
    return VenvCreator()

def test_init(venv_creator):
    assert hasattr(venv_creator, 'os_type')
    assert hasattr(venv_creator, 'is_windows')
    assert hasattr(venv_creator, 'is_linux')

def test_find_python_installations(venv_creator):
    installations = venv_creator.find_python_installations()
    assert isinstance(installations, list)
    assert len(installations) > 0

def test_get_python_version(venv_creator):
    python_path = "python"  # assumes python is in PATH
    version = venv_creator.get_python_version(python_path)
    assert isinstance(version, str)
    assert "Python" in version

def test_set_dependencies_folder(venv_creator, tmp_path):
    # Test with valid path
    assert venv_creator.set_dependencies_folder(str(tmp_path)) == True
    
    # Test with invalid path
    assert venv_creator.set_dependencies_folder("/nonexistent/path") == False