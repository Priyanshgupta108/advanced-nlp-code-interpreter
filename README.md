# 🧠 NLP-Based Code Interpreter AI
### Paste any code. Understand everything about it.

An advanced NLP-driven application that detects programming languages, explains code in plain English, translates between languages, visualizes logic as flowcharts, analyzes complexity, detects bugs, and generates test cases. Built using **Python, Streamlit, Supabase, and AI APIs**, this tool bridges the gap between human understanding and machine logic.

---

## 🚀 Live Demo
🔗 *Add your deployed Streamlit app link here*

---

## ✨ Features

### 🔍 Code Intelligence
- **Language Detector** – Detects programming languages with confidence scores.
- **Plain English Explainer** – Explains code in simple terms.
- **Code Translator** – Converts code between programming languages.

### 📊 Analysis & Optimization
- **Complexity Analyzer** – Provides Big-O analysis and optimization suggestions.
- **Bug Detector** – Identifies bugs and suggests fixes.
- **Test Case Generator** – Generates normal, edge, and error test cases.

### 📈 Visualizations
- **Flowchart Visualizer** – Generates control flow diagrams.
- **Heatmap Generator** – Displays readability and complexity insights.
- **Step-by-Step Execution** – Visualizes code execution flow.

### 🔐 User Features
- **Secure Authentication** – Login and signup using Supabase.
- **Chat History Sidebar** – Stores and retrieves previous analyses.
- **Interactive UI** – Built with Streamlit for a seamless experience.

---

## 🔬 NLP Concepts Demonstrated

- **Tokenization** – Breaking code into meaningful tokens  
- **Stop Word Removal** – Filtering low-value keywords  
- **Stemming** – Root word extraction using Porter Stemmer  
- **Lemmatization** – Vocabulary-based normalization using WordNet  
- **TF-IDF** – Identifying important identifiers in code  
- **N-gram Analysis** – Pattern detection using bigrams  
- **Pattern Matching** – Regex-based language classification  
- **Named Entity Recognition (NER)** – Identifying functions and classes  
- **Control Flow Parsing** – Generating logical flowcharts  

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| Frontend | Streamlit, HTML, CSS |
| Backend | Python |
| NLP Libraries | NLTK, Pygments, Scikit-learn |
| AI Integration | Groq API / Gemini API |
| Visualization | Graphviz, Matplotlib |
| Authentication & Database | Supabase |
| Version Control | Git & GitHub |
| Deployment | Streamlit Community Cloud |

---

## 📁 Project Structure
Code-Interpreter-AI/
│── .streamlit/
│ └── secrets.toml
│── app.py
│── auth_manager.py
│── api_handler.py
│── detector.py
│── nlp_processor.py
│── history_manager.py
│── code_visualizer.py
│── heatmap_generator.py
│── step_visualizer.py
│── visualizer.py
│── supabase_setup.sql
│── requirements.txt
│── README.md
│── Project_Report.docx

---

## ⚙️ Installation and Setup

1️⃣ Clone the Repository
```bash
git clone https://github.com/Priyanshgupta108/code-detect-explain-translate-nlp.git
cd code-detect-explain-translate-nlp

2️⃣ Create a Virtual Environment
python -m venv venv
3️⃣ Activate the Environment
Windows
venv\Scripts\activate
Mac/Linux
source venv/bin/activate

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Install Graphviz
Windows: Download from https://graphviz.org/download/
 and select "Add to PATH"
Ubuntu/Debian:
sudo apt-get install graphviz
macOS:
brew install graphviz

6️⃣ Configure Secrets
Create a .streamlit/secrets.toml file:
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
GROQ_API_KEY = "your_groq_api_key"
# Optional
GEMINI_API_KEY = "your_gemini_api_key"

7️⃣ Run the Application
streamlit run app.py

8️⃣ Open in Browser
http://localhost:8501
