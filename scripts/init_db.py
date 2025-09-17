"""
Database initialization script for UNICARE.

This script initializes the database with the required collections and default data.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establish a connection to the MongoDB database."""
    try:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        return client[os.getenv('MONGODB_NAME', 'unicare')]
    except ConnectionFailure:
        print("Error: Could not connect to MongoDB. Make sure it's running and the MONGODB_URI is correct.")
        sys.exit(1)

def create_collections(db):
    """Create necessary collections with validation rules."""
    # Users collection
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
        print("Created 'users' collection")
    
    # Create indexes for users collection
    db.users.create_index('email', unique=True)
    db.users.create_index('username', unique=True)
    
    # Game scores collection
    if 'game_scores' not in db.list_collection_names():
        db.create_collection('game_scores')
        print("Created 'game_scores' collection")
    
    # Personality tests collection
    if 'personality_tests' not in db.list_collection_names():
        db.create_collection('personality_tests')
        print("Created 'personality_tests' collection")
    
    # Add more collections as needed

def create_default_admin(db):
    """Create a default admin user if one doesn't exist."""
    admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'ChangeThisPassword123!')
    
    if not db.users.find_one({'email': admin_email}):
        admin_user = {
            'email': admin_email,
            'password': generate_password_hash(admin_password),
            'first_name': 'Admin',
            'last_name': 'User',
            'is_admin': True,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'last_login': None
        }
        db.users.insert_one(admin_user)
        print(f"Created default admin user with email: {admin_email}")
    else:
        print(f"Admin user with email {admin_email} already exists")

def main():
    """Main function to initialize the database."""
    print("Starting database initialization...")
    
    # Connect to the database
    db = get_db_connection()
    
    # Create collections
    create_collections(db)
    
    # Create default admin user
    create_default_admin(db)
    
    print("\nDatabase initialization completed successfully!")
    print("You can now start the application using 'python run.py'")

if __name__ == "__main__":
    main()
