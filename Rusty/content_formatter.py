class ContentFormatter:
    def format(self, text: str) -> str:
        """Format the input content (basic whitespace normalization)."""
        import re
        return re.sub(r'\s+', ' ', text.strip())
