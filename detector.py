"""
detector.py — Programming Language Detector v2.0 (FIXED)
NLP BASED CODE INTERPRETER
Fix: Java, C++, C were being incorrectly scored as Python
Uses priority scoring with exclusive markers and negative scoring
"""

import re
from collections import Counter
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound


# ── EXCLUSIVE MARKERS ─────────────────────────────────────────
# If ANY of these are found, that language gets a massive priority boost
# and Python score is penalized — these CANNOT appear in Python
EXCLUSIVE_MARKERS = {
    "Java": [
        r'\bSystem\.out\.print(ln)?\s*\(',   # System.out.println(
        r'\bpublic\s+static\s+void\s+main\b',# public static void main
        r'\bimport\s+java\.',                 # import java.
        r'\bnew\s+[A-Z][a-zA-Z]+\s*[<(]',   # new ArrayList<> / new Obj(
        r'\bArrayList\b',
        r'\bHashMap\b',
        r'\bHashTable\b|\bHashtable\b',
        r'\bVector\b',
        r'@Override',
        r'\bpublic\s+class\b',
        r'\bprivate\s+\w+\s+\w+\s*;',       # private int x;
        r'\bvoid\s+\w+\s*\(',                # void methodName(
    ],
    "C++": [
        r'#include\s*<iostream>',
        r'#include\s*<vector>',
        r'#include\s*<string>',
        r'\bstd::\w+',                        # std::cout
        r'\bcout\s*<<',
        r'\bcin\s*>>',
        r'\bendl\b',
        r'using\s+namespace\s+std',
        r'\btemplate\s*<',
        r'::\s*\w+',                          # scope resolution
    ],
    "C": [
        r'#include\s*<stdio\.h>',
        r'#include\s*<stdlib\.h>',
        r'#include\s*<string\.h>',
        r'\bprintf\s*\(',
        r'\bscanf\s*\(',
        r'\bint\s+main\s*\(\s*(void|int)',
        r'\bmalloc\s*\(',
        r'\bfree\s*\(',
        r'\bstruct\s+\w+\s*\{',
        r'->\w+',                             # pointer->member
    ],
    "JavaScript": [
        r'\bconsole\.log\s*\(',
        r'\bdocument\.\w+',
        r'\bwindow\.\w+',
        r'\bconst\s+\w+\s*=',
        r'\blet\s+\w+\s*=',
        r'=>\s*[\{(]',                        # arrow function
        r'\bPromise\b',
        r'\basync\s+function\b',
        r'\bawait\b',
        r'require\s*\(',
        r'module\.exports',
    ],
    "TypeScript": [
        r':\s*(string|number|boolean|void|any|never)\b',
        r'\binterface\s+\w+\s*\{',
        r'\benum\s+\w+\s*\{',
        r'<[A-Z]\w*>',                        # generics
        r'\bReadonly\b',
        r'\bPartial\b',
        r'\.ts\b',
    ],
    "Python": [
        r'\bdef\s+\w+\s*\([^)]*\)\s*:',      # def func():
        r'\bimport\s+[a-z_]+$',              # import os
        r'\bfrom\s+\w+\s+import\b',          # from x import y
        r'\bself\.\w+',                       # self.attr
        r'\belif\b',                          # elif (Python only)
        r'\bTrue\b|\bFalse\b|\bNone\b',      # Python literals
        r'\bprint\s*\(',                      # print(
        r'^\s*#.*$',                          # Python comments
    ],
    "SQL": [
        r'\bSELECT\b.+\bFROM\b',
        r'\bINSERT\s+INTO\b',
        r'\bCREATE\s+TABLE\b',
        r'\bALTER\s+TABLE\b',
        r'\bDROP\s+TABLE\b',
        r'\bWHERE\b.+\bAND\b',
    ],
    "Go": [
        r'\bpackage\s+main\b',
        r'\bfunc\s+\w+\s*\(',
        r'\bfmt\.\w+\(',
        r':=',
        r'\bgoroutine\b',
        r'\bchan\b',
    ],
    "Kotlin": [
        r'\bfun\s+\w+\s*\(',
        r'\bval\s+\w+\s*:',
        r'\bvar\s+\w+\s*:',
        r'\bprintln\s*\(',
        r'\bdata\s+class\b',
        r'\?[.:]',                            # nullable ?.
    ],
    "Ruby": [
        r'\bputs\s+',
        r'\battr_accessor\b',
        r'\.each\s+do\b',
        r'\bdo\s*\|',
        r'\bend\b\s*$',
    ],
    "PHP": [
        r'<\?php',
        r'\$[a-zA-Z_]\w*',                   # $variable
        r'\becho\s+',
        r'->\w+\(',
    ],
}

