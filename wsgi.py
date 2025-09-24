"""
WSGI config for UNICARE project.

This module contains the WSGI application used by the development server.
"""
import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
