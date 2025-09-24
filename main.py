"""
Main entry point for the UNICARE application.

This script initializes and runs the Flask application.
"""
import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("Starting UNICARE development server...")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)
