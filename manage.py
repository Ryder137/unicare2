from flask_migrate import Migrate
from app import create_app, db
from models import *
import click
from flask.cli import with_appcontext

app = create_app()
migrate = Migrate(app, db)

# Custom CLI commands
@app.cli.command("create-db")
@with_appcontext
def create_db():
    """Create database tables."""
    db.create_all()
    print("Database tables created successfully!")

@app.cli.command("drop-db")
@with_appcontext
def drop_db():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all database tables?', abort=True):
        db.drop_all()
        print("Database tables dropped successfully!")

if __name__ == '__main__':
    app.run(debug=True)
