from app import create_app, db
from app.models import *

app = create_app()

def initialize_database():
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            return True
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            return False

if __name__ == "__main__":
    initialize_database()
