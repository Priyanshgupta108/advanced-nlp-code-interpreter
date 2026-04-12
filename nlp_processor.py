"""
nlp_processor.py — Core NLP Processing Pipeline
NLP BASED CODE INTERPRETER
Covers: Tokenization, Stop Word Removal, Stemming, TF-IDF, Keyword Extraction
"""

import re
import math
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Download required NLTK data
for pkg in ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass


# ─────────────────────────────────────────────
# Programming language specific stop words
# (keywords that appear everywhere, low info value)
# ─────────────────────────────────────────────
CODE_STOPWORDS = {
    'if', 'else', 'elif', 'for', 'while', 'do', 'return', 'break',
    'continue', 'import', 'from', 'class', 'def', 'function', 'var',
    'let', 'const', 'int', 'string', 'bool', 'float', 'void', 'null',
    'true', 'false', 'none', 'new', 'this', 'self', 'public', 'private',
    'static', 'final', 'the', 'a', 'an', 'is', 'are', 'was', 'were'
}


class NLPProcessor:
    """
    Full NLP pipeline for code analysis.
    Demonstrates core NLP techniques on source code.
    """

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english')) | CODE_STOPWORDS
        except Exception:
            self.stop_words = CODE_STOPWORDS

    # ─────────────────────────────────────────
    # NLP CONCEPT 1: Tokenization
    # Splitting raw text into individual tokens
    # ─────────────────────────────────────────
    def tokenize(self, text: str) -> list:
        """Split code/text into tokens"""
        # Extract words and identifiers
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', text)
        return tokens

    # ─────────────────────────────────────────
    # NLP CONCEPT 2: Stop Word Removal
    # Removing common/unimportant words
    # ─────────────────────────────────────────
    def remove_stopwords(self, tokens: list) -> list:
        """Remove stop words from token list"""
        return [t for t in tokens if t.lower() not in self.stop_words and len(t) > 1]

    # ─────────────────────────────────────────
    # NLP CONCEPT 3: Stemming
    # Reducing words to their root form
    # e.g., running → run, classes → class
    # ─────────────────────────────────────────
    def stem(self, tokens: list) -> list:
        """Apply Porter Stemming to tokens"""
        return [self.stemmer.stem(t.lower()) for t in tokens]

    # ─────────────────────────────────────────
    # NLP CONCEPT 4: Lemmatization
    # More accurate root form (uses vocabulary)
    # e.g., running → run, better → good
    # ─────────────────────────────────────────
    def lemmatize(self, tokens: list) -> list:
        """Apply WordNet Lemmatization to tokens"""
        return [self.lemmatizer.lemmatize(t.lower()) for t in tokens]

    # ─────────────────────────────────────────
    # NLP CONCEPT 5: TF-IDF
    # Term Frequency - Inverse Document Frequency
    # Finds the most "important" words in code
    # ─────────────────────────────────────────
    def compute_tfidf(self, code: str) -> dict:
        """
        Compute TF-IDF scores for code tokens.
        Higher score = more important/unique identifier.
        """
        # Split code into "documents" by function/line blocks
        lines = [line for line in code.split('\n') if line.strip()]
        if len(lines) < 2:
            lines = [code]

        # Tokenize each line
        docs = [self.tokenize(line) for line in lines]
        docs = [self.remove_stopwords(doc) for doc in docs]
        docs = [doc for doc in docs if doc]

        if not docs:
            return {}

        # Flatten all tokens
        all_tokens = [t.lower() for doc in docs for t in doc]
        vocab = set(all_tokens)

        # Term Frequency (in full code)
        tf_counter = Counter(all_tokens)
        total_terms = len(all_tokens)

        tf = {term: count / total_terms for term, count in tf_counter.items()}

        # Inverse Document Frequency
        N = len(docs)
        idf = {}
        for term in vocab:
            df = sum(1 for doc in docs if term in [t.lower() for t in doc])
            idf[term] = math.log(N / (1 + df)) + 1

        # TF-IDF Score
        tfidf = {term: round(tf[term] * idf[term], 4) for term in vocab}

        # Return top keywords sorted by score
        return dict(sorted(tfidf.items(), key=lambda x: -x[1])[:15])

    # ─────────────────────────────────────────
    # NLP CONCEPT 6: Comment Language Detection
    # Detects human language in code comments
    # ─────────────────────────────────────────
    def extract_comments(self, code: str) -> list:
        """Extract all comments from code"""
        comments = []
        # Single line comments: //, #
        single = re.findall(r'(?://|#)\s*(.+)', code)
        comments.extend(single)
        # Multi-line comments: /* */ or """ """
        multi = re.findall(r'/\*[\s\S]*?\*/|"""[\s\S]*?"""', code)
        comments.extend(multi)
        return [c.strip() for c in comments if c.strip()]

    def detect_comment_language(self, code: str) -> str:
        """Detect human language in comments (simplified heuristic)"""
        comments = self.extract_comments(code)
        if not comments:
            return "No comments found"

        combined = ' '.join(comments).lower()

        # Language word sets
        hindi_words = {'hai', 'ka', 'ki', 'ke', 'aur', 'yeh', 'woh', 'main', 'hoon', 'karo'}
        french_words = {'le', 'la', 'les', 'un', 'une', 'est', 'sont', 'pour', 'dans', 'avec'}
        spanish_words = {'el', 'la', 'los', 'un', 'una', 'es', 'son', 'para', 'con', 'que'}
        german_words = {'der', 'die', 'das', 'ein', 'eine', 'ist', 'sind', 'und', 'für', 'mit'}

        words = set(combined.split())
        scores = {
            'Hindi (Roman)': len(words & hindi_words),
            'French': len(words & french_words),
            'Spanish': len(words & spanish_words),
            'German': len(words & german_words),
            'English': len([w for w in words if re.match(r'^[a-z]+$', w)])
        }
        return max(scores, key=scores.get)

    # ─────────────────────────────────────────
    # Full Pipeline: Run all NLP steps
    # ─────────────────────────────────────────
    def full_pipeline(self, code: str) -> dict:
        """Run complete NLP pipeline and return all results"""
        tokens = self.tokenize(code)
        no_stop = self.remove_stopwords(tokens)
        stemmed = self.stem(no_stop)
        lemmatized = self.lemmatize(no_stop)
        tfidf = self.compute_tfidf(code)
        comments = self.extract_comments(code)
        comment_lang = self.detect_comment_language(code)

        return {
            "raw_tokens": tokens[:20],
            "after_stopword_removal": no_stop[:20],
            "stemmed": stemmed[:20],
            "lemmatized": lemmatized[:20],
            "tfidf_keywords": tfidf,
            "comments_found": comments,
            "comment_language": comment_lang,
            "total_tokens": len(tokens),
            "unique_identifiers": len(set(no_stop)),
        }
