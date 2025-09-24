"""
Test script to identify import errors with simplified imports.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_import(module_name, attr=None):
    """Test importing a module and print success or error."""
    try:
        if attr:
            module = __import__(module_name, fromlist=[attr])
            if hasattr(module, attr):
                print(f"✅ Successfully imported {attr} from {module_name}")
                return True
            else:
                print(f"❌ {attr} not found in {module_name}")
                return False
        else:
            __import__(module_name)
            print(f"✅ Successfully imported {module_name}")
            return True
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

print("Testing imports...\n")

# Test basic imports
print("1. Testing basic imports:")
test_import("flask")
test_import("flask_login")
test_import("flask_sqlalchemy")
test_import("flask_mail")
test_import("flask_pymongo")

# Test app imports
print("\n2. Testing app imports:")
test_import("app")
test_import("app.extensions")
test_import("app.models")
test_import("app.models.user", "User")
test_import("app.forms.auth_forms", "LoginForm")
test_import("app.forms.auth_forms", "RegisterForm")

# Test routes
print("\n3. Testing route imports:")
try:
    from app.routes import main
    print("✅ Successfully imported app.routes.main")
except Exception as e:
    print(f"❌ Error importing app.routes.main: {e}")

try:
    from app.routes import auth
    print("✅ Successfully imported app.routes.auth")
except Exception as e:
    print(f"❌ Error importing app.routes.auth: {e}")

# Test database
print("\n4. Testing database:")
try:
    from app.extensions import db
    print("✅ Successfully imported db from app.extensions")
    
    # Create a test app context
    from app import create_app
    app = create_app()
    with app.app_context():
        print("✅ Successfully created app context")
        try:
            db.create_all()
            print("✅ Successfully created database tables")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTest complete!")
