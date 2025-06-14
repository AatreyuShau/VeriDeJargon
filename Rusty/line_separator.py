# line_separator.py
import re

def separate_lines(text: str):
    """Split text into lines/statements."""
    return [line.strip() for line in re.split(r'[\n\.]', text) if line.strip()]
