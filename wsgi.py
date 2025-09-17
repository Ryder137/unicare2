"""
WSGI config for UNICARE project.

This module contains the WSGI application used by the development server.
"""
import os
from unicate import create_app

app = create_app()

if __name__ == "__main__":
    # This block is only executed when running the development server
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
