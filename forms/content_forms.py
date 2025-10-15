"""Content management forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, 
    BooleanField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Length, Optional

class ContentForm(FlaskForm):
    """Form for creating and editing content."""
    
    author = StringField('Author', validators=[
        DataRequired(message='Author is required'),
        Length(max=100, message='Author name must be less than 100 characters')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter author name'
    })
    
    messages = TextAreaField('Content Message', validators=[
        DataRequired(message='Content message is required'),
        Length(min=10, message='Content must be at least 10 characters long')
    ], render_kw={
        'class': 'form-control',
        'placeholder': 'Enter the content message...',
        'rows': 5
    })
    
    content_type = SelectField('Content Type', choices=[
        ('general', 'General'),
        ('mental_health', 'Mental Health'),
        ('educational', 'Educational'),
        ('motivational', 'Motivational'),
        ('awareness', 'Awareness'),
        ('announcement', 'Announcement')
    ], validators=[Optional()], render_kw={
        'class': 'form-select'
    })
    
    is_active = BooleanField('Active', default=True, render_kw={
        'class': 'form-check-input'
    })
    
    submit = SubmitField('Save Content', render_kw={
        'class': 'btn btn-primary'
    })

class ContentSearchForm(FlaskForm):
    """Form for searching and filtering content."""
    
    search_query = StringField('Search', validators=[Optional()], render_kw={
        'class': 'form-control',
        'placeholder': 'Search content...'
    })
    
    status_filter = SelectField('Status', choices=[
        ('', 'All Status'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], validators=[Optional()], render_kw={
        'class': 'form-select'
    })
    
    submit = SubmitField('Search', render_kw={
        'class': 'btn btn-outline-primary'
    })