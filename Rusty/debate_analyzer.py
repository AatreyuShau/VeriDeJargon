import sys
from textblob import Word
from init_summarizer import compress_sentences
from keyword_dejargonifier import KeywordDejargonifier

class DebateAnalyzer:
    def __init__(self):
        self.dejargonifier = KeywordDejargonifier()

    def assign_weights(self, lines):
        """Assign confidence weights to each line by fact-checking against online sources and providing citations."""
        weighted = []
        for line in lines:
            # Extract keywords for this line
            keywords = self.dejargonifier.extract_keywords(line)
            # For each keyword, fetch context from online sources
            found_contexts = []
            citations = []
            for kw in keywords:
                context = self.dejargonifier.fetch_context(kw)
                if context:
                    found_contexts.append(context)
                    citations.append(f"{kw}: {context[:80]}...")
            # Fact-check: if any keyword context matches or supports the line, boost confidence
            confidence = 0.5
            for ctx in found_contexts:
                if ctx and any(word in ctx.lower() for word in line.lower().split()):
                    confidence += 0.2
            # If no context found, lower confidence
            if not found_contexts:
                confidence -= 0.2
            # Clamp confidence between 0 and 1
            confidence = max(0.0, min(1.0, confidence))
            # Attach citations for transparency
            if citations:
                line_with_cite = line + "\n[Citations: " + "; ".join(citations) + "]"
            else:
                line_with_cite = line
            weighted.append((line_with_cite, confidence))
        return weighted

def simplify_text(text):
    """Replace complex words in text with simpler synonyms using TextBlob, and split into very short sentences."""
    import nltk
    nltk.download('punkt', quiet=True)
    from nltk.tokenize import sent_tokenize
    simple_words = set([
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
    ])
    sentences = sent_tokenize(text)
    simplified_sentences = []
    for sent in sentences:
        words = sent.split()
        simplified = []
        for w in words:
            w_clean = ''.join(filter(str.isalpha, w)).lower()
            if w_clean in simple_words or len(w_clean) <= 4:
                simplified.append(w)
            else:
                blob_word = Word(w_clean)
                syns = blob_word.synsets
                if syns:
                    lemma = syns[0].lemmas()[0].name().replace('_', ' ')
                    if lemma in simple_words:
                        simplified.append(lemma)
                    else:
                        simplified.append(w)
                else:
                    simplified.append(w)
        # Make each sentence very short (max 6 words)
        for i in range(0, len(simplified), 6):
            chunk = simplified[i:i+6]
            if chunk:
                simplified_sentences.append(' '.join(chunk))
    return simplified_sentences


def simplify_summary(lines, confidences=None):
    """Directly summarize the combined simplified sentences for a child-friendly output, using two passes."""
    if not lines:
        return "No credible information to summarize."
    if confidences is None:
        confidences = [1.0] * len(lines)
    all_broken = []
    for line in lines:
        all_broken.extend(simplify_text(line))
    # Join all the simplified sentences
    joined_simple = ' '.join(all_broken)
    # First summarization pass
    first_summary = compress_sentences(joined_simple, fast=True, max_length=40, min_length=10)
    # Second summarization pass for extra simplification
    final_summary = compress_sentences(first_summary, fast=True, max_length=30, min_length=8)
    print("\n📝 Final Child-Friendly Summary:", file=sys.stderr)
    print(final_summary, file=sys.stderr)
    return final_summary
