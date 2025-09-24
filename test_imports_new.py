"""
Test script to debug import issues.
"""
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("\nTrying to import Flask...")
try:
    from flask import Flask
    print("Successfully imported Flask")
except ImportError as e:
    print(f"Error importing Flask: {e}")
    print("Python path:", sys.path)
    print("\nTrying to install Flask...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    print("Please run this script again after installation.")
    sys.exit(1)

print("\nTrying to import from app...")
try:
    from app import create_app
    print("Successfully imported create_app from app")
    
    print("\nCreating app instance...")
    app = create_app()
    print("Successfully created app instance")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
