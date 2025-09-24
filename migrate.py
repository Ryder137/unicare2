from flask_migrate import Migrate, upgrade, migrate, init, stamp
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

def deploy():
    """Run deployment tasks."""
    # Create database tables
    db.create_all()
    
    # Create or update the database
    init()
    stamp()
    migrate(message='Initial migration')
    upgrade()

if __name__ == '__main__':
    with app.app_context():
        deploy()
