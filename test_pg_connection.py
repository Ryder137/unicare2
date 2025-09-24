import os
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔗 Database URL: {db_url}")
    
    try:
        # Parse the database URL
        result = urlparse(db_url)
        dbname = result.path[1:]  # remove leading '/'
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432  # default PostgreSQL port
        
        # Connect to the database
        print(f"\n🔌 Connecting to PostgreSQL database at {host}:{port}...")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # Get database version
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            print(f"✅ Successfully connected to PostgreSQL {db_version[0]}")
            
            # List all tables in public schema
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            
            if tables:
                print("\n📋 Tables in 'public' schema:")
                for table in tables:
                    table_name = table[0]
                    print(f"\nTable: {table_name}")
                    print("Columns:")
                    
                    # Get column information
                    cur.execute(sql.SQL("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = %s
                        ORDER BY ordinal_position;
                    """), [table_name])
                    
                    for col in cur.fetchall():
                        print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {col[3]}' if col[3] else ''}")
            else:
                print("\n❌ No tables found in the 'public' schema")
                print("This could mean:")
                print("1. The database is empty")
                print("2. The user doesn't have permission to access the tables")
                print("3. The tables are in a different schema")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if the database server is running")
        print("2. Verify DATABASE_URL in your .env file is correct")
        print("3. Check if the database name, username, and password are correct")
        print("4. Ensure the database user has proper permissions")
        print("5. Check if your IP is whitelisted if using a cloud database")
        print("6. Try connecting with a PostgreSQL client like pgAdmin or psql to verify credentials")
        print("\nTo install psycopg2 if missing, run:")
        print("pip install psycopg2-binary")
        return False

if __name__ == "__main__":
    # Check if psycopg2 is installed
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 is not installed. Please install it by running:")
        print("pip install psycopg2-binary")
        sys.exit(1)
    
    test_connection()
