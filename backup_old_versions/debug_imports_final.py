"""
Final debug script to identify import issues.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_import(module_name):
    """Test importing a module and print the result."""
    try:
        print(f"\nAttempting to import {module_name}...")
        __import__(module_name)
        print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing {module_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test importing core modules
print("Testing core imports...")
test_import("flask")
test_import("flask_sqlalchemy")
test_import("flask_login")

# Test importing app modules
print("\nTesting app imports...")
test_import("app")
test_import("app.extensions")
test_import("app.models")
test_import("app.forms")
test_import("app.routes")

# Test importing specific forms
print("\nTesting form imports...")
test_import("app.forms.auth_forms")
test_import("app.forms.admin_forms")

# Test importing models
print("\nTesting model imports...")
test_import("app.models.user")
test_import("app.models.client")
test_import("app.models.appointment")

# Test importing routes
print("\nTesting route imports...")
test_import("app.routes.main")
test_import("app.routes.auth")
test_import("app.routes.admin")

print("\nDebug complete!")
