"""
Test script to verify imports in app/__init__.py
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing imports in app/__init__.py...")

try:
    # Test importing Flask
    print("1. Importing Flask...")
    from flask import Flask
    
    # Test importing extensions
    print("2. Importing extensions...")
    from app.extensions import db, mail, mongo, csrf, login_manager, limiter, socketio, init_extensions
    
    # Test importing create_app
    print("3. Importing create_app...")
    from app import create_app
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Error during imports: {e}")
    import traceback
    traceback.print_exc()
