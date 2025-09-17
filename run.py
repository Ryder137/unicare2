#!/usr/bin/env python
"""
Run the UNICARE development server.
"""
from unicate import create_app

app = create_app()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting UNICARE development server...")
    print("="*50 + "\n")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
