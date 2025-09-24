"""
Test script to check User model import and basic functionality.
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing User model...\n")

try:
    from app.models.user import User
    print("✅ Successfully imported User model")
    print(f"User model: {User}")
    
    # Test creating a User instance
    try:
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password_hash="testhash"
        )
        print("✅ Successfully created User instance")
        print(f"User: {user}")
    except Exception as e:
        print(f"❌ Error creating User instance: {e}")
        
except ImportError as e:
    print(f"❌ ImportError: {e}")
    
    # Try to print the full traceback
    import traceback
    traceback.print_exc()
    
    # Try to find the file
    user_model_path = os.path.join('app', 'models', 'user.py')
    if os.path.exists(user_model_path):
        print(f"\n✅ User model file exists at: {user_model_path}")
        try:
            with open(user_model_path, 'r') as f:
                first_few_lines = [next(f) for _ in range(10)]
            print("First few lines of user.py:")
            print(''.join(first_few_lines))
        except Exception as e:
            print(f"Error reading user.py: {e}")
    else:
        print(f"\n❌ User model file not found at: {user_model_path}")

print("\nTest complete.")
