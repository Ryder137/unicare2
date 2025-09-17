from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional

class BaseLoginForm(FlaskForm):
    """Base login form with common fields"""
    email = StringField('Email', validators=[
        DataRequired('Email is required'),
        Email('Please enter a valid email address')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'your.email@example.com',
        'autofocus': True
    })
    
    password = PasswordField('Password', validators=[
        DataRequired('Password is required')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    })
    
    remember_me = BooleanField('Remember Me', default=False, render_kw={
        'class': 'form-check-input'
    })
    
    submit = SubmitField('Sign In', render_kw={
        'class': 'btn btn-primary w-100'
    })

class PsychologistLoginForm(BaseLoginForm):
    """Login form for psychologists"""
    pass  # Can add psychologist-specific fields if needed

class GuidanceCounselorLoginForm(BaseLoginForm):
    """Login form for guidance counselors"""
    pass  # Can add counselor-specific fields if needed

class ClientLoginForm(BaseLoginForm):
    """Login form for clients"""
    pass  # Can add client-specific fields if needed

class RoleSelectionForm(FlaskForm):
    """Form for selecting user role before login"""
    role = SelectField('Login As', choices=[
        ('', 'Select your role'),
        ('admin', 'Administrator'),
        ('psychologist', 'Psychologist'),
        ('counselor', 'Guidance Counselor'),
        ('client', 'Client')
    ], validators=[DataRequired()], render_kw={
        'class': 'form-select',
        'id': 'roleSelect'
    })
    
    continue_btn = SubmitField('Continue', render_kw={
        'class': 'btn btn-primary w-100 mt-3'
    })
