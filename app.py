"""
app.py — NeuraCode: AI Code Interpreter v3.1 (FINAL)
Fixes: empty top box, mobile API key, caching, guest privacy, lazy visuals
"""

import streamlit as st

# MUST be the very first Streamlit call — no duplicate import, no st. before this
st.set_page_config(
    page_title="NeuraCode: AI Code Interpreter",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def get_secret(key, fallback=""):
    try:
        return st.secrets.get(key, fallback)
    except Exception:
        return fallback

SUPABASE_URL = get_secret("SUPABASE_URL", "")
SUPABASE_KEY = get_secret("SUPABASE_KEY", "")

st.markdown("""<style>
.stApp{background-color:#1e1e2e;color:#cdd6f4;}
/* THE FIX for empty grey box */
div[data-testid="stDecoration"]{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
header[data-testid="stHeader"]{height:0!important;min-height:0!important;}
.block-container{padding-top:1rem!important;}
.stTextArea textarea{background-color:#313244!important;color:#cdd6f4!important;
  font-family:'Courier New',monospace!important;font-size:14px!important;
  border:1px solid #45475a!important;border-radius:8px!important;caret-color:#fff!important;}
.stTextInput>div>div>input{background-color:#313244!important;color:#cdd6f4!important;
  border:1px solid #45475a!important;border-radius:6px!important;}
.stButton>button{background:linear-gradient(135deg,#cba6f7,#89b4fa);color:#1e1e2e;
  font-weight:bold;border:none;border-radius:8px;padding:0.5rem 1.5rem;font-size:15px;}
.metric-card{background:#313244;border-radius:10px;padding:15px;text-align:center;
  border-left:4px solid #cba6f7;margin:5px;}
.metric-card h3{color:#cba6f7;font-size:24px;margin:0;}
.metric-card p{color:#bac2de;font-size:13px;margin:0;}
.nlp-tag{display:inline-block;background:#45475a;color:#89dceb;
  padding:3px 10px;border-radius:20px;font-size:12px;margin:2px;}
.lang-badge{background:linear-gradient(135deg,#a6e3a1,#89dceb);color:#1e1e2e;
  padding:8px 20px;border-radius:20px;font-size:18px;font-weight:bold;}
.cache-badge{background:linear-gradient(135deg,#f9e2af,#fab387);color:#1e1e2e;
  padding:6px 16px;border-radius:20px;font-size:14px;font-weight:bold;}
.user-badge{background:linear-gradient(135deg,#cba6f7,#89b4fa);color:#1e1e2e;
  padding:4px 12px;border-radius:20px;font-size:12px;font-weight:bold;}
.guest-badge{background:#45475a;color:#bac2de;padding:4px 12px;border-radius:20px;font-size:12px;}
.api-banner{background:#2a2a3e;border:1px solid #cba6f7;border-radius:10px;
  padding:12px 16px;margin-bottom:10px;}
.auth-card{background:#313244;border-radius:12px;padding:28px;max-width:420px;
  margin:8px auto;border:1px solid #45475a;}
h1,h2,h3{color:#cdd6f4!important;}
@media(max-width:768px){.block-container{padding:0.5rem!important;}.metric-card h3{font-size:18px;}}
</style>""", unsafe_allow_html=True)

DEFAULTS = {
    "api_key":"","code":"","lang":"","analyzed":False,
    "confidence":None,"token_stats":None,"nlp_results":None,
    "cached":False,"cached_data":None,"chat_messages":[],"ai_results":{},
    "logged_in":False,"user_id":None,"username":"","user_email":"","access_token":None,
    "history_records":[],"active_history_id":None,
    "user_authenticated":False,"active_tab":0,"translated_python_code":None,
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

@st.cache_resource
def get_managers():
    return HistoryManager(SUPABASE_URL,SUPABASE_KEY), AuthManager(SUPABASE_URL,SUPABASE_KEY)

@st.cache_resource
def get_api_handler(api_key):
    return APIHandler(api_key)

@st.cache_resource
def get_nlp_proc():
    return NLPProcessor()

history_mgr,auth_mgr = get_managers()

@st.cache_data(ttl=3600,show_spinner=False)
def cached_detect(code): return detect_language(code)
@st.cache_data(ttl=3600,show_spinner=False)
def cached_tokens(code): return get_token_stats(code)
@st.cache_data(ttl=3600,show_spinner=False)
def cached_nlp(code): return get_nlp_proc().full_pipeline(code)
@st.cache_data(ttl=3600,show_spinner=False)
def cached_flowchart(code,lang): return generate_flowchart(code,lang)
@st.cache_data(ttl=3600,show_spinner=False)
def cached_heatmap(code): return generate_heatmap(code)
@st.cache_data(ttl=3600,show_spinner=False)
def cached_viz(code,lang): return generate_visualization(code,lang)

def refresh_history():
    if st.session_state.user_authenticated and st.session_state.user_id:
        st.session_state.history_records = history_mgr.get_user_history(st.session_state.user_id)
    else:
        st.session_state.history_records = []

def save_if_auth(code,lang,results):
    """Guest = incognito. Auth users only."""
    if st.session_state.get("user_authenticated") and st.session_state.get("user_id"):
        if history_mgr.save_to_history(code,lang,results,st.session_state.user_id):
            refresh_history()

def get_cached_result(code):
    if st.session_state.user_authenticated and st.session_state.user_id:
        return history_mgr.get_cached(code,st.session_state.user_id) or {}
    return {}

def load_history_item(rid):
    d = history_mgr.get_full_record(rid)
    if d:
        code=d.get("code","")
        st.session_state.update({
            "code":code,"lang":d.get("language",""),"cached_data":d,
            "cached":True,"analyzed":True,"active_history_id":rid,
            "chat_messages":[],"confidence":cached_detect(code)[1],
            "token_stats":cached_tokens(code),"nlp_results":cached_nlp(code),
        })

def show_auth_page():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown(
            "<h2 style='text-align:center;'>🧠 NeuraCode: AI Code Interpreter</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center;color:#6c7086;'>Sign in to save your personal history</p>",
            unsafe_allow_html=True
        )

        st.divider()
        t1, t2, t3 = st.tabs(["🔐 Login", "📝 Sign Up", "👤 Guest"])
        st.divider()
        t1,t2,t3 = st.tabs(["🔐 Login","📝 Sign Up","👤 Guest"])
        with t1:
            with st.form("lf"):
                em=st.text_input("Email",placeholder="you@example.com")
                pw=st.text_input("Password",type="password")
                if st.form_submit_button("Login",use_container_width=True):
                    if em and pw:
                        with st.spinner("Logging in..."):
                            r=auth_mgr.sign_in(em,pw)
                        if r["success"]:
                            st.session_state.update({"logged_in":True,"user_authenticated":True,
                                "user_id":r.get("user_id"),"user_email":r.get("email",em),
                                "username":r.get("username",em.split("@")[0]),
                                "access_token":r.get("access_token")})
                            refresh_history(); st.rerun()
                        else: st.error("❌ "+r["message"])
                    else: st.warning("Fill all fields")
        with t2:
            with st.form("sf"):
                un=st.text_input("Username",placeholder="Your name")
                em2=st.text_input("Email",placeholder="you@example.com")
                pw2=st.text_input("Password",type="password",placeholder="Min 6 chars")
                cp=st.text_input("Confirm Password",type="password")
                if st.form_submit_button("Create Account",use_container_width=True):
                    if not em2 or not pw2: st.warning("Fill all fields")
                    elif pw2!=cp: st.error("Passwords don't match!")
                    elif len(pw2)<6: st.error("Min 6 characters")
                    else:
                        with st.spinner("Creating..."): r=auth_mgr.sign_up(em2,pw2,un)
                        if r["success"]: st.success("✅ Account created! Please login.")
                        else: st.error("❌ "+r["message"])
        with t3:
            st.info("🔒 **Guest = Incognito**\nNo data stored anywhere.")
            if st.button("Continue as Guest",use_container_width=True):
                st.session_state.update({"logged_in":True,"user_authenticated":False,
                    "user_id":None,"username":"Guest","history_records":[]})
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

def show_main_app():
    is_auth=st.session_state.user_authenticated

    with st.sidebar:
        badge="user-badge" if is_auth else "guest-badge"
        icon="👤" if is_auth else "👻"
        st.markdown(f"<span class='{badge}'>{icon} {st.session_state.username}</span>",unsafe_allow_html=True)
        if st.session_state.user_email: st.caption(st.session_state.user_email)
        if st.button("🚪 Logout",use_container_width=True):
            for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
            st.rerun()
        st.divider()
        st.markdown("### 🔑 Groq API Key")
        st.caption("Desktop: here | Mobile: main screen ↓")
        ki=st.text_input("ks",type="password",placeholder="gsk_...",label_visibility="collapsed")
        if ki: st.session_state.api_key=ki
        if st.session_state.api_key: st.success("✅ Key active!")
        st.caption("[Get free key →](https://console.groq.com)")
        st.divider()
        if is_auth:
            st.markdown("### 🕐 History")
            c1,c2=st.columns(2)
            with c1:
                if st.button("🔄",use_container_width=True): refresh_history()
            with c2:
                if st.button("✏️ New",use_container_width=True):
                    for k in ["analyzed","cached","cached_data","active_history_id"]:
                        st.session_state[k]=DEFAULTS[k]
                    st.session_state.code=""; st.rerun()
            records=st.session_state.history_records
            if not records: st.caption("No history yet.")
            else:
                from datetime import datetime
                today=datetime.now().date()
                grps={"Today":[],"Earlier":[]}
                for rec in records[:30]:
                    try:
                        d=datetime.fromisoformat(str(rec.get("created_at",""))[:19]).date()
                        (grps["Today"] if d==today else grps["Earlier"]).append(rec)
                    except: grps["Earlier"].append(rec)
                for grp,items in grps.items():
                    if items:
                        st.caption(f"— {grp} —")
                        for rec in items:
                            rid=rec.get("id",""); lang=rec.get("language","?")
                            preview=rec.get("code","")[:26].replace('\n',' ').strip()
                            active=rid==st.session_state.active_history_id
                            icn="🔷" if active else "📄"
                            hc1,hc2=st.columns([5,1])
                            with hc1:
                                if st.button(f"{icn} {lang}: {preview}...",key=f"h_{rid}",use_container_width=True):
                                    load_history_item(rid); st.rerun()
                            with hc2:
                                if st.button("✕",key=f"d_{rid}"):
                                    history_mgr.delete_history(rid); refresh_history(); st.rerun()
        else:
            st.markdown("### 👻 Guest Mode")
            st.caption("🔒 Incognito — nothing saved")
            if st.button("🔐 Sign In",use_container_width=True):
                for k in DEFAULTS: st.session_state[k]=DEFAULTS[k]
                st.rerun()
        st.divider()
        for c in ["🔤 Tokenization","🚫 Stop Words","🌱 Stemming","📖 Lemmatization",
                  "📊 TF-IDF","🔍 Pattern Matching","📐 N-grams","🌍 Lang Detection","🏷️ POS Tagging"]:
            st.markdown(f"<span class='nlp-tag'>{c}</span>",unsafe_allow_html=True)

    st.markdown("# 🧠 NeuraCode: AI Code Interpreter")
    st.markdown("Detect · Explain · Translate · Visualize · Step-Trace · Optimize")

    # Mobile API Key — visible on main screen, essential for mobile
    if not st.session_state.api_key:
        st.markdown("<div class='api-banner'>📱 <b>Enter Groq API Key</b> — required for AI features (sidebar hidden on mobile)</div>",unsafe_allow_html=True)
        mk=st.text_input("mk",type="password",placeholder="gsk_... — free key at console.groq.com",label_visibility="collapsed")
        if mk: st.session_state.api_key=mk; st.rerun()

    st.divider()

    c1,c2=st.columns([3,1])
    with c1:
        code_input=st.text_area("ci",height=250,label_visibility="collapsed",
            placeholder="Paste Python, Java, C++, JavaScript... any code here")
    with c2:
        st.markdown("### ⚙️ Options")
        auto=st.checkbox("Auto-detect language",value=True)
        manual_lang=None
        if not auto:
            manual_lang=st.selectbox("ls",["Python","Java","C++","C","JavaScript","TypeScript","Go","Kotlin","Ruby","SQL"],label_visibility="collapsed")
        target_lang=st.selectbox("Translate To",["Java","Python","C++","JavaScript","Go","Kotlin","TypeScript","Ruby"])

    if st.button("🚀 Analyze Code",use_container_width=True):
        if not code_input.strip():
            st.error("⚠️ Paste some code first!")
        else:
            cached=get_cached_result(code_input)
            if cached:
                st.session_state.update({"cached":True,"cached_data":cached,
                    "lang":cached.get("language","Unknown"),"active_history_id":cached.get("id")})
            else:
                st.session_state.update({"cached":False,"cached_data":None,"active_history_id":None})
            det,conf=cached_detect(code_input)
            st.session_state.update({
                "lang":manual_lang or det,"confidence":conf,
                "token_stats":cached_tokens(code_input),"nlp_results":cached_nlp(code_input),
                "code":code_input,"analyzed":True,"chat_messages":[],"ai_results":{},
            })

    if st.session_state.analyzed:
        final_lang=st.session_state.lang; code=st.session_state.code

        if st.session_state.cached:
            st.markdown("<div class='cache-badge'>⚡ From Cache — No API used!</div>",unsafe_allow_html=True)
            st.markdown("")
        elif not is_auth:
            st.info("👻 Guest mode — results not saved. Sign in to keep history.")

        st.divider()
        st.markdown("## 🔍 Step 1: NLP Analysis Pipeline")
        st.markdown(f"<div style='text-align:center;padding:8px;'><span class='lang-badge'>📦 {final_lang}</span></div>",unsafe_allow_html=True)

        if st.session_state.confidence:
            top5=dict(list(st.session_state.confidence.items())[:5])
            cols=st.columns(len(top5))
            for i,(lang,score) in enumerate(top5.items()):
                with cols[i]: st.markdown(f"<div class='metric-card'><h3>{score}%</h3><p>{lang}</p></div>",unsafe_allow_html=True)

        if st.session_state.token_stats:
            ts=st.session_state.token_stats
            c1,c2,c3,c4=st.columns(4)
            for col,val,lbl in [(c1,ts['total_tokens'],"Tokens"),(c2,ts['unique_tokens'],"Unique"),
                                (c3,ts['total_lines'],"Lines"),(c4,ts['avg_tokens_per_line'],"Per Line")]:
                with col: st.markdown(f"<div class='metric-card'><h3>{val}</h3><p>{lbl}</p></div>",unsafe_allow_html=True)

        if st.session_state.nlp_results:
            nr=st.session_state.nlp_results
            with st.expander("🔬 Full NLP Pipeline (Tokenization → TF-IDF)"):
                p1,p2=st.columns(2)
                with p1:
                    st.markdown("**1️⃣ Raw Tokens**"); st.code(' | '.join(nr.get('raw_tokens',[])[:15]))
                    st.markdown("**2️⃣ Stop Words Removed**"); st.code(' | '.join(nr.get('after_stopword_removal',[])[:15]))
                with p2:
                    st.markdown("**3️⃣ Stemmed**"); st.code(' | '.join(nr.get('stemmed',[])[:15]))
                    st.markdown("**4️⃣ Lemmatized**"); st.code(' | '.join(nr.get('lemmatized',[])[:15]))
                if nr.get('tfidf_keywords'):
                    st.markdown("**5️⃣ TF-IDF**")
                    tc=st.columns(5)
                    for i,(w,s) in enumerate(list(nr['tfidf_keywords'].items())[:10]):
                        with tc[i%5]: st.markdown(f"<div class='metric-card'><h3>{s}</h3><p>{w}</p></div>",unsafe_allow_html=True)
                st.markdown(f"**6️⃣ Comment Language:** `{nr.get('comment_language','N/A')}`")

        st.divider()
        st.markdown("## ⚡ Step 2: AI-Powered Features")
        if not st.session_state.api_key:
            st.warning("⚠️ Enter your Groq API Key above!")
        else:
            api=get_api_handler(st.session_state.api_key)
            cd=st.session_state.cached_data or {}
            TABS=["📖 Explain","🔄 Translate","📈 Complexity","🐛 Bugs","🧪 Tests","📝 Pseudocode","🔢 Algorithm","🔀 Approaches"]
            sel=st.radio("fs",TABS,index=st.session_state.active_tab,horizontal=True,label_visibility="collapsed")
            st.session_state.active_tab=TABS.index(sel)

            def ai_block(key,label,ckey,fn,*args):
                st.markdown(f"### {label}")
                if cd.get(ckey): st.info("⚡ Cached!"); st.markdown(cd[ckey])
                elif st.button(label,key=key):
                    with st.spinner("Calling Groq API..."): result=fn(*args)
                    st.markdown(result); st.session_state.ai_results[ckey]=result

            with st.container():
                if sel=="📖 Explain": ai_block("bex","📖 Explain Code","explanation",api.explain_code,code,final_lang)
                elif sel=="🔄 Translate":
                    st.markdown(f"### 🔄 {final_lang} → {target_lang}")
                    if cd.get("translation"): st.info("⚡ Cached!"); st.code(cd["translation"],language=target_lang.lower())
                    elif st.button(f"Translate to {target_lang}",key="btr"):
                        with st.spinner("Translating..."): r=api.translate_code(code,final_lang,target_lang)
                        st.code(r,language=target_lang.lower()); st.session_state.ai_results["translation"]=r
                        if target_lang.lower()=="python": st.session_state.translated_python_code=r
                elif sel=="📈 Complexity": ai_block("bcx","📈 Analyze Complexity","complexity",api.analyze_complexity,code,final_lang)
                elif sel=="🐛 Bugs": ai_block("bbg","🐛 Scan for Bugs","bugs",api.detect_bugs,code,final_lang)
                elif sel=="🧪 Tests": ai_block("bts","🧪 Generate Tests","test_cases",api.generate_test_cases,code,final_lang)
                elif sel=="📝 Pseudocode": ai_block("bps","📝 Generate Pseudocode","pseudocode",api.generate_pseudocode,code,final_lang)
                elif sel=="🔢 Algorithm": ai_block("bal","🔢 Identify Algorithm","algorithm",api.generate_algorithm,code,final_lang)
                elif sel=="🔀 Approaches": ai_block("bap","🔀 All Approaches","approaches",api.generate_approaches,code,final_lang)

            if st.session_state.ai_results and not st.session_state.cached:
                save_if_auth(code,final_lang,st.session_state.ai_results)

        st.divider()
        st.markdown("## 🎨 Step 3: Visual Analysis")
        vt1,vt2,vt3,vt4=st.tabs(["🗺️ Flowchart","▶️ Step Executor","🌡️ Heatmap","🔬 Line Visualizer"])

        with vt1:
            st.markdown("### 🗺️ Flowchart (Zoom + Pan)")
            st.caption("Graphviz — local, no API needed")
            if st.button("🗺️ Generate Flowchart",key="btn_fc"):
                with st.spinner("Generating..."): cb=cached_flowchart(code,final_lang)
                b64=base64.b64encode(cb).decode()
                components.html(f"""<!DOCTYPE html><html><head><style>
body{{margin:0;background:#1e1e2e;overflow:hidden;}}
#c{{width:100%;height:480px;overflow:auto;cursor:grab;background:#1e1e2e;display:flex;align-items:flex-start;justify-content:center;}}
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
let dd=false,sx,sy,sl,st2;
c.addEventListener('mousedown',(e)=>{{dd=true;sx=e.pageX-c.offsetLeft;sy=e.pageY-c.offsetTop;sl=c.scrollLeft;st2=c.scrollTop;}});
c.addEventListener('mousemove',(e)=>{{if(!dd)return;e.preventDefault();c.scrollLeft=sl-(e.pageX-c.offsetLeft-sx);c.scrollTop=st2-(e.pageY-c.offsetTop-sy);}});
c.addEventListener('mouseup',()=>dd=false);c.addEventListener('mouseleave',()=>dd=false);
img.onload=()=>fit();
</script></body></html>""",height=530,scrolling=False)
            else:
                st.caption("Click to generate — Graphviz, no API")

        with vt2:
            st.markdown("### ▶️ Step-by-Step Executor")
            st.caption("Local Python tracer — like pythontutor.com")
            if final_lang.lower()=="python":
                if st.button("▶️ Run Step-by-Step",key="bstep"):
                    py_code=st.session_state.get("translated_python_code") or code
                    with st.spinner("Tracing locally..."): steps=trace_python_execution(py_code)
                    if steps:
                        components.html(render_step_visualizer(steps,py_code),height=560,scrolling=False)
                        st.caption(f"✅ {len(steps)} steps · ◀ ▶ or arrow keys")
                    else: st.warning("Could not trace — ensure valid Python")
                else:
                    components.html("""<html><body style="background:#1e1e2e;display:flex;align-items:center;justify-content:center;height:260px;margin:0;">
<div style="color:#6c7086;font-family:Arial;text-align:center;"><div style="font-size:44px;margin-bottom:10px;">▶️</div>
<div style="font-size:14px;">Click Run Step-by-Step</div>
<div style="font-size:11px;margin-top:6px;color:#45475a;">Python only · No API</div>
</div></body></html>""",height=280)
            else:
                st.info(f"⚠️ Python only (detected: **{final_lang}**)")
                st.markdown("💡 Use **🔄 Translate → Python** first!")

        with vt3:
            st.markdown("### 🌡️ Readability Heatmap")
            st.caption("Local scoring — no API")
            if st.button("🌡️ Generate Heatmap",key="btn_hm"):
                with st.spinner("Scoring..."): ld,ov=cached_heatmap(code)
                sm=get_readability_summary(ld,ov)
                if sm:
                    s1,s2,s3,s4,s5=st.columns(5)
                    for col,val,lbl in [(s1,f"{sm['overall']}/100","Score"),(s2,sm['grade'],"Grade"),
                                       (s3,sm['excellent_lines'],"Excellent"),(s4,sm['good_lines'],"Good"),(s5,sm['poor_lines'],"Poor")]:
                        with col: st.markdown(f"<div class='metric-card'><h3>{val}</h3><p>{lbl}</p></div>",unsafe_allow_html=True)
                components.html(render_heatmap_html(ld,ov),height=min(max(len(ld)*28+60,200),600),scrolling=True)
            else: st.caption("Click to score readability line by line")

        with vt4:
            st.markdown("### 🔬 Line-by-Line Visualizer")
            st.caption("Local NLP POS tagging — no API")
            if st.button("🔬 Visualize Lines",key="btn_lv"):
                with st.spinner("Analyzing..."): an=cached_viz(code,final_lang)
                components.html(render_visualization_html(an),height=min(max(len(an)*52+60,200),700),scrolling=True)
            else: st.caption("Click to classify each line by type")

        st.divider()
        st.markdown("## 🤖 AI Code Assistant")
        st.caption("Groq API · Only called when you send a message")
        if not st.session_state.api_key:
            st.warning("Enter Groq API key to use chat!")
        else:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
            ui=st.chat_input("Ask about your code...")
            if ui:
                st.session_state.chat_messages.append({"role":"user","content":ui})
                with st.chat_message("user"): st.markdown(ui)
                api=get_api_handler(st.session_state.api_key)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."): r=api.chat_about_code(code,final_lang,st.session_state.chat_messages[:-1])
                    st.markdown(r); st.session_state.chat_messages.append({"role":"assistant","content":r})
            if st.session_state.chat_messages:
                if st.button("🗑️ Clear Chat"): st.session_state.chat_messages=[]; st.rerun()

        st.divider(); st.success("✅ Analysis Complete!")
        if not is_auth: st.info("💡 Sign in to save this analysis!")

    st.markdown("<div style='text-align:center;color:#6c7086;font-size:12px;padding:14px;'>🧠 NeuraCode: AI Code Interpreter &nbsp;|&nbsp; By Priyansh Gupta &nbsp;|&nbsp;<a href='https://github.com/Priyanshgupta108/code-detect-explain-translate-nlp' style='color:#cba6f7;'>GitHub</a></div>",unsafe_allow_html=True)

if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
