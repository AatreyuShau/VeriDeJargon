class ContentCuller:
    def cull(self, text: str) -> str:
        """Remove bracketed info like [extra info not my concern rn] and summarize if needed."""
        import re
        return re.sub(r'\[.*?not my concern.*?\]', '', text, flags=re.IGNORECASE)
