"""
Test script to verify Flask app initialization.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing Flask app initialization...")

try:
    print("1. Importing create_app from app...")
    from app import create_app
    
    print("2. Creating app instance...")
    app = create_app()
    
    print("3. Testing app configuration...")
    print(f"Debug mode: {app.debug}")
    print(f"Testing mode: {app.testing}")
    print(f"Secret key: {'Set' if app.secret_key else 'Not set'}")
    
    print("\n✅ App initialized successfully!")
    
except Exception as e:
    print(f"\n❌ Error initializing app: {e}")
    import traceback
    traceback.print_exc()
