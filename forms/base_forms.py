"""Base forms used across the application."""
from datetime import datetime, date
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, 
    SubmitField, HiddenField, SelectField, DateField, TextAreaField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp, Optional, InputRequired

class AdminRegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(max=100, message='Name must be less than 100 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter your full name',
        'autofocus': True
    })
    
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'your.email@example.com',
        'autocomplete': 'email'
    })

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Create a password',
        'autocomplete': 'new-password'
    })

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Confirm your password',
        'autocomplete': 'new-password'
    })

    submit = SubmitField('Register', render_kw={
        'class': 'btn btn-primary btn-lg w-100 mt-3'
    })

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your email',
        'autocomplete': 'email',
        'autofocus': True
    })

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password'
    })

    remember_me = BooleanField('Remember Me', default=False, render_kw={
        'class': 'form-check-input'
    })

    submit = SubmitField('Sign In', render_kw={
        'class': 'btn btn-primary btn-lg w-100'
    })

class CreateAdminForm(FlaskForm):
    """Form for creating a new admin user."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter email address',
        'autocomplete': 'email'
    })
    
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must be less than 50 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter first name'
    })
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must be less than 50 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter last name'
    })
    
    is_super_admin = BooleanField('Super Admin', 
        false_values=(False, 'false', 0, '0'),
        render_kw={
            'class': 'form-check-input',
            'data-toggle': 'tooltip',
            'title': 'Super admins have full system access and can manage other admins'
        }
    )
    
    submit = SubmitField('Create Admin', render_kw={
        'class': 'btn btn-primary'
    })
    
    def validate_email(self, field):
        """Validate that the email is not already in use."""
        from models import Admin
        admin = Admin.query.filter_by(email=field.data).first()
        if admin is not None:
            raise ValidationError('This email is already registered. Please use a different email.')


class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your email',
        'autocomplete': 'email',
        'autofocus': True
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password'
    })
    
    remember_me = BooleanField('Remember Me', default=False, render_kw={
        'class': 'form-check-input'
    })
    
    submit = SubmitField('Sign In', render_kw={
        'class': 'btn btn-primary btn-lg w-100'
    })


class RegisterForm(FlaskForm):
    """Form for user registration."""
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(max=50, message='First name must be less than 50 characters')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your first name',
        'autofocus': True
    })
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(max=50, message='Last name must be less than 50 characters')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your last name'
    })
    
    gender = SelectField('Gender', choices=[
        ('', 'Select gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[
        DataRequired(message='Please select your gender')
    ], render_kw={
        'class': 'form-select form-select-lg'
    })
    
    birthdate = DateField('Birthdate', validators=[
        DataRequired(message='Birthdate is required')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'type': 'date',
        'max': datetime.now().strftime('%Y-%m-%d')
    })
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters long'),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Username must have only letters, numbers, dots or underscores')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Choose a username',
        'autocomplete': 'username'
    })
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'your.email@example.com',
        'autocomplete': 'email'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$',
               message='Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one number')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Create a strong password',
        'autocomplete': 'new-password',
        'data-bs-toggle': 'tooltip',
        'title': 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character'
    })
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Retype your password',
        'autocomplete': 'new-password'
    })
    
    submit = SubmitField('Create Account', render_kw={
        'class': 'btn btn-primary btn-lg w-100 mt-3'
    })
    
    def validate_birthdate(self, field):
        """Validate that the user is at least 13 years old."""
        today = date.today()
        age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
        if age < 13:
            raise ValidationError('You must be at least 13 years old to register.')


class ForgotPasswordForm(FlaskForm):
    """Form for requesting a password reset."""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your email address',
        'autofocus': True
    })
    
    submit = SubmitField('Reset Password', render_kw={
        'class': 'btn btn-primary btn-lg w-100 mt-3'
    })


class ResetPasswordForm(FlaskForm):
    """Form for resetting a password."""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long'),
        EqualTo('confirm_password', message='Passwords must match')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter a new password',
        'autocomplete': 'new-password',
        'autofocus': True
    })
    
    confirm_password = PasswordField('Confirm New Password', render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Confirm your new password',
        'autocomplete': 'new-password'
    })
    
    token = HiddenField()
    
    submit = SubmitField('Reset Password', render_kw={
        'class': 'btn btn-primary btn-lg w-100 mt-3'
    })
