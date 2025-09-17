"""
Custom template filters for the application.
"""
from datetime import datetime
import re
from bson import ObjectId

def time_ago(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if dt is None:
        return default
    
    now = datetime.utcnow()
    diff = now - dt if now > dt else dt - now
    
    periods = (
        (diff.days // 365, "year", "years"),
        (diff.days // 30, "month", "months"),
        (diff.days // 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds // 3600, "hour", "hours"),
        (diff.seconds // 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )
    
    for period, singular, plural in periods:
        if period > 0:
            return f"{period} {singular if period == 1 else plural} ago"
    
    return default

def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object as a string."""
    if dt is None:
        return ''
    return dt.strftime(format)

def format_date(dt, format='%Y-%m-%d'):
    """Format a date as a string."""
    if dt is None:
        return ''
    return dt.strftime(format)

def format_time(dt, format='%H:%M:%S'):
    """Format a time as a string."""
    if dt is None:
        return ''
    return dt.strftime(format)

def format_currency(amount, currency='$'):
    """Format a number as currency."""
    if amount is None:
        return ''
    return f"{currency}{amount:,.2f}"

def format_phone_number(phone):
    """Format a phone number as (XXX) XXX-XXXX."""
    if not phone:
        return ''
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', str(phone))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return phone

def object_id(value):
    """Convert a string to a MongoDB ObjectId."""
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except:
        return None

def to_json(value):
    """Convert a value to a JSON string."""
    import json
    return json.dumps(value)

def from_json(value):
    """Convert a JSON string to a Python object."""
    import json
    try:
        return json.loads(value)
    except:
        return {}

def truncate(text, length=100, suffix='...'):
    """Truncate text to a specified length."""
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length].rsplit(' ', 1)[0] + suffix

def pluralize(count, singular='', plural='s'):
    """Return the singular or plural form based on the count."""
    if count == 1:
        return singular
    return plural

def markdown_to_html(text):
    """Convert Markdown to HTML."""
    import markdown
    from markdown.extensions.toc import TocExtension
    
    if not text:
        return ''
    
    return markdown.markdown(
        text,
        extensions=[
            'extra',
            'codehilite',
            'tables',
            'toc',
            'sane_lists',
            'nl2br',
            'smarty',
            'wikilinks',
            TocExtension(toc_depth=3, permalink=True)
        ],
        output_format='html5'
    )

def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ''
    return value.replace('\n', '<br>')
