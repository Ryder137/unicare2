"""
Clean environment test script.
"""
import sys
import os

def print_section(title):
    """Print a section header."""
    print("\n" + "="*50)
    print(f"{title}".center(50))
    print("="*50)

def test_import(module_name):
    """Test importing a module and print the result."""
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "unknown version")
        print(f"✅ {module_name} {version} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing {module_name}: {e}")
        return False

def main():
    """Main function to run the tests."""
    print_section("System Information")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")

    print_section("Testing Core Imports")
    test_import("flask")
    test_import("flask_sqlalchemy")
    test_import("flask_login")
    test_import("sqlalchemy")

    print_section("Test Complete")

if __name__ == "__main__":
    main()
