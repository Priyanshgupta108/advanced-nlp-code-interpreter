# 🧠 NLP Based Code Interpreter

> Paste any code. Understand everything about it.

A powerful NLP-driven tool that detects programming languages, explains code in plain English, translates between languages, visualizes logic as flowcharts, analyzes complexity, detects bugs, and generates test cases — all powered by core NLP concepts.

---

## ✨ Features

| Feature | Description | NLP Concept |
|---|---|---|
| 🔍 Language Detector | Detects programming language with confidence scores | Pattern Matching, Tokenization |
| 📖 Plain English Explainer | Explains what code does in simple terms | Text Generation, Summarization |
| 🔄 Code Translator | Translates code between programming languages | Sequence-to-Sequence NLP |
| 🗺️ Flowchart Visualizer | Generates control flow diagram from code | Structural Parsing, Graph Analysis |
| 📈 Complexity Analyzer | Big O time/space analysis + optimized version | Code Analysis |
| 🐛 Bug Detector | Finds bugs, code smells, and suggests fixes | Text Classification |
| 🧪 Test Case Generator | Auto-generates normal, edge, and error test cases | Text Generation |

---

## 🔬 NLP Concepts Demonstrated

- **Tokenization** — Breaking code into meaningful tokens
- **Stop Word Removal** — Filtering out common/low-value keywords
- **Stemming** — Reducing words to root form (Porter Stemmer)
- **Lemmatization** — Vocabulary-based root form (WordNet)
- **TF-IDF** — Finding most important identifiers in code
- **N-gram Analysis** — Bigram extraction for pattern detection
- **Pattern Matching** — Regex-based language classification
- **Named Entity Recognition** — Detecting function/class names
- **Control Flow Parsing** — Structural analysis for flowcharts

---

## 🛠️ Tech Stack

- **Frontend** — Streamlit
- **NLP** — NLTK, Pygments, scikit-learn
- **AI Features** — Google Gemini API (gemini-2.5-flash)
- **Visualization** — Graphviz
- **Language** — Python 3.10+

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/NLP-Code-Interpreter.git
cd NLP-Code-Interpreter
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Graphviz (system-level)
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Windows
# Download from https://graphviz.org/download/
# Make sure to check "Add to PATH" during installation
```

### 4. Get a FREE Gemini API Key
- Go to [aistudio.google.com](https://aistudio.google.com)
- Sign in with your Google account
- Click **Get API Key** → **Create API Key**
- Copy the key (starts with `AIzaSy...`)

### 5. Run the app
```bash
python -m streamlit run app.py
```

### 6. Open in browser
```
http://localhost:8501
```

### 7. Paste your Gemini API key in the sidebar and start analyzing!

---

## 📁 Project Structure

```
NLP_Code_Interpreter/
├── app.py              # Main Streamlit application
├── detector.py         # Language detection (Tokenization + Pattern Matching)
├── nlp_processor.py    # NLP pipeline (Stemming, TF-IDF, Lemmatization)
├── api_handler.py      # Gemini API calls (Explain, Translate, Bugs, Tests)
├── visualizer.py       # Flowchart generation (Graphviz)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🎓 Academic Info

**Project Title:** NLP Based Code Interpreter  
**Subject:** Natural Language Processing Laboratory  
**Degree:** B.Tech CSE (Data Science)  

---

## 📸 Screenshots

> Add screenshots of your running app here after setup

---

## 📄 License

MIT License — feel free to use and modify for educational purposes.