import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing imports...")

try:
    from app.forms import BaseLoginForm, LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm, CreateAdminForm, AdminLoginForm, AdminRegisterForm
    print("All forms imported successfully!")
    
    # Print the classes to verify they're imported correctly
    print("\nImported classes:")
    for cls in [BaseLoginForm, LoginForm, RegisterForm, ForgotPasswordForm, 
                ResetPasswordForm, CreateAdminForm, AdminLoginForm, AdminRegisterForm]:
        print(f"- {cls.__name__}")
        
except ImportError as e:
    print(f"Error importing forms: {e}")
    print("\nPython path:", sys.path)
    print("Current working directory:", os.getcwd())
    print("\nContents of app/forms directory:")
    forms_dir = os.path.join(project_root, 'app', 'forms')
    if os.path.exists(forms_dir):
        print(os.listdir(forms_dir))
    else:
        print(f"Directory not found: {forms_dir}")
