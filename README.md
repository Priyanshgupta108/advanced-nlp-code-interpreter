<div align="center">

# 🧠 NeuraCode: AI Code Interpreter

**An NLP-powered, AI-assisted code analysis tool**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://neuracode.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq_API-LLaMA_3.1-00A67E?style=for-the-badge)](https://console.groq.com)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

### 🚀 [Live Demo → neuracode.streamlit.app](https://neuracode.streamlit.app)

</div>

---

## 📖 Overview

NeuraCode is an AI-powered code analysis platform built with Python and Streamlit. It combines NLP techniques with LLM APIs to analyze source code — detecting its language, explaining its logic, translating it, visualizing structure, detecting bugs, and providing an interactive AI chat assistant.

**Key principle:** Local processing everywhere possible. Groq API only for AI-specific tasks.

---

## ✨ Features

### 🔍 Step 1 — NLP Analysis (100% Local, No API)
| Feature | Method |
|---|---|
| Language Detection | Regex + Pygments pattern matching |
| Tokenization | NLTK |
| Stop Word Removal | NLTK corpus |
| Stemming | Porter Stemmer |
| Lemmatization | WordNet Lemmatizer |
| TF-IDF Keywords | scikit-learn |
| N-gram Analysis | Custom |
| Comment Language | Regex |

### ⚡ Step 2 — AI Features (Groq API, on-demand only)
| Tab | Feature |
|---|---|
| 📖 Explain | Plain English explanation |
| 🔄 Translate | Convert between 8 languages |
| 📈 Complexity | Big O analysis + optimized version |
| 🐛 Bugs | Bug detection + fixed code |
| 🧪 Tests | Normal, edge, and error test cases |
| 📝 Pseudocode | Plain English steps |
| 🔢 Algorithm | Name + concept + complexity |
| 🔀 Approaches | Brute force → optimized → best |

### 🎨 Step 3 — Visualizations (100% Local, No API)
| Feature | Description |
|---|---|
| 🗺️ Flowchart | Graphviz control flow diagram with zoom + pan |
| ▶️ Step Executor | Python line-by-line tracer (like pythontutor.com) |
| 🌡️ Heatmap | Line-by-line readability scoring (0-100) |
| 🔬 Line Visualizer | POS tagging — classifies each line by type |

### 🤖 AI Chat Assistant
- Full conversation memory
- Groq API — only called when message is sent
- Context-aware answers about the pasted code

---

## 🏗️ Architecture

```
Code Input
    │
    ├── NLP Pipeline (Local)
    │   ├── detector.py       — Language detection
    │   ├── nlp_processor.py  — Full NLP pipeline
    │   └── visualizer.py     — Flowchart generation
    │
    ├── AI Layer (Groq API — on-demand)
    │   └── api_handler.py    — 9 AI feature methods
    │
    ├── Visualization Layer (Local)
    │   ├── heatmap_generator.py   — Readability heatmap
    │   ├── code_visualizer.py     — Line-by-line analysis
    │   └── step_visualizer.py     — Python execution tracer
    │
    └── Data Layer (Supabase — auth users only)
        ├── history_manager.py  — CRUD via REST API
        └── auth_manager.py     — Email/password auth
```

---

## 📁 Project Structure

```
NeuraCode/
├── app.py                  # Main Streamlit app (entry point)
├── api_handler.py          # Groq API integration
├── detector.py             # Language detection (local)
├── nlp_processor.py        # NLP pipeline (local)
├── visualizer.py           # Graphviz flowchart (local)
├── heatmap_generator.py    # Readability heatmap (local)
├── code_visualizer.py      # Line-by-line visualizer (local)
├── step_visualizer.py      # Python execution tracer (local)
├── history_manager.py      # Supabase REST API client
├── auth_manager.py         # Supabase Auth client
├── requirements.txt        # Dependencies
├── packages.txt            # System packages (Graphviz)
├── supabase_setup.sql      # Database schema
└── .streamlit/
    └── secrets.toml        # API keys (not in repo)
```

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10.11 | Core language |
| Streamlit | 1.32.0 | Web UI |
| Groq API | llama-3.1-8b-instant | AI features |
| Supabase | Free tier | Database + Auth |
| NLTK | 3.8.1 | NLP processing |
| Pygments | 2.17.2 | Language detection |
| scikit-learn | 1.4.0 | TF-IDF |
| Graphviz | 0.20.3 | Flowcharts |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- Graphviz installed on system

