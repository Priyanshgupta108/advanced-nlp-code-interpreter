"""
detector.py — Programming Language Detector
NLP BASED CODE INTERPRETER
Uses: Tokenization, Pattern Matching, N-gram Analysis, Statistical Scoring
"""

import re
from collections import Counter
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

# ─────────────────────────────────────────────
# NLP CONCEPT: Keyword-based Pattern Dictionary
# Each language has a set of regex patterns (tokens)
# ─────────────────────────────────────────────
LANGUAGE_PATTERNS = {
    'Python': [
        r'\bdef\b', r'\bimport\b', r'\bprint\s*\(', r'\bself\b',
        r'\belif\b', r'\bTrue\b', r'\bFalse\b', r'\bNone\b',
        r':\s*$', r'\bclass\b', r'\blambda\b', r'\byield\b'
    ],
    'Java': [
        r'\bpublic\b', r'\bprivate\b', r'\bSystem\.out\.println\b',
        r'\bvoid\b', r'\bclass\b', r'\bstatic\b', r'\bnew\b',
        r'\bimport\s+java', r'\bthrows\b', r'\bextends\b'
    ],
    'C++': [
        r'#include', r'\bcout\b', r'\bcin\b', r'\bnamespace\b',
        r'std::', r'\btemplate\b', r'\bvector\b', r'::\s*',
        r'\bdelete\b', r'\bnew\b', r'endl'
    ],
    'C': [
        r'#include\s*<stdio', r'\bprintf\b', r'\bscanf\b',
        r'\bint\s+main\b', r'\bmalloc\b', r'\bfree\b',
        r'\bstruct\b', r'\btypedef\b', r'->|&[a-zA-Z]'
    ],
    'JavaScript': [
        r'\bconst\b', r'\blet\b', r'\bconsole\.log\b',
        r'\bfunction\b', r'=>', r'\bdocument\b', r'\bwindow\b',
        r'\basync\b', r'\bawait\b', r'\bPromise\b'
    ],
    'TypeScript': [
        r':\s*string\b', r':\s*number\b', r':\s*boolean\b',
        r'\binterface\b', r'\benum\b', r'<[A-Z][a-z]+>',
        r'\bReadonly\b', r'\bPartial\b'
    ],
    'SQL': [
        r'\bSELECT\b', r'\bFROM\b', r'\bWHERE\b',
        r'\bINSERT\b', r'\bCREATE\b', r'\bDROP\b',
        r'\bJOIN\b', r'\bGROUP BY\b', r'\bHAVING\b'
    ],
    'HTML': [
        r'<html', r'<div', r'<head', r'<body',
        r'<!DOCTYPE', r'<script', r'<style', r'<p\b', r'<a\s'
    ],
    'CSS': [
        r'\{[^}]*:', r'font-size', r'background-color',
        r'margin:', r'padding:', r'display\s*:', r'@media'
    ],
    'Ruby': [
        r'\bdef\b', r'\bend\b', r'\bputs\b', r'\brequire\b',
        r'\bdo\b\s*\|', r'\battr_accessor\b', r'\.each\b'
    ],
    'Go': [
        r'\bpackage\b', r'\bfunc\b', r'\bfmt\.', r':=',
        r'\bgoroutine\b', r'\bchan\b', r'\bdefer\b', r'\bgo\b\s'
    ],
    'Kotlin': [
        r'\bfun\b', r'\bval\b', r'\bvar\b', r'\bprintln\b',
        r'\bdata class\b', r'\bobject\b', r'\bwhen\b', r'\?[.:]'
    ],
    'Swift': [
        r'\bvar\b', r'\blet\b', r'\bfunc\b', r'\bguard\b',
        r'\boptional\b', r'\bprotocol\b', r'\bextension\b'
    ],
    'R': [
        r'<-', r'\blibrary\b', r'\bc\(', r'\bdata\.frame\b',
        r'\bggplot\b', r'\bsapply\b', r'\blapply\b'
    ],
    'PHP': [
        r'<\?php', r'\becho\b', r'\$[a-zA-Z_]',
        r'\bfunction\b', r'->', r'\barray\b', r'\bforeach\b'
    ],
}

# ─────────────────────────────────────────────
# NLP CONCEPT: Tokenization
# Breaks raw code into meaningful tokens/words
# ─────────────────────────────────────────────
def tokenize_code(code: str) -> list:
    """Tokenize code into individual tokens (NLP: Tokenization)"""
    tokens = re.findall(r'[a-zA-Z_]\w*|[{}()\[\];,.]|"[^"]*"|\'[^\']*\'|\d+', code)
    return tokens


