"""
Environment test script.
"""
import sys
import os

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ {module_name} error: {e}")
        return False

print("Testing Python environment...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

print("\nTesting core imports...")
test_import("flask")
test_import("flask_sqlalchemy")
test_import("flask_login")

print("\nTest complete!")
