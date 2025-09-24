import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/unicare')
print(f"Database URL: {db_url}")

# Test database connection
try:
    from sqlalchemy import create_engine
    
    print("\nTesting database connection...")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute("SELECT version()")
        version = result.scalar()
        print(f"✅ Successfully connected to database!")
        print(f"Database version: {version}")
        
        # List tables
        print("\nListing tables in the database:")
        result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = [row[0] for row in result.fetchall()]
        if tables:
            print("\nFound tables:")
            for table in tables:
                print(f"- {table}")
        else:
            print("No tables found in the database.")
            
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    print("\nTroubleshooting steps:")
    print("1. Check if the database server is running")
    print("2. Verify the DATABASE_URL in your .env file")
    print("3. Make sure your database user has the correct permissions")
    print("4. Check if the database 'unicare' exists")
