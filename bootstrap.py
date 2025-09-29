"""
Bootstrap script to set up the Python path and run the UNICARE application.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the app
from app import app

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting UNICARE development server...")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
