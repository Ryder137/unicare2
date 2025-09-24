"""
Forms package for the application.
"""
from .auth_forms import (
    BaseLoginForm,
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm
)

from .admin_forms import CreateAdminForm, AdminLoginForm, AdminRegisterForm

__all__ = [
    'BaseLoginForm',
    'LoginForm',
    'RegisterForm',
    'ForgotPasswordForm',
    'ResetPasswordForm',
    'CreateAdminForm',
    'AdminLoginForm',
    'AdminRegisterForm'
]
