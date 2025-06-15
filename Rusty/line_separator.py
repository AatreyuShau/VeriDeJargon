import re

def separate_lines(text: str):
    """Split text into lines/statements."""
    return [line.strip() for line in re.split(r'[\n\.]', text) if line.strip()]

class LineSeparator:
    def separate(self, text, mode="lenient"):
        """Separate text into sentences/chunks. Mode can be 'lenient' or 'strict'.
        'strict' splits on [.!?] followed by space or end; 'lenient' splits on [.!?] or newline.
        """
        if mode == "strict":
            # Split on period, exclamation, or question mark followed by space or end of string
            return [s.strip() for s in re.split(r'[.!?](?:\s|$)', text) if s.strip()]
        else:
            # Lenient: split on period, exclamation, question mark, or newline
            return [s.strip() for s in re.split(r'[.!?\n]', text) if s.strip()]
