"""
Test script to isolate the auth import issue.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_import():
    print("1. Importing auth module...")
    try:
        from app.routes import auth
        print("✅ Successfully imported auth module")
        return True
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_import()
