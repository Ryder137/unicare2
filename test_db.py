import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the create_app function
from app import create_app

# Create the Flask application
app = create_app()

# Test the database connection
with app.app_context():
    try:
        # Test SQLAlchemy connection
        from app.extensions import db
        db.engine.connect()
        print("Successfully connected to the database!")
        
        # Test MongoDB connection
        from app.extensions import mongo
        mongo.cx.server_info()
        print("Successfully connected to MongoDB!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
