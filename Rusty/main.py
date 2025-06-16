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
import concurrent.futures

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
            return []  # Return empty list instead of None
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
            # Add context from online resources for the whole summary
            try:
                from keyword_dejargonifier import KeywordDejargonifier
                dejargonifier = KeywordDejargonifier()
                # Get all keyword contexts for the merged credible lines
                keyword_contexts = dejargonifier.get_contexts(merged_credible)
                if keyword_contexts:
                    online_context = '\n'.join([f"{k}: {v}" for k, v in keyword_contexts.items() if len(v.split()) > 5])
                    combined_summary = extractive_summary + ' ' + abstractive_summary + "\n\nOnline Context:\n" + online_context
                else:
                    combined_summary = extractive_summary + ' ' + abstractive_summary
            except Exception as e:
                combined_summary = extractive_summary + ' ' + abstractive_summary + f"\n[Online context error: {e}]"
            # Post-process to remove hallucinated phrases not in the original input
            combined_summary = self.remove_hallucinations(combined_summary, merged_credible)
            # Add de-jargonified context for technical terms (filtered, as before)
            try:
                explanations = dejargonifier.dejargonify(merged_credible)
                filtered_explanations = {}
                for term, expl in explanations.items():
                    if term.lower() in merged_credible.lower() and term.lower() not in extractive_summary.lower():
                        filtered_explanations[term] = expl
                if filtered_explanations:
                    combined_summary += "\n\nTechnical Terms Explained:\n"
                    for term, expl in filtered_explanations.items():
                        if term.lower() in merged_credible.lower() and len(expl.split()) > 5:
                            combined_summary += f"- {term}: {expl}\n"
            except Exception as e:
                combined_summary += f"\n[Dejargonifier error: {e}]"
            # Final pass: summarize everything (extractive + generative + online context + explanations)
            final_summary = self.summarizer.summarize(combined_summary, fast=True, max_length=30, min_length=10)
            final_summary = self.remove_irrelevant_lines(final_summary, merged_credible)
            print("\n📝 Simplified Verified Summary:", file=sys.stderr)
            print(final_summary)
            with open("output_final_summary.txt", "w") as f:
                f.write(final_summary)
        return weighted_lines

    def select_representative_sentences(self, lines, top_n=2):
        """Select the most representative sentences (extractive)."""
        # pick the longest and most information-dense lines
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
        return '.'.join(filtered)

def print_progress(message):
    """Print progress message with animation"""
    print(f"\n{message}", end="", file=sys.stderr)
    for _ in range(3):
        sleep(0.3)
        print(".", end="", file=sys.stderr)
    print(file=sys.stderr)

def process_text(input_text, return_definitions=False):
    """Run the pipeline on input text and return summary and definitions if requested."""
    import concurrent.futures
    try:
        pipeline = Pipeline()
        # Fast path: skip weighting if text is long, just summarize and extract keywords
        if not isinstance(input_text, str):
            input_text = str(input_text)
        if len(input_text.split()) > 400:
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                summary_future = executor.submit(pipeline.summarizer.summarize, input_text, True, 60, 15)
                definitions = {}
                try:
                    from Rusty.keyword_dejargonifier import KeywordDejargonifier
                    dejargonifier = KeywordDejargonifier()
                    keywords = dejargonifier.extract_keywords(input_text)
                    if not isinstance(keywords, list):
                        keywords = list(keywords)
                    keywords = [k for k in keywords if isinstance(k, str) and len(k) > 4][:5]
                    def_futures = {k: executor.submit(dejargonifier.fetch_context, k) for k in keywords}
                    for k, fut in def_futures.items():
                        try:
                            defn = fut.result(timeout=6)
                            if isinstance(defn, str) and isinstance(k, str) and k.lower() in defn.lower() and 'film' not in defn.lower() and 'movie' not in defn.lower():
                                definitions[k] = defn
                        except Exception:
                            continue
                except Exception:
                    definitions = {}
                summary = summary_future.result(timeout=10)
            if return_definitions:
                return summary, definitions
            else:
                return summary
        # Normal path for short/medium text
        lines = input_text.split('\n')
        if len(lines) > 50:
            lines = lines[:50]
            input_text = '\n'.join(lines)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            weighted_future = executor.submit(pipeline.run, input_text)
            definitions = {}
            try:
                from Rusty.keyword_dejargonifier import KeywordDejargonifier
                dejargonifier = KeywordDejargonifier()
                keywords = dejargonifier.extract_keywords(input_text)
                if not isinstance(keywords, list):
                    keywords = list(keywords)
                keywords = [k for k in keywords if isinstance(k, str) and len(k) > 4][:5]
                def_futures = {k: executor.submit(dejargonifier.fetch_context, k) for k in keywords}
                for k, fut in def_futures.items():
                    try:
                        defn = fut.result(timeout=6)
                        if isinstance(defn, str) and isinstance(k, str) and k.lower() in defn.lower() and 'film' not in defn.lower() and 'movie' not in defn.lower():
                            definitions[k] = defn
                    except Exception:
                        continue
            except Exception:
                definitions = {}
            try:
                weighted_lines = weighted_future.result(timeout=60)
            except concurrent.futures.TimeoutError:
                print("\n ! Warning: assign_weights timed out", file=sys.stderr)
                weighted_lines = []
        # Defensive: if weighted_lines is not a list of (line, confidence) tuples, fix it
        if not weighted_lines or not (isinstance(weighted_lines, list) and all(isinstance(x, (list, tuple)) and len(x) == 2 for x in weighted_lines)):
            weighted_lines = []
        try:
            with open("output_final_summary.txt", "r") as f:
                summary = f.read().strip()
        except Exception:
            summary = ""
        if return_definitions:
            return summary, definitions
        else:
            return summary
    except KeyboardInterrupt:
        print("\n\n Error: Process interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n Error occurred: {str(e)}", file=sys.stderr)
        print("\nDebug information:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return {'output': f'Error: {str(e)}'}

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
