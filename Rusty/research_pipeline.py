import requests
from bs4 import BeautifulSoup
from Rusty.init_summarizer import Summarizer

def fetch_wikipedia_section(topic, section=None):
    urls = [
        f'https://simple.wikipedia.org/wiki/{topic.replace(" ", "_")}',
        f'https://en.wikipedia.org/wiki/{topic.replace(" ", "_")}'
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                if section:
                    header = soup.find(['span', 'h2', 'h3'], string=lambda s: s and section.lower() in s.lower())
                    if header:
                        p = header.find_next('p')
                        if p and len(p.text) > 40:
                            return p.text.strip()
                # fallback: first paragraph
                p = soup.find('p')
                if p and len(p.text) > 40:
                    return p.text.strip()
        except Exception:
            pass
    return None

def process_research_topic(topic):
    summarizer = Summarizer()
    # Definition
    definition = fetch_wikipedia_section(topic, section='definition')
    if not definition:
        definition = fetch_wikipedia_section(topic)
    if definition:
        definition = summarizer.summarize(definition, fast=True, max_length=40, min_length=10)
    # Overview
    overview = fetch_wikipedia_section(topic, section='overview')
    if not overview:
        overview = fetch_wikipedia_section(topic)
    if overview:
        overview = summarizer.summarize(overview, fast=True, max_length=60, min_length=15)
    # History
    history = fetch_wikipedia_section(topic, section='history')
    if history:
        history = summarizer.summarize(history, fast=True, max_length=60, min_length=15)
    # Derivation (optional)
    derivation = fetch_wikipedia_section(topic, section='derivation')
    if derivation:
        derivation = summarizer.summarize(derivation, fast=True, max_length=60, min_length=15)
    # Deep dive (try to get a longer section)
    deepdive = fetch_wikipedia_section(topic)
    if deepdive:
        deepdive = summarizer.summarize(deepdive, fast=True, max_length=120, min_length=30)
    return {
        'definition': definition or '',
        'overview': overview or '',
        'history': history or '',
        'derivation': derivation or '',
        'deepdive': deepdive or ''
    }