### 1. Clone the repository
```bash
git clone https://github.com/Priyanshgupta108/code-detect-explain-translate-nlp.git
cd code-detect-explain-translate-nlp
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Graphviz to PATH (Windows)
```powershell
$env:Path += ";C:\Program Files\Graphviz\bin"
```

### 4. Run the app
```bash
python -m streamlit run app.py
```

### 5. Open in browser
```
http://localhost:8501
```

### 6. Get your free Groq API key
Visit [console.groq.com](https://console.groq.com) → Sign up → API Keys → Create

---

## ☁️ Deploy on Streamlit Cloud

### Step 1 — Push to GitHub
```bash
git add .
git commit -m "NeuraCode v3.1 final"
git push origin main
```

### Step 2 — Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app** → Select your repo → Branch: `main` → File: `app.py`
3. Click **Deploy**

### Step 3 — Add Secrets
In app settings → **Secrets**, paste:
```toml
SUPABASE_URL = "https://xysdsmdgiklcysrmtibd.supabase.co"
SUPABASE_KEY = "your_supabase_anon_key"
```

### Step 4 — Add packages.txt
Create `packages.txt` in repo root:
```
graphviz
```

---

## 🗄️ Supabase Setup

Run `supabase_setup.sql` in Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS code_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    code_hash TEXT NOT NULL,
    language TEXT, code TEXT,
    explanation TEXT, translation TEXT, complexity TEXT,
    bugs TEXT, test_cases TEXT, pseudocode TEXT,
    algorithm TEXT, approaches TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
ALTER TABLE code_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "User owns their history" ON code_history
FOR ALL TO authenticated USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());
CREATE POLICY "Anonymous access" ON code_history
FOR ALL TO anon USING (user_id IS NULL) WITH CHECK (user_id IS NULL);
```

Also go to: **Authentication → Settings → Disable email confirmation** for easier testing.

---

## 🔒 Privacy Model

| Mode | History | Database |
|---|---|---|
| 👤 Logged In | ✅ Saved per user | ✅ Stored in Supabase |
| 👻 Guest | ❌ Not saved | ❌ Nothing stored |

Guest mode is fully incognito — zero database writes.

---

## ⚡ Performance Features

- `@st.cache_resource` — managers and NLP processor initialized once
- `@st.cache_resource` — API handler cached per key
- `@st.cache_data(ttl=3600)` — NLP results, flowcharts, heatmaps cached 1 hour
- **Lazy loading** — visualizations only render when button clicked
- **Groq API lazy** — only called on button click, never on page load
- **Cache-first** — same code analyzed twice = 0 API calls

---

## 📱 Mobile Support

- API key input visible on main screen (sidebar hidden on mobile)
- Responsive metric cards stack vertically on small screens
- Touch-friendly buttons and inputs
- Streamlit's native mobile viewport handling

---

## 🧠 NLP Concepts Demonstrated

1. **Tokenization** — breaking code into tokens
2. **Stop Word Removal** — filtering common words
3. **Stemming** — Porter Stemmer reduces words to root
4. **Lemmatization** — WordNet reduces to dictionary form
5. **TF-IDF** — Term Frequency-Inverse Document Frequency scoring
6. **N-gram Analysis** — context windows for language detection
7. **Pattern Matching** — regex-based keyword detection
8. **Language Detection** — combined approach with confidence scores
9. **POS Tagging (Code)** — classifying code tokens by syntactic role
10. **Control Flow Parsing** — extracting program structure

---

## 📄 Requirements

```
streamlit==1.32.0
groq
pygments==2.17.2
nltk==3.8.1
graphviz==0.20.3
scikit-learn==1.4.0
supabase
requests
```

**packages.txt** (for Streamlit Cloud):
```
graphviz
```

---

## 👨‍💻 Author

**Priyansh Gupta**
B.Tech CSE (Data Science) — NLP Laboratory Project 2024-25

[![GitHub](https://img.shields.io/badge/GitHub-Priyanshgupta108-181717?style=flat&logo=github)](https://github.com/Priyanshgupta108)

---

## 📜 License

MIT License — free to use and modify.

---

<div align="center">
<b>⭐ Star this repo if it helped you!</b>
</div>