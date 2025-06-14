# main.py
from content_formatter import format_content
from content_culler import cut_cull_summarize
from line_separator import separate_lines
from debate_analyzer import assign_weights
from init_summarizer import compress_sentences
import sys
import traceback
from time import sleep

def print_progress(message):
    """Print progress message with animation"""
    print(f"\n{message}", end="", file=sys.stderr)
    for _ in range(3):
        sleep(0.3)
        print(".", end="", file=sys.stderr)
    print(file=sys.stderr)

def process_text(input_text):
    """Main processing pipeline."""
    try:
        print_progress("📝 Formatting content")
        formatted = format_content(input_text)
        print_progress("✂️ Cutting/Culling & Summarizing")
        summarized = cut_cull_summarize(formatted)
        print_progress("🔗 Separating the lines")
        lines = separate_lines(summarized)
        if not lines:
            print("\n⚠️ Warning: No clear statements found to analyze", file=sys.stderr)
            return None
        print_progress("🤔 Assigning weights (truth/confidence)")
        weighted_lines = assign_weights(lines)
        print("\n📊 Analysis Results:", file=sys.stderr)
        print("\n🎯 Most Credible Statements:", file=sys.stderr)
        credible_lines = [line for line, confidence in weighted_lines if confidence >= 0.6]
        for line, confidence in weighted_lines:
            if confidence >= 0.8:
                print(f"\n✅ HIGH CONFIDENCE ({confidence:.2f}):")
                print(f"   {line}")
            elif confidence >= 0.6:
                print(f"\n📎 MODERATE CONFIDENCE ({confidence:.2f}):")
                print(f"   {line}")
            else:
                print(f"\n❓ LOW CONFIDENCE ({confidence:.2f}):")
                print(f"   {line}")
        # Summarize using only credible (moderate/high confidence) lines
        if credible_lines:
            summary = simplify_summary(credible_lines)
            print("\n📝 Simplified Verified Summary:", file=sys.stderr)
            print(summary)
        return weighted_lines
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error occurred: {str(e)}", file=sys.stderr)
        print("\nDebug information:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point with input handling"""
    if sys.stdin.isatty():  # If running interactively
        print("\n🎤 Please enter your text (press Ctrl+D when finished):", file=sys.stderr)
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            text = "\n".join(lines)
    else:  # If input is piped
        text = sys.stdin.read()
    
    if not text.strip():
        print("\n❌ Error: No input text provided", file=sys.stderr)
        sys.exit(1)
    
    process_text(text)

def simplify_summary(lines):
    """Summarize and simplify a list of credible lines using a faster model-based summarizer only."""
    if not lines:
        return "No credible information to summarize."
    text = ' '.join(lines)
    summary = compress_sentences(text, fast=True)
    return summary

if __name__ == "__main__":
    main()
