# debate_analyzer.py

def assign_weights(lines):
    """Assign a dummy confidence/truth weight to each line."""
    weighted = []
    for line in lines:
        weight = min(1.0, max(0.1, len(line) / 100))
        weighted.append((line, round(weight, 2)))
    return weighted
