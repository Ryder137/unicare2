#!/usr/bin/env python
"""
Run the UNICARE development server.
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting UNICARE development server...")
    print("="*50 + "\n")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
