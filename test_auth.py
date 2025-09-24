"""
Test script to isolate the auth import issue.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing imports...\n")

# Test importing auth forms
try:
    from app.forms.auth_forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
    print("✅ Successfully imported auth forms")
except ImportError as e:
    print(f"❌ Error importing auth forms: {e}")

# Test importing User model
try:
    from app.models.user import User
    print("✅ Successfully imported User model")
    print(f"User model has is_authenticated: {hasattr(User, 'is_authenticated')}")
    print(f"User model has is_active: {hasattr(User, 'is_active')}")
    print(f"User model has is_anonymous: {hasattr(User, 'is_anonymous')}")
    print(f"User model has get_id: {hasattr(User, 'get_id')}")
except ImportError as e:
    print(f"❌ Error importing User model: {e}")

# Test importing auth blueprint
try:
    from app.routes.auth import bp as auth_blueprint
    print("✅ Successfully imported auth blueprint")
except ImportError as e:
    print(f"❌ Error importing auth blueprint: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
