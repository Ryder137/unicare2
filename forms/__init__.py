"""Forms package for the application."""

# Import base forms
from .base_forms import (
    AdminRegisterForm,
    AdminLoginForm,
    CreateAdminForm,
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm
)

# Import other forms
from .guidance_counselor_form import CreateGuidanceCounselorForm
from .psychologist_form import PsychologistForm, PsychologistFilterForm

__all__ = [
    'AdminRegisterForm',
    'AdminLoginForm',
    'CreateAdminForm',
    'LoginForm',
    'RegisterForm',
    'ForgotPasswordForm',
    'ResetPasswordForm',
    'CreateGuidanceCounselorForm',
    'PsychologistForm',
    'PsychologistFilterForm'
]
