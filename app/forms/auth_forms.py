"""
Authentication-related forms for the application.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from services.accounts_reposervice import account_repo_service

class BaseLoginForm(FlaskForm):
    """Base form for login functionality."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    role = StringField('Role', validators=[DataRequired()])

class LoginForm(BaseLoginForm):
    """Form for user login."""
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # Set the role to 'user' by default for this login form
        self.role.data = 'client'

class RegisterForm(FlaskForm):
    """Form for user registration."""
    first_name = StringField('First Name', validators=[DataRequired("First Name is required"), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired("Last Name is required"), Length(max=50)])
    email = StringField('Email', validators=[DataRequired("Email is required"), Email()])
    password = PasswordField('Password', validators=[
        DataRequired("Password is required"),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired("Confirm Password is required"),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
      """Check if email is already registered."""
      existing_user = account_repo_service.get_account_by_email(email.data)
      return existing_user.count is not None

class ForgotPasswordForm(FlaskForm):
    """Form for requesting a password reset."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Form for resetting a password."""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
