from datetime import datetime

def time_ago(timestamp):
    """Convert a timestamp to a human-readable 'time ago' string."""
    if not timestamp:
        return ""
        
    now = datetime.utcnow()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    
    if days > 7:
        return timestamp.strftime('%b %d, %Y')
    elif days > 1:
        return f'{int(days)} days ago'
    elif days == 1:
        return 'yesterday'
    elif hours >= 1:
        return f'{int(hours)} hour{"s" if hours > 1 else ""} ago'
    elif minutes >= 1:
        return f'{int(minutes)} minute{"s" if minutes > 1 else ""} ago'
    else:
        return 'just now'
