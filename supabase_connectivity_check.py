from utils import db
from services.database_service import db_service

print("\n=== Supabase Connectivity Check ===\n")

# Test utils/db.py
print("[utils/db.py] Testing fetch_all on 'users' table:")
users = db.fetch_all('users')
print(f"Fetched {len(users)} users (if 0, table may be empty or not exist)")

print("[utils/db.py] Testing insert_data on 'users' table:")
try:
    test_user = {'id': 'test_check', 'created_at': '2025-01-01T00:00:00Z'}
    db.insert_data('users', test_user)
    print("Insert attempted (if no error above, insert function is connected)")
except Exception as e:
    print(f"Insert failed: {e}")

# Test services/database_service.py
print("\n[services/database_service.py] Testing get_user:")
user = db_service.get_user('test_check')
print(f"get_user returned: {user}")

print("[services/database_service.py] Testing get_user_scores:")
scores = db_service.get_user_scores('test_check')
print(f"Fetched {len(scores)} scores (if 0, table may be empty or not exist)")

print("[services/database_service.py] Testing get_user_personality_tests:")
tests = db_service.get_user_personality_tests('test_check')
print(f"Fetched {len(tests)} personality test results (if 0, table may be empty or not exist)")

print("\n=== Connectivity Check Complete ===\n")
print("Check above for any error messages. If all sections ran without errors, all files are connected to Supabase.")
