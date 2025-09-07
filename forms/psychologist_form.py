from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class PsychologistForm(FlaskForm):
    """Form for adding/editing psychologist information."""
    license_number = StringField('License Number', validators=[
        DataRequired(),
        Length(max=50, message='License number cannot exceed 50 characters')
    ])
    
    specialization = StringField('Specialization', validators=[
        DataRequired(),
        Length(max=100, message='Specialization cannot exceed 100 characters')
    ])
    
    bio = TextAreaField('Professional Bio', validators=[
        Optional(),
        Length(max=2000, message='Bio cannot exceed 2000 characters')
    ])
    
    years_of_experience = IntegerField('Years of Experience', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Years of experience must be between 0 and 100')
    ])
    
    education = TextAreaField('Education', validators=[
        Optional(),
        Length(max=500, message='Education information cannot exceed 500 characters')
    ])
    
    languages_spoken = StringField('Languages Spoken (comma-separated)', validators=[
        Optional(),
        Length(max=200, message='Languages list cannot exceed 200 characters')
    ])
    
    consultation_fee = DecimalField('Consultation Fee', validators=[
        Optional(),
        NumberRange(min=0, message='Fee cannot be negative')
    ], places=2)
    
    is_available = BooleanField('Currently Accepting New Patients', default=True)

    def process_languages(self):
        """Process the languages_spoken field into a list."""
        if self.languages_spoken.data:
            return [lang.strip() for lang in self.languages_spoken.data.split(',') if lang.strip()]
        return []

class PsychologistFilterForm(FlaskForm):
    """Form for filtering psychologists."""
    specialization = StringField('Specialization', validators=[Optional()])
    min_experience = IntegerField('Minimum Years of Experience', validators=[
        Optional(),
        NumberRange(min=0, max=100)
    ])
    max_fee = DecimalField('Maximum Fee', places=2, validators=[
        Optional(),
        NumberRange(min=0)
    ])
    language = StringField('Language', validators=[Optional()])
