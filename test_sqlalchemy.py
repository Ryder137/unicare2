"""
Test script to check SQLAlchemy compatibility with Python 3.13.4
"""
import sys
import os

print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Try to import SQLAlchemy
try:
    print("\n1. Testing SQLAlchemy import...")
    import sqlalchemy
    print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
    
    # Test basic SQLAlchemy functionality
    print("\n2. Testing SQLAlchemy core functionality...")
    from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
    from sqlalchemy.orm import declarative_base, sessionmaker
    
    # Create an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    print("✅ Created SQLAlchemy engine")
    
    # Create a simple table
    Base = declarative_base()
    
    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        email = Column(String)
    
    # Create tables
    Base.metadata.create_all(engine)
    print("✅ Created test table")
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test CRUD operations
    new_user = User(name='Test User', email='test@example.com')
    session.add(new_user)
    session.commit()
    print("✅ Added test user")
    
    # Query the user
    user = session.query(User).first()
    print(f"✅ Retrieved user: {user.name} ({user.email})")
    
    print("\n✅ All SQLAlchemy tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