# ── PATTERN SCORING ──────────────────────────────────────────
LANGUAGE_PATTERNS = {
    "Python":     [r'\bdef\b', r'\belif\b', r'\bself\b', r'\bTrue\b',
                   r'\bFalse\b', r'\bNone\b', r'\bprint\s*\(', r':\s*$',
                   r'\bimport\b', r'\bfrom\b', r'\bclass\b', r'\blambda\b'],
    "Java":       [r'\bpublic\b', r'\bprivate\b', r'\bvoid\b', r'\bclass\b',
                   r'\bstatic\b', r'\bnew\b', r'\bimport\b', r'\bthrows\b'],
    "C++":        [r'#include', r'\bcout\b', r'\bcin\b', r'\bnamespace\b',
                   r'std::', r'\btemplate\b', r'endl'],
    "C":          [r'#include', r'\bprintf\b', r'\bscanf\b', r'\bint\s+main\b',
                   r'\bmalloc\b', r'\bfree\b', r'\bstruct\b'],
    "JavaScript": [r'\bconst\b', r'\blet\b', r'\bconsole\b', r'\bfunction\b',
                   r'=>', r'\bdocument\b', r'\bwindow\b'],
    "TypeScript": [r':\s*string\b', r':\s*number\b', r'\binterface\b', r'\benum\b'],
    "SQL":        [r'\bSELECT\b', r'\bFROM\b', r'\bWHERE\b', r'\bINSERT\b',
                   r'\bCREATE\b', r'\bJOIN\b'],
    "Go":         [r'\bpackage\b', r'\bfunc\b', r'\bfmt\b', r':=',
                   r'\bchan\b', r'\bdefer\b'],
    "Kotlin":     [r'\bfun\b', r'\bval\b', r'\bvar\b', r'\bprintln\b',
                   r'\bwhen\b', r'\?\.'],
    "Ruby":       [r'\bputs\b', r'\bend\b', r'\bdo\b', r'\brequire\b',
                   r'\.each\b'],
    "PHP":        [r'<\?php', r'\$\w+', r'\becho\b', r'\barray\b'],
}

# ── NEGATIVE SCORING ─────────────────────────────────────────
# These patterns REDUCE a language's score
NEGATIVE_PATTERNS = {
    "Python": [
        r'\bSystem\.out\b',    # Java
        r'\bcout\b',           # C++
        r'\bprintf\b',         # C
        r'<\?php',             # PHP
        r'\$\w+',              # PHP
        r'\bpublic\s+static\b',# Java
        r'#include',           # C/C++
        r'\bpackage\s+\w+\s*;',# Java package declaration
        r'import\s+java\.',    # Java import
    ],
    "Java": [
        r'\bself\b',           # Python
        r'\belif\b',           # Python
        r'cout\s*<<',          # C++
        r'std::',              # C++
        r'<\?php',             # PHP
    ],
    "C++": [
        r'\bSystem\.out\b',    # Java
        r'\bself\b',           # Python
        r'\belif\b',           # Python
        r'<\?php',             # PHP
    ],
}


def tokenize_code(code: str) -> list:
    """NLP: Tokenization — breaks code into tokens"""
    return re.findall(r'[a-zA-Z_]\w*|[{}()\[\];,.]|"[^"]*"|\'[^\']*\'|\d+', code)


