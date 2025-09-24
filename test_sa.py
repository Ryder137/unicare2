"""
Test SQLAlchemy with Flask
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    print("Creating database and tables...")
    db.create_all()
    print("Database created successfully!")
    
    print("\nAdding test user...")
    test_user = User(username='test', email='test@example.com')
    db.session.add(test_user)
    db.session.commit()
    print("Test user added successfully!")
    
    print("\nQuerying users...")
    users = User.query.all()
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"- {user.username} ({user.email})")

print("\n✅ Test completed successfully!")
