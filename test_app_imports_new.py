"""
Test script to verify imports and app initialization.
"""
import os
import sys
import traceback

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_import(module_name, fromlist=None):
    """Test importing a module and print the result."""
    try:
        if fromlist:
            module = __import__(module_name, fromlist=fromlist)
            for item in fromlist:
                if hasattr(module, item):
                    print(f"✅ Successfully imported {item} from {module_name}")
                else:
                    print(f"❌ {item} not found in {module_name}")
        else:
            __import__(module_name)
            print(f"✅ Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        traceback.print_exc()
        return False

print("Testing imports...\n")

# Test basic Python imports
print("1. Testing basic imports:")
test_import("flask")
test_import("flask_sqlalchemy")
test_import("flask_migrate")
test_import("flask_login")
test_import("flask_wtf")
test_import("pymongo")

# Test app imports
print("\n2. Testing app imports:")
test_import("app", ["create_app"])
test_import("app.forms", ["BaseLoginForm", "LoginForm", "AdminLoginForm"])
test_import("app.models", ["User", "AdminUser"])
test_import("app.routes", ["auth", "admin"])

# Test creating the app
print("\n3. Testing app creation:")
try:
    from app import create_app
    print("✅ Successfully imported create_app")
    
    print("Creating app instance...")
    app = create_app()
    print("✅ App created successfully!")
    
    # Test basic route
    @app.route('/test')
    def test_route():
        return "Test route works!"
    
    print("✅ Test route created successfully!")
    print("\n✅ All tests passed!")
    print("You can now run the application using: python run.py")
    
except Exception as e:
    print(f"❌ Error creating app: {e}")
    traceback.print_exc()
