""
Check if the project has the required directory structure and files.
"""
import os
import sys
from pathlib import Path

# Required directories
REQUIRED_DIRS = [
    'app',
    'app/static',
    'app/templates',
    'app/models',
    'app/forms',
    'app/routes',
    'app/utils',
    'services',
    'scripts',
    'migrations',
    'static',
    'templates',
    'uploads',
    'logs'
]

# Required files
REQUIRED_FILES = [
    'app/__init__.py',
    'app/models/__init__.py',
    'app/forms/__init__.py',
    'app/routes/__init__.py',
    'app/utils/__init__.py',
    'requirements.txt',
    '.env.example',
    '.gitignore',
    'README.md'
]

def check_project_structure():
    """Check if the project has the required structure."""
    project_root = Path(__file__).parent
    missing_dirs = []
    missing_files = []
    
    # Check directories
    for dir_path in REQUIRED_DIRS:
        full_path = project_root / dir_path
        if not full_path.exists() or not full_path.is_dir():
            missing_dirs.append(dir_path)
    
    # Check files
    for file_path in REQUIRED_FILES:
        full_path = project_root / file_path
        if not full_path.exists() or not full_path.is_file():
            missing_files.append(file_path)
    
    # Print results
    if not missing_dirs and not missing_files:
        print("✅ Project structure is complete!")
        return True
    
    if missing_dirs:
        print("\n❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
    
    if missing_files:
        print("\n❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
    
    print("\nPlease create the missing directories and files before proceeding.")
    return False

if __name__ == "__main__":
    check_project_structure()
