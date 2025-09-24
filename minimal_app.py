"""
Minimal Flask app to test imports.
"""
import os
import sys
from flask import Flask

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

app = Flask(__name__)

# Basic configuration
app.config.update(
    SECRET_KEY='dev-secret-key',
    SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MONGO_URI='mongodb://localhost:27017/test'
)

# Initialize extensions
from app.extensions import db, login_manager, init_extensions
init_extensions(app)

# Import and register blueprints
print("Importing blueprints...")
try:
    from app.routes import main as main_blueprint
    from app.routes.auth import auth as auth_blueprint
    from app.routes.admin import admin as admin_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    print("✅ Blueprints registered successfully!")
except Exception as e:
    print(f"❌ Error registering blueprints: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
    
    print("\nStarting Flask app...")
    app.run(debug=True, port=5001)
