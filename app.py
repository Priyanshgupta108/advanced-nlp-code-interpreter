"""
app.py — Main Application v3.0
NLP BASED CODE INTERPRETER
New: User Authentication, ChatGPT-style History Sidebar, Step-by-Step Visualizer
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from detector import detect_language, get_token_stats
from nlp_processor import NLPProcessor
from api_handler import APIHandler
from visualizer import generate_flowchart
from heatmap_generator import generate_heatmap, render_heatmap_html, get_readability_summary
from code_visualizer import generate_visualization, render_visualization_html
from history_manager import HistoryManager
from auth_manager import AuthManager
from step_visualizer import trace_python_execution, render_step_visualizer

st.set_page_config(page_title="NeuraCode: AI Code Interpreter", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
import streamlit as st
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

st.markdown("""
<style>

/* App Background */
.stApp {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* Reduce Top Space */
.block-container {
    padding-top: 0.5rem !important;
}

/* Hide Streamlit Header and Toolbar */
header[data-testid="stHeader"] {
    background: transparent;
    height: 0rem;
}

div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}

/* Hide Streamlit Top Decoration (Removes Grey Box) */
div[data-testid="stDecoration"] {
    display: none;
}

/* Remove Empty Containers */
div[data-testid="stVerticalBlock"]:empty {
    display: none;
}

/* Text Area Styling */
.stTextArea textarea {
    background-color: #313244 !important;
    color: #cdd6f4 !important;
    font-family: 'Courier New', monospace !important;
    font-size: 14px !important;
    border: 1px solid #45475a !important;
    border-radius: 8px !important;
    caret-color: #ffffff !important;
}

/* Input Fields */
.stTextInput > div > div > input {
    background-color: #313244 !important;
    color: #cdd6f4 !important;
    border: 1px solid #45475a !important;
    border-radius: 6px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #cba6f7, #89b4fa);
    color: #1e1e2e;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-size: 15px;
}

/* Metric Cards */
.metric-card {
    background: #313244;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    border-left: 4px solid #cba6f7;
    margin: 5px;
}

.metric-card h3 {
    color: #cba6f7;
    font-size: 24px;
    margin: 0;
}

.metric-card p {
    color: #bac2de;
    font-size: 13px;
    margin: 0;
}

/* NLP Tags */
.nlp-tag {
    display: inline-block;
    background: #45475a;
    color: #89dceb;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    margin: 2px;
}

