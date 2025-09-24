"""
Test script to check app imports.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_import(module_name):
    """Test importing a module and print the result."""
    try:
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

print("Testing imports...\n")

# Test importing core modules
test_import("flask")
test_import("flask_sqlalchemy")
test_import("flask_login")
test_import("flask_mail")
test_import("flask_pymongo")
test_import("flask_limiter")
test_import("flask_wtf")
test_import("flask_socketio")

# Test importing app modules
test_import("app")
test_import("app.extensions")
test_import("app.models")
test_import("app.forms")
test_import("app.routes")

print("\nTest complete!")