# ─────────────────────────────────────────────
# NLP CONCEPT: N-gram Analysis
# Generates bigrams from code tokens
# ─────────────────────────────────────────────
def get_ngrams(tokens: list, n: int = 2) -> list:
    """Generate N-grams from token list"""
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


# ─────────────────────────────────────────────
# NLP CONCEPT: Statistical Pattern Matching
# Scores each language based on keyword frequency
# ─────────────────────────────────────────────
def detect_language(code: str) -> tuple:
    """
    Main language detection function.
    Combines pattern matching + Pygments for accuracy.
    Returns: (detected_language, confidence_dict)
    """
    scores = {}

    # Step 1: Pattern-based scoring with weighted priorities
    for lang, patterns in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE | re.MULTILINE)
            score += len(matches)
        if score > 0:
            scores[lang] = score

    # Step 1.5: Python-specific boost (critical fix)
    # If code has 'def' with ':' and no semicolons, heavily favor Python
    if re.search(r'\bdef\s+\w+\s*\([^)]*\)\s*:', code):
        scores['Python'] = scores.get('Python', 0) + 10
    
    # If code has indentation-based blocks (4+ spaces), boost Python
    if re.search(r'\n    [^\s]', code):
        scores['Python'] = scores.get('Python', 0) + 5
    
    # If code has NO semicolons at end of lines, boost Python
    if not re.search(r';[\s]*$', code, re.MULTILINE):
        scores['Python'] = scores.get('Python', 0) + 3
    
    # Penalize C if no semicolons found
    if 'C' in scores and not re.search(r';', code):
        scores['C'] = max(0, scores['C'] - 5)

    # Step 1.6: Additional Python-specific heuristics

# Detect common Python built-in functions
    if re.search(r'\bprint\s*\(', code):
        scores['Python'] = scores.get('Python', 0) + 5

    if re.search(r'\bmap\s*\(', code):
        scores['Python'] = scores.get('Python', 0) + 3

    if re.search(r'\bstr\s*\(', code):
        scores['Python'] = scores.get('Python', 0) + 2

    if re.search(r'\blen\s*\(', code):
        scores['Python'] = scores.get('Python', 0) + 2

    # Detect Python list multiplication (e.g., [5] * 3)
    if re.search(r'\[\s*\d+\s*\]\s*\*\s*\d+', code):
        scores['Python'] = scores.get('Python', 0) + 4

    # Detect list literals like [1, 2, 3]
    if re.search(r'\[\s*\d+(?:\s*,\s*\d+)+\s*\]', code):
        scores['Python'] = scores.get('Python', 0) + 3

    # Detect Python-style comments
    if re.search(r'^\s*#', code, re.MULTILINE):
        scores['Python'] = scores.get('Python', 0) + 2

    # Detect absence of semicolons (typical in Python)
    if not re.search(r';', code):
        scores['Python'] = scores.get('Python', 0) + 2

    # Step 2: Pygments-based detection (adds bonus score)
    try:
        lexer = guess_lexer(code)
        pygments_lang = lexer.name
        # Normalize Pygments name
        for lang in LANGUAGE_PATTERNS:
            if lang.lower() in pygments_lang.lower():
                scores[lang] = scores.get(lang, 0) + 8  # Increased weight
                break
    except ClassNotFound:
        pass

    # Step 3: Compute confidence percentages
    if not scores:
        return "Unknown", {}

    total = sum(scores.values())
    confidence = {
        lang: round((score / total) * 100, 1)
        for lang, score in sorted(scores.items(), key=lambda x: -x[1])
    }

    detected = max(scores, key=scores.get)
    return detected, confidence


def get_token_stats(code: str) -> dict:
    """
    NLP: Token frequency analysis
    Returns stats about the code tokens
    """
    tokens = tokenize_code(code)
    freq = Counter(tokens)
    lines = code.strip().split('\n')

    return {
        "total_tokens": len(tokens),
        "unique_tokens": len(set(tokens)),
        "total_lines": len(lines),
        "avg_tokens_per_line": round(len(tokens) / max(len(lines), 1), 2),
        "top_keywords": freq.most_common(10),
        "bigrams": get_ngrams(tokens, 2)[:5]
    }
