"""
Test script to verify imports in app/__init__.py
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

print("Testing imports in app/__init__.py...\n")

# Test basic imports
print("1. Testing basic imports:")
test_import("flask")
test_import("os")
test_import("logging")
test_import("dotenv")

# Test importing extensions
print("\n2. Testing extensions import:")
try:
    from app.extensions import db, mail, mongo, csrf, login_manager, limiter, socketio, init_extensions
    print("✅ Successfully imported all extensions")
except ImportError as e:
    print(f"❌ Failed to import extensions: {e}")
    traceback.print_exc()

# Test creating the app
print("\n3. Testing app creation:")
try:
    from app import create_app
    print("✅ Successfully imported create_app")
    
    print("Creating app instance...")
    app = create_app()
    print("✅ App created successfully!")
    
    # Test basic configuration
    print("\nApp configuration:")
    print(f"Debug mode: {app.debug}")
    print(f"Testing mode: {app.testing}")
    print(f"Secret key: {'Set' if app.secret_key else 'Not set'}")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error creating app: {e}")
    traceback.print_exc()
