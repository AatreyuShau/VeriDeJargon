# VeriDeJargon
truth from jargon. no misinfo and clickbait; simplified lingo

VeriDeJargon is a research-driven NLP pipeline that detects misinformation, flags clickbait, and simplifies complex or jargon-heavy language into accurate, readable summaries. It is designed to help readers cut through noise, especially in science and news articles, by separating fact from hype.

## Overview

VeriDeJargon takes raw text — such as a news article or a headline — and processes it through a multi-stage pipeline:

- Fact Verification
- Clickbait Detection
- Jargon Simplification
- Weighted Summarization

This project aims to build trust in an age of disinformation, with tools that combine natural language processing, deep learning, and factual reasoning.

## Features

- Verifies individual lines in text as likely true, false, or unverifiable using a trained verifier
- Detects and flags clickbait based on linguistic patterns and exaggeration signals
- Breaks down complex or technical language into layman-friendly summaries
- Weighs the importance of lines based on their factuality before summarization
- Outputs a final summary that prioritizes truth, context, and readability

## Technologies Used

- PyTorch
- Hugging Face Transformers (RoBERTa, T5, etc.)
- SpaCy
- scikit-learn
- Python standard libraries (json, re, etc.)

## System Architecture

1. **Text Segmentation**
   - Input is split into lines or semantic units
2. **Clickbait Classifier**
   - Uses transformer embeddings + logistic regression or fine-tuned classifier
3. **Truth Assignment Engine**
   - Each segment is passed to a misinformation detector trained on real/fake corpora
4. **Line Rating**
   - Lines are weighted based on verifiability and contextual confidence
5. **Simplified Summary Generator**
   - A seq2seq model rewrites trustworthy content in plain English

## Setup Instructions

Clone the repository:

```bash
git clone https://github.com/AatreyuShau/VeriDeJargon.git
cd VeriDeJargon
