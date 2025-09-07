from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class CreateGuidanceCounselorForm(FlaskForm):
    """Form for creating a new guidance counselor."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    full_name = StringField('Full Name', validators=[DataRequired()])
    license_number = StringField('License Number', validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=1000)])
    years_of_experience = IntegerField(
        'Years of Experience',
        validators=[Optional(), NumberRange(min=0, max=50)]
    )
    education = TextAreaField('Education', validators=[Optional()])
    languages_spoken = StringField('Languages Spoken (comma-separated)', validators=[Optional()])
    is_available = BooleanField('Is Available', default=True)
