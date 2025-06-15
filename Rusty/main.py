from content_formatter import ContentFormatter
from content_culler import ContentCuller
from line_separator import LineSeparator
from debate_analyzer import DebateAnalyzer
from init_summarizer import Summarizer
from textblob import Word
import sys
import traceback
from time import sleep
import json
import re

class Pipeline:
    def __init__(self):
        self.formatter = ContentFormatter()
        self.culler = ContentCuller()
        self.separator = LineSeparator()
        self.debater = DebateAnalyzer()
        self.summarizer = Summarizer()

    def sentence_separation(self, text, mode="lenient"):
        return self.separator.separate(text, mode=mode)

    def summarize_chunks(self, chunks, fast=True, max_length=40, min_length=10):
        return [self.summarizer.summarize(chunk, fast=fast, max_length=max_length, min_length=min_length) for chunk in chunks if chunk.strip()]

    def format_content(self, text):
        return self.formatter.format(text)

    def cull_content(self, text):
        return self.culler.cull(text)

    def assign_weights(self, lines):
        return self.debater.assign_weights(lines)

    def export_weighted_lines(self, weighted_lines, filename="output_weighted_lines.json"):
        export_data = [
            {"line": line, "confidence": confidence}
            for line, confidence in weighted_lines
        ]
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)

    def multi_layer_summarize(self, lines, layer1_max=40, layer1_min=10, layer2_max=25, layer2_min=8):
        joined = ' '.join(lines)
        layer1 = self.summarizer.summarize(joined, fast=True, max_length=layer1_max, min_length=layer1_min)
        layer2 = self.summarizer.summarize(layer1, fast=True, max_length=layer2_max, min_length=layer2_min)
        return layer2

    def run(self, input_text):
        print_progress("~ 1. Sentence Separation (lenient)")
        first_chunks = self.sentence_separation(input_text, mode="lenient")
        print_progress("~ 1. Summarization (on large chunks)")
        summarized_chunks = self.summarize_chunks(first_chunks)
        joined_summarized = ' '.join(summarized_chunks)
        print_progress("~ 2. Cutting/Culling & Summarizing (more aggressive)")
        formatted = self.format_content(joined_summarized)
        culled = self.cull_content(formatted)
        print_progress("~ 2. Sentence Separation (smaller bits)")
        small_bits = self.sentence_separation(culled, mode="strict")
        if not small_bits:
            print("\n ! Warning: No clear statements found to analyze", file=sys.stderr)
            return None
        print_progress(" ? Assigning weights (truth/confidence)")
        weighted_lines = self.assign_weights(small_bits)
        self.export_weighted_lines(weighted_lines)
        print("\n📊 Analysis Results:", file=sys.stderr)
        print("\n🎯 Most Credible Statements:", file=sys.stderr)
        # Merge all high and medium confidence lines for summary
        credible_lines = [line for line, confidence in weighted_lines if confidence >= 0.6]
        for line, confidence in weighted_lines:
            if confidence >= 0.8:
                print(f"\n### HIGH CONF ({{confidence:.2f}}):")
                print(f"   {{line}}")
            elif confidence >= 0.6:
                print(f"\n## MODERATE CONF ({{confidence:.2f}}):")
                print(f"   {{line}}")
            else:
                print(f"\n# LOW CONF ({{confidence:.2f}}):")
                print(f"   {{line}}")
        if credible_lines:
            # Merge all credible lines
            merged_credible = ' '.join(credible_lines)
            # Extractive: select the top 1-2 most representative sentences
            extractive_sents = self.select_representative_sentences(credible_lines, top_n=2)
            extractive_summary = ' '.join(extractive_sents)
            # Generative: pass merged credible lines through the summarizer
            abstractive_summary = self.summarizer.summarize(merged_credible, fast=True, max_length=25, min_length=8)
            # Combine both summaries
            combined_summary = extractive_summary + ' ' + abstractive_summary
            # Post-process to remove hallucinated phrases not in the original input
            combined_summary = self.remove_hallucinations(combined_summary, merged_credible)
            # Add de-jargonified context for technical terms
            try:
                from keyword_dejargonifier import KeywordDejargonifier
                dejargonifier = KeywordDejargonifier()
                explanations = dejargonifier.dejargonify(merged_credible)
                # Only add explanations that are contextually relevant (contain a keyword from the credible lines)
                filtered_explanations = {}
                for term, expl in explanations.items():
                    if term.lower() in merged_credible.lower() and term.lower() not in extractive_summary.lower():
                        filtered_explanations[term] = expl
                if filtered_explanations:
                    combined_summary += "\n\nTechnical Terms Explained:\n"
                    for term, expl in filtered_explanations.items():
                        # Only add if explanation is not generic or irrelevant
                        if term.lower() in merged_credible.lower() and len(expl.split()) > 5:
                            combined_summary += f"- {term}: {expl}\n"
            except Exception as e:
                combined_summary += f"\n[Dejargonifier error: {e}]"
            # Final pass: summarize everything (extractive + generative + explanations)
            final_summary = self.summarizer.summarize(combined_summary, fast=True, max_length=30, min_length=10)
            # Remove any lines that are not contextually present in the credible lines
            final_summary = self.remove_irrelevant_lines(final_summary, merged_credible)
            print("\n📝 Simplified Verified Summary:", file=sys.stderr)
            print(final_summary)
            # Export final summary to a .txt file
            with open("output_final_summary.txt", "w") as f:
                f.write(final_summary)
        return weighted_lines

    def select_representative_sentences(self, lines, top_n=2):
        """Select the most representative sentences (extractive)."""
        # Simple heuristic: pick the longest and most information-dense lines
        sorted_lines = sorted(lines, key=lambda l: len(l.split()), reverse=True)
        return sorted_lines[:top_n]

    def remove_hallucinations(self, summary, source_text):
        """Remove common hallucinated phrases if not present in the source text."""
        hallucinated_patterns = [
            r"i'?m not a big fan[,.]?", r"says [A-Za-z]+", r"according to", r"warns", r"claims", r"study", r"experts?", r"scientists?", r"doctors?", r"alleges?", r"confirms?", r"allegedly", r"reported", r"reportedly", r"research", r"findings", r"evidence", r"concludes?", r"conclusion", r"concluded that", r"concludes that", r"according to [A-Za-z ]+", r"according to the study", r"according to the research"
        ]
        for pat in hallucinated_patterns:
            matches = re.findall(pat, summary, flags=re.IGNORECASE)
            for m in matches:
                if m.lower() not in source_text.lower():
                    summary = re.sub(re.escape(m), '', summary, flags=re.IGNORECASE)
        # Clean up extra spaces and punctuation
        summary = re.sub(r'\s+', ' ', summary).strip()
        summary = re.sub(r'\s+([.,!?])', r'\1', summary)
        return summary

    def remove_irrelevant_lines(self, summary, credible_text):
        """Remove lines from summary that are not contextually present in the credible input."""
        summary_lines = summary.split('. ')
        filtered = []
        for line in summary_lines:
            # Only keep lines that share at least 2 words with the credible input
            words = set(line.lower().split())
            credible_words = set(credible_text.lower().split())
            if len(words & credible_words) >= 2:
                filtered.append(line)
        return '. '.join(filtered)

def print_progress(message):
    """Print progress message with animation"""
    print(f"\n{message}", end="", file=sys.stderr)
    for _ in range(3):
        sleep(0.3)
        print(".", end="", file=sys.stderr)
    print(file=sys.stderr)

def process_text(input_text):
    """Run the pipeline on input text and return weighted lines."""
    try:
        pipeline = Pipeline()
        return pipeline.run(input_text)
    except KeyboardInterrupt:
        print("\n\n Error: Process interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n Error occurred: {str(e)}", file=sys.stderr)
        print("\nDebug information:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point with input handling"""
    if sys.stdin.isatty():  # If running interactively
        print("\n Content (press Ctrl+D when finished):", file=sys.stderr)
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
        print("\n Error: No input", file=sys.stderr)
        sys.exit(1)
    process_text(text)

if __name__ == "__main__":
    main()
