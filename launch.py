"""
Launch script for UNICARE application.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_DEBUG'] = '1'

# Import the app after setting up the environment
from app import app, create_app

if __name__ == "__main__":
    # Create the app instance
    app = create_app()
    
    print("\n" + "="*50)
    print("Starting UNICARE development server...")
    print("="*50 + "\n")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
