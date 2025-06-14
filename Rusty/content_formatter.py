# content_formatter.py
import re

def format_content(text: str) -> str:
    """Format the input content (basic whitespace normalization)."""
    return re.sub(r'\s+', ' ', text.strip())
