"""
Test Flask installation and basic functionality.
"""
import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Python path:", sys.path)

# Try to import Flask
try:
    import flask
    print("\n✅ Flask is installed. Version:", flask.__version__)
    
    # Try creating a basic Flask app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello, World!"
    
    print("✅ Basic Flask app created successfully!")
    print("To run the app, use: app.run(debug=True)")
    
except ImportError as e:
    print("\n❌ Error importing Flask:", e)
    print("\nTry installing Flask with: pip install flask")
except Exception as e:
    print("\n❌ Error:", e)
    import traceback
    traceback.print_exc()
