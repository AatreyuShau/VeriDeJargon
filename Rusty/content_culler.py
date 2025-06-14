# content_culler.py
import re

def cut_cull_summarize(text: str) -> str:
    """Remove bracketed info like [extra info not my concern rn] and summarize if needed."""
    # Remove all [ ... not my concern ... ]
    return re.sub(r'\[.*?not my concern.*?\]', '', text, flags=re.IGNORECASE)
