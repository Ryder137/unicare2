import os
import bcrypt
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print('--- MIGRATING PLAINTEXT PASSWORDS TO BCRYPT ---')
users = supabase.table('users').select('id,username,password').execute().data

for user in users:
    pwd = user.get('password')
    # Heuristic: if password is not already a bcrypt hash (starts with $2b$ or $2a$), hash it
    if pwd and not (pwd.startswith('$2b$') or pwd.startswith('$2a$')):
        hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        supabase.table('users').update({'password': hashed}).eq('id', user['id']).execute()
        print(f"Updated user {user['username']} (id={user['id']}) to bcrypt hash.")
    else:
        print(f"User {user['username']} already has a hashed password.")

print('--- MIGRATION COMPLETE ---')