def get_ngrams(tokens: list, n: int = 2) -> list:
    """NLP: N-gram analysis"""
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def detect_language(code: str) -> tuple:
    """
    Improved language detection using:
    1. Exclusive marker detection (strongest signal)
    2. Pattern frequency scoring
    3. Negative scoring (penalize wrong language)
    4. Pygments verification
    Returns: (detected_language, confidence_dict)
    """
    if not code or not code.strip():
        return "Unknown", {}

    scores = {}

    # ── STEP 1: Check exclusive markers (highest priority) ────
    exclusive_hits = {}
    for lang, patterns in EXCLUSIVE_MARKERS.items():
        hits = 0
        for p in patterns:
            if re.search(p, code, re.MULTILINE | re.IGNORECASE):
                hits += 1
        if hits > 0:
            exclusive_hits[lang] = hits

    # If we have exclusive hits, heavily weight them
    if exclusive_hits:
        for lang, hits in exclusive_hits.items():
            scores[lang] = hits * 20  # Strong boost

    # ── STEP 2: General pattern scoring ───────────────────────
    for lang, patterns in LANGUAGE_PATTERNS.items():
        base = scores.get(lang, 0)
        for p in patterns:
            matches = re.findall(p, code, re.MULTILINE | re.IGNORECASE)
            base += len(matches)
        scores[lang] = base

    # ── STEP 3: Apply negative scoring ───────────────────────
    for lang, neg_patterns in NEGATIVE_PATTERNS.items():
        penalty = 0
        for p in neg_patterns:
            if re.search(p, code, re.MULTILINE | re.IGNORECASE):
                penalty += 15  # Hard penalty
        if penalty > 0 and lang in scores:
            scores[lang] = max(0, scores[lang] - penalty)

    # ── STEP 4: Structural heuristics ────────────────────────
    # Java specific: has semicolons at end + braces style
    if re.search(r';\s*$', code, re.MULTILINE) and \
       re.search(r'\bclass\b.+\{', code, re.MULTILINE):
        if not re.search(r'std::|cout|cin', code):  # not C++
            scores["Java"] = scores.get("Java", 0) + 10

    # Python specific: indentation-based, no semicolons at line end
    has_semicolons = bool(re.search(r';\s*$', code, re.MULTILINE))
    has_def_colon = bool(re.search(r'\bdef\s+\w+\s*\([^)]*\)\s*:', code))
    has_class_colon = bool(re.search(r'\bclass\s+\w+.*:', code))
    if not has_semicolons and (has_def_colon or has_class_colon):
        scores["Python"] = scores.get("Python", 0) + 8

    # C/C++ has #include
    if re.search(r'^#include', code, re.MULTILINE):
        if re.search(r'std::|cout|cin|namespace', code):
            scores["C++"] = scores.get("C++", 0) + 12
        else:
            scores["C"] = scores.get("C", 0) + 12

    # PHP must have <?php
    if not re.search(r'<\?php', code, re.IGNORECASE):
        scores.pop("PHP", None)

    # ── STEP 5: Pygments cross-check ─────────────────────────
    try:
        lexer = guess_lexer(code)
        pygments_lang = lexer.name.lower()
        for lang in LANGUAGE_PATTERNS:
            if lang.lower() in pygments_lang:
                scores[lang] = scores.get(lang, 0) + 10
                break
    except (ClassNotFound, Exception):
        pass

    # ── STEP 6: Remove zero-score languages ──────────────────
    scores = {k: v for k, v in scores.items() if v > 0}

    if not scores:
        return "Unknown", {}

    # ── STEP 7: Compute confidence percentages ────────────────
    total = sum(scores.values())
    confidence = {
        lang: round((score / total) * 100, 1)
        for lang, score in sorted(scores.items(), key=lambda x: -x[1])
    }

    detected = max(scores, key=scores.get)
    return detected, confidence


def get_token_stats(code: str) -> dict:
    """NLP: Token frequency analysis"""
    tokens = tokenize_code(code)
    freq = Counter(tokens)
    lines = code.strip().split('\n')
    return {
        "total_tokens": len(tokens),
        "unique_tokens": len(set(tokens)),
        "total_lines": len(lines),
        "avg_tokens_per_line": round(len(tokens) / max(len(lines), 1), 2),
        "top_keywords": freq.most_common(10),
        "bigrams": get_ngrams(tokens, 2)[:5],
    }
