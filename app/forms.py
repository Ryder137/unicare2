"""
Forms for the application.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, DecimalField, DateField, DateTimeField, TimeField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from ..models.user import User

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    """Form for user registration."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.get_by_email(email.data)
        if user is not None:
            raise ValidationError('Please use a different email address.')

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

class CreateAdminForm(FlaskForm):
    """Form for creating a new admin user."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Create Admin')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        from ..extensions import mongo
        user = mongo.db.users.find_one({'email': email.data.lower()})
        if user is not None:
            raise ValidationError('Email already registered')

class ProfileForm(FlaskForm):
    """Form for updating user profile."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_email, *args, **kwargs):
        """Initialize form with original email for validation."""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Check if email is already in use by another user."""
        if email.data != self.original_email:
            from ..extensions import mongo
            user = mongo.db.users.find_one({'email': email.data.lower()})
            if user is not None:
                raise ValidationError('Email already in use by another account')
    
    def validate_current_password(self, field):
        """Validate current password if changing password."""
        if self.new_password.data and not field.data:
            raise ValidationError('Current password is required to change password')

class ContactForm(FlaskForm):
    """Form for contact page."""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Send Message')

class AssessmentForm(FlaskForm):
    """Base form for assessments."""
    submit = SubmitField('Submit Assessment')

class MoodEntryForm(FlaskForm):
    """Form for mood tracking entries."""
    mood = SelectField('Mood', choices=[
        ('1', '😭 Very Sad'),
        ('2', '😔 Sad'),
        ('3', '😐 Neutral'),
        ('4', '🙂 Happy'),
        ('5', '😄 Very Happy')
    ], validators=[DataRequired()])
    energy_level = SelectField('Energy Level', choices=[
        ('1', '😴 Very Low'),
        ('2', '😕 Low'),
        ('3', '😐 Normal'),
        ('4', '😊 High'),
        ('5', '🚀 Very High')
    ], validators=[DataRequired()])
    stress_level = SelectField('Stress Level', choices=[
        ('1', '😌 Very Low'),
        ('2', '🙂 Low'),
        ('3', '😐 Normal'),
        ('4', '😟 High'),
        ('5', '😫 Very High')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    submit = SubmitField('Save Entry')

class GratitudeJournalForm(FlaskForm):
    """Form for gratitude journal entries."""
    entry = TextAreaField('What are you grateful for today?', validators=[
        DataRequired(),
        Length(min=10, max=2000, message='Entry must be between 10 and 2000 characters')
    ])
    mood = SelectField('Current Mood', choices=[
        ('1', '😭 Very Sad'),
        ('2', '😔 Sad'),
        ('3', '😐 Neutral'),
        ('4', '🙂 Happy'),
        ('5', '😄 Very Happy')
    ], validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    submit = SubmitField('Save Entry')

class MultiCheckboxField(SelectMultipleField):
    """Multiple checkbox field for forms."""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class PersonalityTestForm(FlaskForm):
    """Form for personality test."""
    # Example questions for the Big Five personality test
    # Openness
    o1 = SelectField('I am someone who is full of energy, always active.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    o2 = SelectField('I have a rich vocabulary.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    # Conscientiousness
    c1 = SelectField('I am always prepared.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    c2 = SelectField('I pay attention to details.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    # Extraversion
    e1 = SelectField('I am the life of the party.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    e2 = SelectField('I don\'t talk a lot.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    # Agreeableness
    a1 = SelectField('I am interested in people.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    a2 = SelectField('I sympathize with others\' feelings.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    # Neuroticism
    n1 = SelectField('I get stressed out easily.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    n2 = SelectField('I worry about things.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Submit Test')

class EQTestForm(FlaskForm):
    """Form for emotional intelligence test."""
    # Example questions for emotional intelligence test
    q1 = SelectField('I can recognize my emotions as I experience them.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    q2 = SelectField('I find it hard to understand the non-verbal messages of other people.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    q3 = SelectField('I can easily recognize my emotions.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    q4 = SelectField('I have a good sense of why I have certain feelings most of the time.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    q5 = SelectField('I have a good understanding of my own emotions.', choices=[
        ('1', 'Strongly Disagree'),
        ('2', 'Disagree'),
        ('3', 'Neutral'),
        ('4', 'Agree'),
        ('5', 'Strongly Agree')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Submit Test')
