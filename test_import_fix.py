import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now try importing the forms
print("Trying to import forms...")
try:
    from app.forms import BaseLoginForm
    print("Successfully imported BaseLoginForm!")
except ImportError as e:
    print(f"Error importing BaseLoginForm: {e}")
    print("Current Python path:", sys.path)
