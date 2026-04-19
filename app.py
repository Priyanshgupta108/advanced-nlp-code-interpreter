"""
app.py — NeuraCode: AI Code Interpreter v3.2
Mobile-responsive, performance-optimized, guest-incognito
"""

import streamlit as st

# ── MUST BE ABSOLUTE FIRST CALL — no imports before this ──────
st.set_page_config(
    page_title="NeuraCode: AI Code Interpreter",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ALL IMPORTS AFTER set_page_config ─────────────────────────
import base64
import streamlit.components.v1 as components
from detector import detect_language, get_token_stats
from nlp_processor import NLPProcessor
from api_handler import APIHandler
from visualizer import generate_flowchart
from heatmap_generator import generate_heatmap, render_heatmap_html, get_readability_summary
from code_visualizer import generate_visualization, render_visualization_html
from history_manager import HistoryManager
from auth_manager import AuthManager
from step_visualizer import trace_python_execution, render_step_visualizer

# ── SECRETS ────────────────────────────────────────────────────
def get_secret(key, fallback=""):
    try:
        return st.secrets.get(key, fallback)
    except Exception:
        return fallback

SUPABASE_URL = get_secret("SUPABASE_URL", "https://xysdsmdgiklcysrmtibd.supabase.co")
SUPABASE_KEY = get_secret("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5c2RzbWRnaWtsY3lzcm10aWJkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUyMDM3NTUsImV4cCI6MjA5MDc3OTc1NX0.1c-TAcQZPLnKRoODun_E0auSIUjOBPRDEi5OptDzuE8")

# ── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══ BASE ═══════════════════════════════════════════════════ */
.stApp { background-color: #1e1e2e; color: #cdd6f4; }

/* ── FIX: Remove empty grey box at top (stDecoration) ───────── */
div[data-testid="stDecoration"]  { display: none !important; }
div[data-testid="stToolbar"]     { display: none !important; }
header[data-testid="stHeader"]   { height: 0 !important; min-height: 0 !important; }
.block-container                 { padding-top: 1rem !important; }

/* ═══ INPUTS ═════════════════════════════════════════════════ */
.stTextArea textarea {
    background-color: #313244 !important; color: #cdd6f4 !important;
    font-family: 'Courier New', monospace !important; font-size: 13px !important;
    border: 1px solid #45475a !important; border-radius: 8px !important;
    caret-color: #fff !important;
}
.stTextInput > div > div > input {
    background-color: #313244 !important; color: #cdd6f4 !important;
    border: 1px solid #45475a !important; border-radius: 6px !important;
    font-size: 14px !important;
}
select, .stSelectbox > div > div {
    background-color: #313244 !important; color: #cdd6f4 !important;
    border: 1px solid #45475a !important;
}

/* ═══ BUTTONS ════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #cba6f7, #89b4fa) !important;
    color: #1e1e2e !important; font-weight: bold !important;
    border: none !important; border-radius: 8px !important;
    font-size: 14px !important; width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ═══ CARDS ══════════════════════════════════════════════════ */
.metric-card {
    background: #313244; border-radius: 10px; padding: 12px;
    text-align: center; border-left: 4px solid #cba6f7; margin: 4px;
}
.metric-card h3 { color: #cba6f7; font-size: 20px; margin: 0; }
.metric-card p  { color: #bac2de; font-size: 12px; margin: 0; }

/* ═══ BADGES & TAGS ══════════════════════════════════════════ */
.nlp-tag {
    display: inline-block; background: #45475a; color: #89dceb;
    padding: 3px 10px; border-radius: 20px; font-size: 12px; margin: 2px;
}
.lang-badge {
    background: linear-gradient(135deg, #a6e3a1, #89dceb); color: #1e1e2e;
    padding: 8px 20px; border-radius: 20px; font-size: 17px; font-weight: bold;
    display: inline-block;
}
.cache-badge {
    background: linear-gradient(135deg, #f9e2af, #fab387); color: #1e1e2e;
    padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: bold;
    display: inline-block;
}
.user-badge {
    background: linear-gradient(135deg, #cba6f7, #89b4fa); color: #1e1e2e;
    padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;
}
.guest-badge {
    background: #45475a; color: #bac2de;
    padding: 4px 12px; border-radius: 20px; font-size: 12px;
}

/* ═══ MOBILE API KEY BANNER ══════════════════════════════════ */
.api-banner {
    background: linear-gradient(135deg, #2a2a3e, #1e1e2e);
    border: 1px solid #cba6f7; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 12px;
    font-size: 14px; color: #cdd6f4;
}

/* ═══ AUTH CARD ══════════════════════════════════════════════ */
.auth-card {
    background: #313244; border-radius: 14px; padding: 24px;
    max-width: 420px; margin: 8px auto; border: 1px solid #45475a;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* ═══ TABS ════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; flex-wrap: wrap;
    background: #313244; border-radius: 8px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #bac2de !important; border-radius: 6px !important;
    font-size: 12px !important; padding: 6px 10px !important;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #cba6f7, #89b4fa) !important;
    color: #1e1e2e !important;
}

/* ═══ CHAT ════════════════════════════════════════════════════ */
.stChatMessage { background: #313244 !important; border-radius: 10px !important; }

/* ═══ MOBILE: screen < 768px ════════════════════════════════ */
@media (max-width: 768px) {
    .block-container    { padding: 0.4rem 0.4rem !important; }
    h1                  { font-size: 1.4rem !important; }
    h2                  { font-size: 1.1rem !important; }
    h3                  { font-size: 1rem !important; }
    .metric-card h3     { font-size: 16px; }
    .metric-card p      { font-size: 11px; }
    .metric-card        { padding: 8px; margin: 2px; }
    .stTextArea textarea { font-size: 12px !important; }
    .lang-badge         { font-size: 14px; padding: 6px 14px; }

    /* Stack columns on mobile */
    [data-testid="column"] { min-width: 100% !important; }

    /* Scrollable horizontal tabs on mobile */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto; flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }

    /* Full-width buttons on mobile */
    .stButton > button { font-size: 13px !important; padding: 0.4rem 0.8rem !important; }
}

/* ═══ GENERAL ════════════════════════════════════════════════ */
h1, h2, h3 { color: #cdd6f4 !important; }

/* Smooth scrollable containers */
.scroll-wrap {
    overflow-x: auto; overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 8px;
}

/* ── RADIO TABS: visible colored pills ───────── */
div[role="radiogroup"] {
    background: #313244; padding: 6px 8px;
    border-radius: 10px; gap: 4px; flex-wrap: wrap;
}
div[role="radiogroup"] label {
    background: #45475a !important; color: #cdd6f4 !important;
    padding: 5px 12px !important; border-radius: 8px !important;
    font-size: 13px !important; cursor: pointer;
    border: 1px solid #585b70 !important;
    transition: all 0.15s; white-space: nowrap;
}
div[role="radiogroup"] label:hover {
    background: #585b70 !important; color: #fff !important;
}
input[type="radio"] { display: none !important; }
div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg,#cba6f7,#89b4fa) !important;
    color: #1e1e2e !important; font-weight: bold !important;
    border-color: transparent !important;
}

/* ── VS CODE EDITOR ───────────────────────────── */
.vscode-titlebar {
    background:#2d2d2d; padding:7px 14px;
    display:flex; align-items:center; gap:7px;
    border-bottom:1px solid #3c3c3c;
    border-radius:8px 8px 0 0;
    font-family:'Segoe UI',Arial,sans-serif;
    font-size:12px; color:#969696;
}
.dot{width:12px;height:12px;border-radius:50%;display:inline-block;}
.dot-r{background:#ff5f56;} .dot-y{background:#ffbd2e;} .dot-g{background:#27c93f;}
.vscode-fname{color:#cccccc;margin-left:6px;font-size:12px;}
.vscode-lang{margin-left:auto;color:#569cd6;font-size:11px;}
.vscode-statusbar {
    background:#007acc; padding:3px 14px;
    font-family:'Segoe UI',Arial,sans-serif;
    font-size:11px; color:#fff;
    display:flex; align-items:center; gap:18px;
    border-radius:0 0 8px 8px;
}
.vscode-wrap { box-shadow:0 4px 20px rgba(0,0,0,0.5); border-radius:8px; }
.vscode-wrap .stTextArea textarea {
    background-color:#1e1e1e !important; color:#d4d4d4 !important;
    font-family:'Cascadia Code','Consolas','Courier New',monospace !important;
    font-size:14px !important; line-height:1.65 !important;
    border:1px solid #3c3c3c !important;
    border-top:none !important; border-bottom:none !important;
    border-radius:0 !important; padding:12px 16px !important;
    caret-color:#aeafad !important;
}
.vscode-wrap .stTextArea textarea::placeholder{
    color:#5a5a5a !important; font-style:italic;
}
.vscode-wrap .stTextArea{margin-bottom:0 !important;}
</style>""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────
DEFAULTS = {
    "api_key": "", "code": "", "lang": "", "analyzed": False,
    "confidence": None, "token_stats": None, "nlp_results": None,
    "cached": False, "cached_data": None,
    "chat_messages": [], "ai_results": {},
    "logged_in": False, "user_id": None,
    "username": "", "user_email": "", "access_token": None,
    "history_records": [], "active_history_id": None,
    "user_authenticated": False,
    "active_tab": 0,
    "translated_python_code": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CACHED RESOURCE INIT ──────────────────────────────────────
@st.cache_resource
def get_managers():
    return HistoryManager(SUPABASE_URL, SUPABASE_KEY), AuthManager(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def get_api_handler(api_key: str):
    """Cached per API key — avoids re-init on every rerun"""
    return APIHandler(api_key)

@st.cache_resource
def get_nlp_proc():
    return NLPProcessor()

history_mgr, auth_mgr = get_managers()

# ── CACHED DATA FUNCTIONS (local — no API) ───────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def cached_detect(code: str):
    return detect_language(code)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_tokens(code: str):
    return get_token_stats(code)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_nlp(code: str):
    return get_nlp_proc().full_pipeline(code)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_flowchart(code: str, lang: str):
    return generate_flowchart(code, lang)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_heatmap(code: str):
    return generate_heatmap(code)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_viz(code: str, lang: str):
    return generate_visualization(code, lang)

# ── HELPER FUNCTIONS ──────────────────────────────────────────
def refresh_history():
    if st.session_state.user_authenticated and st.session_state.user_id:
        st.session_state.history_records = history_mgr.get_user_history(
            st.session_state.user_id)
    else:
        st.session_state.history_records = []

def save_if_auth(code, lang, results):
    """Incognito for guests — only saves for authenticated users"""
    if st.session_state.get("user_authenticated") and st.session_state.get("user_id"):
        if history_mgr.save_to_history(code, lang, results, st.session_state.user_id):
            refresh_history()

def get_cached_result(code):
    if st.session_state.user_authenticated and st.session_state.user_id:
        return history_mgr.get_cached(code, st.session_state.user_id) or {}
    return {}

def load_history_item(rid):
    d = history_mgr.get_full_record(rid)
    if d:
        code = d.get("code", "")
        st.session_state.update({
            "code": code, "lang": d.get("language", ""),
            "cached_data": d, "cached": True, "analyzed": True,
            "active_history_id": rid, "chat_messages": [],
            "confidence": cached_detect(code)[1],
            "token_stats": cached_tokens(code),
            "nlp_results": cached_nlp(code),
        })

def metric_card(val, label):
    return f"<div class='metric-card'><h3>{val}</h3><p>{label}</p></div>"


# ══════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════
def show_auth_page():
    st.markdown("<div style='padding-top:2.5rem;'></div>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;'>🧠 NeuraCode</h2>",
                   unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align:center;color:#6c7086;'>AI Code Interpreter</p>",
            unsafe_allow_html=True)
        st.divider()

        t1, t2, t3 = st.tabs(["🔐 Login", "📝 Sign Up", "👤 Guest"])

        with t1:
            with st.form("lf"):
                em = st.text_input("Email", placeholder="you@example.com")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if em and pw:
                        with st.spinner("Logging in..."):
                            r = auth_mgr.sign_in(em, pw)
                        if r["success"]:
                            st.session_state.update({
                                "logged_in": True,
                                "user_authenticated": True,
                                "user_id": r.get("user_id"),
                                "user_email": r.get("email", em),
                                "username": r.get("username", em.split("@")[0]),
                                "access_token": r.get("access_token"),
                            })
                            refresh_history()
                            st.rerun()
                        else:
                            st.error("❌ " + r["message"])
                    else:
                        st.warning("Fill all fields")

        with t2:
            with st.form("sf"):
                un = st.text_input("Username", placeholder="Your name")
                em2 = st.text_input("Email", placeholder="you@example.com")
                pw2 = st.text_input("Password", type="password",
                                   placeholder="Min 6 chars")
                cp = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account",
                                         use_container_width=True):
                    if not em2 or not pw2:
                        st.warning("Fill all fields")
                    elif pw2 != cp:
                        st.error("Passwords don't match!")
                    elif len(pw2) < 6:
                        st.error("Min 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            r = auth_mgr.sign_up(em2, pw2, un)
                        if r["success"]:
                            st.success("✅ Account created! Please login.")
                        else:
                            st.error("❌ " + r["message"])

        with t3:
            st.info("🔒 **Guest = Incognito mode**\nNo data stored anywhere.")
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.update({
                    "logged_in": True,
                    "user_authenticated": False,
                    "user_id": None,
                    "username": "Guest",
                    "history_records": [],
                })
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
def show_main_app():
    is_auth = st.session_state.user_authenticated

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        badge = "user-badge" if is_auth else "guest-badge"
        icon = "👤" if is_auth else "👻"
        st.markdown(
            f"<span class='{badge}'>{icon} {st.session_state.username}</span>",
            unsafe_allow_html=True)
        if st.session_state.user_email:
            st.caption(st.session_state.user_email)

        if st.button("🚪 Logout", use_container_width=True):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()
        st.divider()

        # API Key — sidebar (desktop)
        st.markdown("### 🔑 Groq API Key")
        st.caption("Desktop: enter here · Mobile: see main screen ↓")
        ki = st.text_input("key_sb", type="password", placeholder="gsk_...",
                           label_visibility="collapsed")
        if ki:
            st.session_state.api_key = ki
        if st.session_state.api_key:
            st.success("✅ Key active!")
        st.caption("[Get free key →](https://console.groq.com)")
        st.divider()

        # History — authenticated users only
        if is_auth:
            st.markdown("### 🕐 History")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔄 Refresh", use_container_width=True):
                    refresh_history()
            with c2:
                if st.button("✏️ New", use_container_width=True):
                    for k in ["analyzed", "cached", "cached_data", "active_history_id"]:
                        st.session_state[k] = DEFAULTS[k]
                    st.session_state.code = ""
                    st.rerun()

            records = st.session_state.history_records
            if not records:
                st.caption("No history yet.")
            else:
                from datetime import datetime
                today = datetime.now().date()
                grps = {"Today": [], "Earlier": []}
                for rec in records[:30]:
                    try:
                        d = datetime.fromisoformat(
                            str(rec.get("created_at", ""))[:19]).date()
                        (grps["Today"] if d == today else grps["Earlier"]).append(rec)
                    except Exception:
                        grps["Earlier"].append(rec)

                for grp, items in grps.items():
                    if items:
                        st.caption(f"— {grp} —")
                        for rec in items:
                            rid = rec.get("id", "")
                            lang = rec.get("language", "?")
                            preview = rec.get("code", "")[:24].replace(
                                '\n', ' ').strip()
                            active = rid == st.session_state.active_history_id
                            icn = "🔷" if active else "📄"
                            hc1, hc2 = st.columns([5, 1])
                            with hc1:
                                if st.button(f"{icn} {lang}: {preview}...",
                                             key=f"h_{rid}",
                                             use_container_width=True):
                                    load_history_item(rid)
                                    st.rerun()
                            with hc2:
                                if st.button("✕", key=f"d_{rid}"):
                                    history_mgr.delete_history(rid)
                                    refresh_history()