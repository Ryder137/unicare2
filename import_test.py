import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Python path:", sys.path)
print("\nTrying to import SQLAlchemy...")
try:
    from sqlalchemy import create_engine
    print("Successfully imported SQLAlchemy!")
except ImportError as e:
    print(f"Error importing SQLAlchemy: {e}")

print("\nTrying to import forms...")
try:
    from app.forms import BaseLoginForm
    print("Successfully imported BaseLoginForm!")
except ImportError as e:
    print(f"Error importing BaseLoginForm: {e}")
    print("Current working directory:", os.getcwd())
    print("Project root:", project_root)
    print("Contents of app directory:", os.listdir(os.path.join(project_root, 'app')))
    print("Contents of app/forms directory:", os.listdir(os.path.join(project_root, 'app', 'forms')))
