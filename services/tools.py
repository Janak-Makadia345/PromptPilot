from datetime import datetime
import re

def parse_datetime(dt_str):
    """Parse a datetime string into a datetime object."""
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None

def extract_email_components(email_str):
    """Extract username and domain from an email address."""
    match = re.match(r"([^@]+)@([^@]+\.[^@]+)", email_str)
    if match:
        return {"username": match.group(1), "domain": match.group(2)}
    return None

def format_response(response):
    """Format a response for output."""
    return str(response)