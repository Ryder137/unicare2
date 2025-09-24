import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    print("Attempting to import BaseLoginForm...")
    from app.forms.auth_forms import BaseLoginForm
    print("✅ Successfully imported BaseLoginForm!")
    print(f"BaseLoginForm: {BaseLoginForm}")
except ImportError as e:
    print(f"❌ Failed to import BaseLoginForm: {e}")
    import traceback
    traceback.print_exc()
