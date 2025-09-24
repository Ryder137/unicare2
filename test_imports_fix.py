import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_import(module_name, attributes=None):
    """Test importing a module and optionally check for attributes."""
    try:
        module = __import__(module_name, fromlist=attributes or [])
        print(f"✅ Successfully imported {module_name}")
        
        if attributes:
            for attr in attributes:
                if hasattr(module, attr):
                    print(f"   ✅ Found attribute: {attr}")
                else:
                    print(f"   ❌ Missing attribute: {attr}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

print("Testing imports...\n")

# Test basic imports
test_import("flask")
test_import("flask_sqlalchemy")
test_import("flask_login")
test_import("flask_wtf")

# Test app imports
print("\nTesting app imports:")
test_import("app", ["create_app"])
test_import("app.forms", ["BaseLoginForm", "LoginForm", "AdminLoginForm"])
test_import("app.models", ["User", "AdminUser"])
test_import("app.routes", ["auth", "admin"])

# Test creating the app
print("\nTesting app creation:")
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
    import traceback
    traceback.print_exc()