/* Badges */
.lang-badge {
    background: linear-gradient(135deg, #a6e3a1, #89dceb);
    color: #1e1e2e;
    padding: 8px 20px;
    border-radius: 20px;
    font-size: 20px;
    font-weight: bold;
}

.cache-badge {
    background: linear-gradient(135deg, #f9e2af, #fab387);
    color: #1e1e2e;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: bold;
}

.user-badge {
    background: linear-gradient(135deg, #cba6f7, #89b4fa);
    color: #1e1e2e;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}

/* Authentication Card */
.auth-card {
    background: #313244;
    border-radius: 12px;
    padding: 30px;
    max-width: 420px;
    margin: 10px auto;
    border: 1px solid #45475a;
    box-shadow: 0 0 25px rgba(0, 0, 0, 0.3);
}

/* Headers */
h1, h2, h3 {
    color: #cdd6f4 !important;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

defaults = {
    "api_key":"","code":"","lang":"","analyzed":False,
    "confidence":None,"token_stats":None,"nlp_results":None,
    "cached":False,"cached_data":None,"chat_messages":[],"ai_results":{},
    "logged_in":False,"user_id":None,"username":"","user_email":"","access_token":None,
    "history_records":[],"active_history_id":None,
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

history_mgr = HistoryManager(SUPABASE_URL, SUPABASE_KEY)
auth_mgr = AuthManager(SUPABASE_URL, SUPABASE_KEY)

def refresh_history():
    uid = st.session_state.get("user_id")
    st.session_state.history_records = history_mgr.get_user_history(uid)

def load_history_item(record_id):
    d = history_mgr.get_full_record(record_id)
    if d:
        st.session_state.code = d.get("code","")
        st.session_state.lang = d.get("language","")
        st.session_state.cached_data = d
        st.session_state.cached = True
        st.session_state.analyzed = True
        st.session_state.active_history_id = record_id
        st.session_state.chat_messages = []
        nlp = NLPProcessor()
        code = d.get("code","")
        detected,conf = detect_language(code)
        st.session_state.confidence = conf
        st.session_state.token_stats = get_token_stats(code)
        st.session_state.nlp_results = nlp.full_pipeline(code)

# ── AUTH PAGE ─────────────────────────────────────────────────
def show_auth_page():
    # st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("## 🧠 NLP Code Interpreter ")
        st.markdown("*Sign in to save your personal history*")
        st.divider()
        t1,t2,t3 = st.tabs(["🔐 Login","📝 Sign Up","👤 Guest"])
        with t1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        r = auth_mgr.sign_in(email, password)
                        if r["success"]:
                            st.session_state.logged_in = True
                            st.session_state.user_id = r.get("user_id")
                            st.session_state.user_email = r.get("email", email)
                            st.session_state.username = r.get("username", email.split("@")[0])
                            st.session_state.access_token = r.get("access_token")
                            refresh_history()
                            st.rerun()
                        else:
                            st.error("❌ " + r["message"])
                    else:
                        st.warning("Fill in all fields")
        with t2:
            with st.form("signup_form"):
                uname = st.text_input("Username", placeholder="Your name")
                email2 = st.text_input("Email", placeholder="you@example.com")
                pwd2 = st.text_input("Password", type="password", placeholder="Min 6 chars")
                cpwd = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if not email2 or not pwd2:
                        st.warning("Fill all fields")
                    elif pwd2 != cpwd:
                        st.error("Passwords don't match!")
                    elif len(pwd2) < 6:
                        st.error("Password too short (min 6)")
                    else:
                        r = auth_mgr.sign_up(email2, pwd2, uname)
                        if r["success"]:
                            st.success("✅ Account created! Login now.")
                        else:
                            st.error("❌ " + r["message"])
        with t3:
            st.info("No account needed. History won't be saved permanently.")
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user_id = None
                st.session_state.username = "Guest"
                refresh_history()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ── MAIN APP ──────────────────────────────────────────────────
def show_main_app():
    with st.sidebar:
        st.markdown(f"<span class='user-badge'>👤 {st.session_state.username}</span>", unsafe_allow_html=True)
        if st.session_state.user_email:
            st.caption(st.session_state.user_email)
        if st.button("🚪 Logout", use_container_width=True):
            for k in defaults: st.session_state[k] = defaults[k]
            st.rerun()
        st.divider()
        st.markdown("### 🔑 Groq API Key")
        ki = st.text_input("Key", type="password", placeholder="gsk_...", label_visibility="collapsed")
        if ki: st.session_state.api_key = ki
        if st.session_state.api_key: st.success("✅ Key saved!")
        st.caption("Free: console.groq.com")
        st.divider()

        # ChatGPT-style history
        st.markdown("### 🕐 History")
        col_r, col_n = st.columns([1,1])
        with col_r:
            if st.button("🔄", use_container_width=True, help="Refresh history"):
                refresh_history()
        with col_n:
            if st.button("✏️ New", use_container_width=True):
                st.session_state.analyzed = False
                st.session_state.code = ""
                st.session_state.cached = False
                st.session_state.cached_data = None
                st.session_state.active_history_id = None
                st.rerun()

        records = st.session_state.history_records
        if not records:
            st.caption("No history yet.")
        else:
            # Group by date like ChatGPT
            from datetime import datetime
            today = datetime.now().date()
            groups = {"Today": [], "Earlier": []}
            for rec in records[:30]:
                try:
                    rec_date = datetime.fromisoformat(str(rec.get("created_at",""))[:19]).date()
                    if rec_date == today:
                        groups["Today"].append(rec)
                    else:
                        groups["Earlier"].append(rec)
                except Exception:
                    groups["Earlier"].append(rec)

            for group, items in groups.items():
                if items:
                    st.caption(f"— {group} —")
                    for rec in items:
                        rid = rec.get("id","")
                        lang = rec.get("language","?")
                        preview = rec.get("code","")[:30].replace('\n',' ').strip()
                        is_active = rid == st.session_state.active_history_id
                        btn_style = "🔷" if is_active else "📄"
                        col1,col2 = st.columns([5,1])
                        with col1:
                            if st.button(f"{btn_style} {lang}: {preview}...", key=f"h_{rid}", use_container_width=True):
                                load_history_item(rid)
                                st.rerun()
                        with col2:
                            if st.button("✕", key=f"d_{rid}"):
                                history_mgr.delete_history(rid)
                                refresh_history()
                                st.rerun()

        st.divider()
        for c in ["🔤 Tokenization","🚫 Stop Words","🌱 Stemming","📖 Lemmatization",
                  "📊 TF-IDF","🔍 Pattern Matching","📐 N-grams","🌍 Lang Detection","🏷️ POS Tagging"]:
            st.markdown(f"<span class='nlp-tag'>{c}</span>", unsafe_allow_html=True)

    # ── MAIN CONTENT ──────────────────────────────────────────
    st.markdown("# 🧠 NLP Based Code Interpreter")
    st.markdown("Paste any code — detect, explain, translate, visualize, step-trace, and optimize.")
    st.divider()

    c1,c2 = st.columns([3,1])
    with c1:
        code_input = st.text_area("Code", height=250, label_visibility="collapsed",
            placeholder="Paste Python, Java, C++, JavaScript... any code here")
    with c2:
        st.markdown("### ⚙️ Options")
        auto = st.checkbox("Auto-detect language", value=True)
        manual_lang = None
        if not auto:
            manual_lang = st.selectbox("Language",["Python","Java","C++","C","JavaScript","TypeScript","Go","Kotlin","Ruby","SQL"])
        target_lang = st.selectbox("Translate To",["Java","Python","C++","JavaScript","Go","Kotlin","TypeScript","Ruby"])

    if st.button("🚀 Analyze Code", use_container_width=True):
        if not code_input.strip():
            st.error("⚠️ Paste some code first!")
        else:
            uid = st.session_state.get("user_id")
            cached = history_mgr.get_cached(code_input, uid)
            if cached:
                st.session_state.cached = True
                st.session_state.cached_data = cached
                st.session_state.lang = cached.get("language","Unknown")
                st.session_state.active_history_id = cached.get("id")
            else:
                st.session_state.cached = False
                st.session_state.cached_data = None
                st.session_state.active_history_id = None
            nlp = NLPProcessor()
            det,conf = detect_language(code_input)
            st.session_state.lang = manual_lang if manual_lang else det
            st.session_state.confidence = conf
            st.session_state.token_stats = get_token_stats(code_input)
            st.session_state.nlp_results = nlp.full_pipeline(code_input)
            st.session_state.code = code_input
            st.session_state.analyzed = True
            st.session_state.chat_messages = []
            st.session_state.ai_results = {}

    if st.session_state.analyzed:
        final_lang = st.session_state.lang
        code = st.session_state.code
        if st.session_state.cached:
            st.markdown("<div class='cache-badge'>⚡ From Cache — No API used!</div>", unsafe_allow_html=True)
            st.markdown("")

        # STEP 1
        st.divider()
        st.markdown("## 🔍 Step 1: NLP Analysis Pipeline")
        st.markdown(f"<div style='text-align:center;padding:10px;'><div class='lang-badge'>📦 Detected: {final_lang}</div></div>", unsafe_allow_html=True)
        if st.session_state.confidence:
            tc = dict(list(st.session_state.confidence.items())[:5])
            cols = st.columns(len(tc))
            for i,(lang,score) in enumerate(tc.items()):
                with cols[i]: st.markdown(f"<div class='metric-card'><h3>{score}%</h3><p>{lang}</p></div>", unsafe_allow_html=True)
        if st.session_state.token_stats:
            ts = st.session_state.token_stats
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(f"<div class='metric-card'><h3>{ts['total_tokens']}</h3><p>Tokens</p></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='metric-card'><h3>{ts['unique_tokens']}</h3><p>Unique</p></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-card'><h3>{ts['total_lines']}</h3><p>Lines</p></div>", unsafe_allow_html=True)
            with c4: st.markdown(f"<div class='metric-card'><h3>{ts['avg_tokens_per_line']}</h3><p>Tokens/Line</p></div>", unsafe_allow_html=True)
        if st.session_state.nlp_results:
            nr = st.session_state.nlp_results
            with st.expander("🔬 Full NLP Pipeline"):
                p1,p2 = st.columns(2)
                with p1:
                    st.markdown("**1️⃣ Tokens**"); st.code(' | '.join(nr['raw_tokens'][:15]))
                    st.markdown("**2️⃣ Stop Words Removed**"); st.code(' | '.join(nr['after_stopword_removal'][:15]))
                with p2:
                    st.markdown("**3️⃣ Stemmed**"); st.code(' | '.join(nr['stemmed'][:15]))
                    st.markdown("**4️⃣ Lemmatized**"); st.code(' | '.join(nr['lemmatized'][:15]))
                if nr.get('tfidf_keywords'):
                    st.markdown("**5️⃣ TF-IDF**")
                    tc2 = st.columns(5)
                    for i,(w,s) in enumerate(list(nr['tfidf_keywords'].items())[:10]):
                        with tc2[i%5]: st.markdown(f"<div class='metric-card'><h3>{s}</h3><p>{w}</p></div>", unsafe_allow_html=True)
                st.markdown(f"**6️⃣ Comment Language:** `{nr.get('comment_language','N/A')}`")

        # STEP 2
        st.divider()
        st.markdown("## ⚡ Step 2: AI-Powered Features")
        if not st.session_state.api_key:
            st.warning("⚠️ Enter Groq API Key in sidebar!")
        else:
            api = APIHandler(st.session_state.api_key)
            cd = st.session_state.cached_data or {}

                # Helper function for AI feature tabs
            def aitab(tab, key, label, ckey, fn, *args):
                with tab:
                    st.markdown(f"### {label}")
                    if cd.get(ckey):
                        st.info("⚡ Cached!")
                        st.markdown(cd[ckey])
                    elif st.button(label, key=key):
                        with st.spinner("Processing..."):
                            r = fn(*args)
                            st.markdown(r)
                            st.session_state.ai_results[ckey] = r

            # Initialize tab state
            if "active_tab" not in st.session_state:
                st.session_state.active_tab = 0

            tab_labels = [
                "📖 Explain","🔄 Translate","📈 Complexity","🐛 Bugs",
                "🧪 Tests","📝 Pseudocode","🔢 Algorithm","🔀 Approaches"
            ]

            selected_tab = st.radio(
                "Select Feature",
                tab_labels,
                index=st.session_state.active_tab,
                horizontal=True,
                label_visibility="collapsed"
            )

            # Update session state based on selection
            st.session_state.active_tab = tab_labels.index(selected_tab)

                        # Select tabs using index
            if selected_tab == "📖 Explain":
                aitab(st.container(), "bex", "📖 Explain Code",
                    "explanation", api.explain_code, code, final_lang)

            elif selected_tab == "🔄 Translate":
                st.markdown(f"### 🔄 {final_lang} → {target_lang}")
                if cd.get("translation"):
                    st.info("⚡ Cached!")
                    st.code(cd["translation"], language=target_lang.lower())
                elif st.button(f"Translate to {target_lang}", key="btr"):
                    with st.spinner("Translating..."):
                        r = api.translate_code(code, final_lang, target_lang)
                        st.code(r, language=target_lang.lower())
                        st.session_state.ai_results["translation"] = r

                        if target_lang.lower() == "python":
                            st.session_state.translated_python_code = r
                            st.success("✅ Translated to Python!")

            elif selected_tab == "📈 Complexity":
                aitab(st.container(), "bcx", "📈 Analyze Complexity",
                    "complexity", api.analyze_complexity, code, final_lang)

            elif selected_tab == "🐛 Bugs":
                aitab(st.container(), "bbg", "🐛 Scan for Bugs",
                    "bugs", api.detect_bugs, code, final_lang)

            elif selected_tab == "🧪 Tests":
                aitab(st.container(), "bts", "🧪 Generate Test Cases",
                    "test_cases", api.generate_test_cases, code, final_lang)

            elif selected_tab == "📝 Pseudocode":
                aitab(st.container(), "bps", "📝 Generate Pseudocode",
                    "pseudocode", api.generate_pseudocode, code, final_lang)

            elif selected_tab == "🔢 Algorithm":
                aitab(st.container(), "bal", "🔢 Identify Algorithm",
                    "algorithm", api.generate_algorithm, code, final_lang)

            elif selected_tab == "🔀 Approaches":
                aitab(st.container(), "bap", "🔀 Show All Approaches",
                    "approaches", api.generate_approaches, code, final_lang)


            if st.session_state.ai_results and not st.session_state.cached:
                uid = st.session_state.get("user_id")
                if history_mgr.save_to_history(code, final_lang, st.session_state.ai_results, uid):
                    refresh_history()

        # STEP 3
        st.divider()
        st.markdown("## 🎨 Step 3: Visual Analysis")
        vt1,vt2,vt3,vt4 = st.tabs(["🗺️ Flowchart","▶️ Step Executor","🌡️ Heatmap","🔬 Line Visualizer"])

        with vt1:
            st.markdown("### 🗺️ Flowchart (Zoom + Pan)")
            try:
                cb = generate_flowchart(code, final_lang)
                b64 = base64.b64encode(cb).decode()
                components.html(f"""<!DOCTYPE html><html><head><style>
body{{margin:0;background:#1e1e2e;overflow:hidden;}}
#c{{width:100%;height:500px;overflow:auto;cursor:grab;background:#1e1e2e;display:flex;align-items:flex-start;justify-content:center;}}
#c:active{{cursor:grabbing;}}#w{{transform-origin:top center;transition:transform 0.15s;padding:10px;}}
img{{max-width:none;display:block;border-radius:8px;}}
.ctrl{{position:fixed;bottom:10px;right:10px;display:flex;gap:6px;z-index:100;}}
.btn{{background:#313244;color:#cdd6f4;border:1px solid #45475a;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;}}
.btn:hover{{background:#cba6f7;color:#1e1e2e;}}
</style></head><body>
<div id="c"><div id="w"><img id="img" src="data:image/png;base64,{b64}"/></div></div>
<div class="ctrl">
<button class="btn" onclick="z(0.25)">＋</button>
<button class="btn" onclick="z(-0.25)">－</button>
<button class="btn" onclick="fit()">⊙ Fit</button>
<button class="btn" onclick="rst()">↺</button>
</div>
<script>
let s=1;const w=document.getElementById('w'),c=document.getElementById('c'),img=document.getElementById('img');
function z(d){{s=Math.min(Math.max(0.2,s+d),4);w.style.transform=`scale(${{s}})`;}}
function rst(){{s=1;w.style.transform='scale(1)';c.scrollTo(0,0);}}
function fit(){{const iw=img.naturalWidth,ih=img.naturalHeight,cw=c.clientWidth-20,ch=c.clientHeight-20;s=Math.min(cw/iw,ch/ih,1);w.style.transform=`scale(${{s}})`;}}
c.addEventListener('wheel',(e)=>{{e.preventDefault();z(e.deltaY<0?0.1:-0.1);}});
let d=false,sx,sy,sl,st2;
c.addEventListener('mousedown',(e)=>{{d=true;sx=e.pageX-c.offsetLeft;sy=e.pageY-c.offsetTop;sl=c.scrollLeft;st2=c.scrollTop;}});
c.addEventListener('mousemove',(e)=>{{if(!d)return;e.preventDefault();c.scrollLeft=sl-(e.pageX-c.offsetLeft-sx);c.scrollTop=st2-(e.pageY-c.offsetTop-sy);}});
c.addEventListener('mouseup',()=>d=false);c.addEventListener('mouseleave',()=>d=false);
img.onload=()=>fit();
</script></body></html>""", height=550, scrolling=False)
            except Exception as e:
                st.error(f"Flowchart error: {e}")

        with vt2:
            st.markdown("### ▶️ Step-by-Step Code Executor")
            st.caption("Watch variables change at each line — use ◀ ▶ buttons or arrow keys to navigate")
            if final_lang.lower() == "python":
                if st.button("▶️ Run Step-by-Step Execution", key="bstep"):
                    with st.spinner("Tracing Python execution..."):
                        python_code = st.session_state.get(
                            "translated_python_code",
                            code
                        )

                        steps = trace_python_execution(python_code)
                    if steps:
                        sh = render_step_visualizer(steps, code)
                        components.html(sh, height=560, scrolling=False)
                        st.caption(f"✅ {len(steps)} steps traced. Arrow keys also work!")
                    else:
                        st.warning("Could not trace. Ensure code is valid Python.")
                else:
                    components.html("""<html><body style="background:#1e1e2e;display:flex;align-items:center;justify-content:center;height:300px;margin:0;">
<div style="color:#6c7086;font-family:Arial;text-align:center;">
<div style="font-size:48px;margin-bottom:16px;">▶️</div>
<div style="font-size:15px;">Click "Run Step-by-Step Execution" above</div>
<div style="font-size:12px;margin-top:8px;color:#45475a;">Works with Python code only · Use ◀ ▶ to navigate steps</div>
</div></body></html>""", height=320)
            else:
                st.info(
                    f"⚠️ Step-by-step execution supports **Python** only. "
                    f"Detected: **{final_lang}**."
                )

                st.markdown("💡 Use the **Translate** tab to convert it to Python first!")

                if st.button("🔄 Go to Translate Tab"):
                    st.warning("Please open the **🔄 Translate** tab above to convert your code.")
                    st.session_state.active_tab = 1  # Index of the Translate tab
                    st.rerun()

        with vt3:
            st.markdown("### 🌡️ Readability Heatmap")
            ld,ov = generate_heatmap(code)
            sm = get_readability_summary(ld, ov)
            if sm:
                s1,s2,s3,s4,s5 = st.columns(5)
                with s1: st.markdown(f"<div class='metric-card'><h3>{sm['overall']}/100</h3><p>Score</p></div>", unsafe_allow_html=True)
                with s2: st.markdown(f"<div class='metric-card'><h3>{sm['grade']}</h3><p>Grade</p></div>", unsafe_allow_html=True)
                with s3: st.markdown(f"<div class='metric-card'><h3>{sm['excellent_lines']}</h3><p>Excellent</p></div>", unsafe_allow_html=True)
                with s4: st.markdown(f"<div class='metric-card'><h3>{sm['good_lines']}</h3><p>Good</p></div>", unsafe_allow_html=True)
                with s5: st.markdown(f"<div class='metric-card'><h3>{sm['poor_lines']}</h3><p>Poor</p></div>", unsafe_allow_html=True)
            components.html(render_heatmap_html(ld,ov), height=min(max(len(ld)*28+60,200),600), scrolling=True)

        with vt4:
            st.markdown("### 🔬 Line-by-Line Visualizer")
            an = generate_visualization(code, final_lang)
            components.html(render_visualization_html(an), height=min(max(len(an)*52+60,200),700), scrolling=True)

        # CHAT
        st.divider()
        st.markdown("## 🤖 AI Code Assistant")
        if not st.session_state.api_key:
            st.warning("Enter Groq API key to use AI chat!")
        else:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            ui = st.chat_input("Ask about your code...")
            if ui:
                st.session_state.chat_messages.append({"role":"user","content":ui})
                with st.chat_message("user"): st.markdown(ui)
                api = APIHandler(st.session_state.api_key)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."): r = api.chat_about_code(code, final_lang, st.session_state.chat_messages[:-1])
                    st.markdown(r)
                    st.session_state.chat_messages.append({"role":"assistant","content":r})
            if st.session_state.chat_messages:
                if st.button("🗑️ Clear Chat"): st.session_state.chat_messages=[]; st.rerun()

        st.divider()
        st.success("✅ Analysis Complete!")
        st.balloons()

    st.markdown("<div style='text-align:center;color:#6c7086;font-size:13px;padding:20px;'>🧠 NLP Code Interpreter | By Priyansh Gupta  </div>", unsafe_allow_html=True)

# ENTRY POINT
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
