"""
Test script to identify import errors.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_import(module_name, import_name=None):
    """Test importing a module and print success or error."""
    try:
        if import_name:
            __import__(module_name, fromlist=[import_name])
            print(f"✅ Successfully imported {import_name} from {module_name}")
        else:
            __import__(module_name)
            print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Error importing {import_name or module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing {import_name or module_name}: {e}")
        return False

print("Testing imports...\n")

# Test importing app
print("Testing app imports:")
test_import("app")
test_import("app.extensions")
test_import("app.models")
test_import("app.models.user", "User")
test_import("app.forms", "LoginForm")
test_import("app.forms", "RegisterForm")
test_import("app.forms", "ForgotPasswordForm")
test_import("app.forms", "ResetPasswordForm")
test_import("app.forms", "CreateAdminForm")

# Test importing routes
print("\nTesting route imports:")
test_import("app.routes.auth")
test_import("app.routes.admin")
test_import("app.routes.main")
test_import("app.routes.games")
test_import("app.routes.assessments")

print("\nTesting complete!")
