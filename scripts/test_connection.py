import os
import requests
from dotenv import load_dotenv
from pathlib import Path

def test_connection():
    try:
        # Load environment variables
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url:
            print("❌ SUPABASE_URL not found in .env file")
            return False
            
        # Add /rest/v1/ to the URL for the REST API endpoint
        rest_url = f"{supabase_url}/rest/v1/"
        
        print(f"🌐 Testing connection to: {rest_url}")
        
        try:
            # Try to make a GET request to the REST endpoint
            response = requests.get(rest_url)
            print(f"✅ Successfully connected to Supabase REST API")
            print(f"   Status Code: {response.status_code}")
            
            # If we get a 401, that's actually good - it means we reached the server
            if response.status_code == 401:
                print("ℹ️ Got 401 Unauthorized - this is expected for unauthenticated requests")
                return True
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to Supabase: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Check your internet connection")
            print("2. Verify the SUPABASE_URL in your .env file")
            print("3. Make sure your Supabase project is running and accessible")
            print("4. Check if there are any firewall restrictions")
            return False
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
