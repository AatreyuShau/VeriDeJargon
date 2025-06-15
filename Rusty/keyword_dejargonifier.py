import re
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

COMMON_SITES = [
    'https://simple.wikipedia.org/wiki/',
    'https://en.wikipedia.org/wiki/',
    'https://www.researchgate.net/search/publication?q=',
    'https://ground.news/search?q=',
    'https://www.nature.com/',
    'https://www.science.org/journal/science',
]

class KeywordDejargonifier:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def is_jargon(self, word):
        # Heuristic: not a stopword, not a common English word, not punctuation, not a number
        return word.isalpha() and word.lower() not in self.stop_words and len(word) > 3

    def extract_keywords(self, text):
        words = word_tokenize(text)
        words = [w for w in words if self.is_jargon(w)]
        freq = Counter(words)
        # Return most common nontrivial words
        return [w for w, _ in freq.most_common(10)]

    def fetch_context(self, keyword):
        # Try Wikipedia first
        url = COMMON_SITES[0] + keyword.replace(' ', '_')
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                p = soup.find('p')
                if p and len(p.text) > 40:
                    return p.text.strip()
        except Exception:
            pass
        # Try other sources
        for base in COMMON_SITES[1:]:
            try:
                resp = requests.get(base + keyword, timeout=5)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Try to find a summary/description
                    p = soup.find('p')
                    if p and len(p.text) > 40:
                        return p.text.strip()
            except Exception:
                continue
        return None

    def dejargonify(self, text):
        keywords = self.extract_keywords(text)
        explanations = {}
        contexts = {}
        for kw in keywords:
            context = self.fetch_context(kw)
            if context:
                explanations[kw] = context
                contexts[kw] = context
        return explanations

    def get_contexts(self, text):
        """Return a dict of keyword:context for all keywords in text."""
        keywords = self.extract_keywords(text)
        contexts = {}
        for kw in keywords:
            context = self.fetch_context(kw)
            if context:
                contexts[kw] = context
        return contexts
