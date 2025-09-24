from app import create_app, db
from app.models.user import User
from models import *  # Import all models from the root models directory

def setup_database():
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating database tables...")
            # Create all database tables
            db.create_all()
            print("Database tables created successfully!")
            
            # Create a default admin user if it doesn't exist
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                admin = User(
                    email='admin@example.com',
                    password='admin123',  # In a real app, hash the password
                    is_admin=True,
                    first_name='Admin',
                    last_name='User'
                )
                db.session.add(admin)
                db.session.commit()
                print("Created default admin user")
                
            return True
            
        except Exception as e:
            print(f"Error setting up database: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if setup_database():
        print("Database setup completed successfully!")
    else:
        print("Database setup failed. Please check the error messages above.")
