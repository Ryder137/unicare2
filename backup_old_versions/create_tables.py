from app import create_app, db
from models import *

app = create_app()

with app.app_context():
    try:
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
