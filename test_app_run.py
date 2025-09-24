import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables for testing
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'true'

# Import the create_app function
from app import create_app

# Create the application
app = create_app()

# Add a test route
@app.route('/test')
def test_route():
    return "Test route works!"

if __name__ == '__main__':
    print("Starting the Flask application...")
    app.run(debug=True, port=5001)
