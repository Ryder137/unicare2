import sys
import os
import pdb

def debug_exception():
    """Debug an exception by dropping into a pdb shell."""
    import traceback
    import pdb
    import sys
    traceback.print_exc()
    pdb.post_mortem(sys.exc_info()[2])

if __name__ == "__main__":
    try:
        # Add the current directory to the Python path
        sys.path.insert(0, os.path.abspath('.'))
        
        # Create and run the app
        from app import create_app
        app = create_app()
        print("App created successfully!")
        
        # Try to import forms
        from app.forms import *
        print("Successfully imported forms!")
        
        # Try to run the app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error: {e}")
        debug_exception()
