import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return
        
    print(f"🔗 Database URL: {db_url}")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Successfully connected to the database")
            
            # Get database version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📊 Database version: {version}")
            
            # List tables
            print("\n📋 Listing tables in the database:")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            
            # Print tables
            print("\nFound tables:")
            for table in result:
                print(f"- {table[0]}")
                
    except Exception as e:
        print(f"\n❌ Error connecting to database: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if the database server is running")
        print("2. Verify your DATABASE_URL in the .env file")
        print("3. Check your internet connection")
        print("4. Make sure the database exists and is accessible")

if __name__ == "__main__":
    test_connection()
