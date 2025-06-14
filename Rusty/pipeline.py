import re
from typing import List, Tuple

def content_formatting(text: str) -> str:
    # Basic formatting: strip, normalize whitespace
    return re.sub(r'\s+', ' ', text.strip())

def cut_cull_summarize(text: str) -> str:
    # Remove bracketed info like [extra info not my concern rn]
    return re.sub(r'\[.*?not my concern.*?\]', '', text, flags=re.IGNORECASE)

def separate_lines(text: str) -> List[str]:
    # Split into sentences or lines
    return [line.strip() for line in re.split(r'[\n\.]', text) if line.strip()]

def assign_weights(lines: List[str]) -> List[Tuple[str, float]]:
    # Dummy weight assignment: longer lines get higher confidence
    weighted = []
    for line in lines:
        # Example: weight = min(1.0, len(line)/100)
        weight = min(1.0, max(0.1, len(line) / 100))
        weighted.append((line, round(weight, 2)))
    return weighted

def pipeline(text: str) -> List[Tuple[str, float]]:
    formatted = content_formatting(text)
    summarized = cut_cull_summarize(formatted)
    lines = separate_lines(summarized)
    weighted_lines = assign_weights(lines)
    return weighted_lines

if __name__ == "__main__":
    sample_input = """
    INPUT: This is a test input. [extra info not my concern rn] Here is another line. This should be processed.
    """
    output = pipeline(sample_input)
    for line, weight in output:
        print(f"{line} (confidence: {weight})")
