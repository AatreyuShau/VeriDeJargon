from transformers import pipeline
import re

fast_summarizer = pipeline("summarization", model="t5-small")

def compress_sentences(text, fast=True, max_length=20, min_length=5):
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    key_sents = []

    for sent in sentences:
        sent_lower = sent.lower()
        if any(word in sent_lower for word in [
            "says", "claims", "study", "suggests", "warns", "proves", "shows", "disproves", "alleges", "confirms", "allegedly", "reported", "reportedly", "research", "researchers", "scientists", "states", "experts", "'", "findings", "evidence", "evidently", "concludes", "conclusion", "concluded", "concludes that", "concluded that", '"', "according to", "according to experts", "according to researchers", "according to scientists", "according to the study", "according to the research"
        ]):
            key_sents.append(sent.strip())

    if not key_sents:
        return fast_summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
    return " ".join(key_sents)

class Summarizer:
    def summarize(self, text, fast=True, max_length=40, min_length=10):
        """Summarize the input text using the T5 model, or fallback to truncation if model fails."""
        try:
            if fast:
                return fast_summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
        except Exception:
            pass
        # Fallback: truncate to max_length words
        words = text.split()
        if len(words) > max_length:
            return ' '.join(words[:max_length]) + '...'
        return text

if __name__ == "__main__":
    example_text = """
    Lemons improve eyesight, says a new viral post.
    However, doctors warn there's no evidence and such claims may be misleading.
    """
    summary = compress_sentences(example_text, fast=True)
    print("⚡ Summary:\n", summary)
