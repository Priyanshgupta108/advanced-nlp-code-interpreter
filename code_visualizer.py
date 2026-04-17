"""
code_visualizer.py — Line-by-Line Code Visualizer (Mobile Optimized)
NLP BASED CODE INTERPRETER v3.2
"""

import re

TOKEN_TYPES = {
    "keyword":   {"color": "#cba6f7", "bg": "rgba(203,166,247,0.15)"},
    "function":  {"color": "#89dceb", "bg": "rgba(137,220,235,0.15)"},
    "variable":  {"color": "#a6e3a1", "bg": "rgba(166,227,161,0.15)"},
    "string":    {"color": "#f9e2af", "bg": "rgba(249,226,175,0.15)"},
    "number":    {"color": "#fab387", "bg": "rgba(250,179,135,0.15)"},
    "operator":  {"color": "#f38ba8", "bg": "rgba(243,139,168,0.15)"},
    "comment":   {"color": "#6c7086", "bg": "rgba(108,112,134,0.15)"},
    "class":     {"color": "#74c7ec", "bg": "rgba(116,199,236,0.15)"},
    "import":    {"color": "#b4befe", "bg": "rgba(180,190,254,0.15)"},
    "return":    {"color": "#eba0ac", "bg": "rgba(235,160,172,0.15)"},
    "condition": {"color": "#e8d44d", "bg": "rgba(232,212,77,0.15)"},
    "loop":      {"color": "#94e2d5", "bg": "rgba(148,226,213,0.15)"},
    "other":     {"color": "#cdd6f4", "bg": "rgba(205,214,244,0.10)"},
}

KEYWORDS = {
    "python": ["def","class","if","elif","else","for","while","return",
               "import","from","try","except","with","as","pass","break",
               "continue","lambda","yield","None","True","False","and",
               "or","not","in","is","global","nonlocal","raise","del"],
    "java":   ["public","private","protected","class","interface","extends",
               "implements","static","final","void","return","if","else",
               "for","while","do","switch","case","break","continue","new",
               "this","super","try","catch","finally","throw","throws",
               "import","package","true","false","null"],
    "javascript": ["var","let","const","function","return","if","else","for",
                   "while","do","switch","case","break","continue","class",
                   "new","this","import","export","default","try","catch",
                   "finally","throw","async","await","true","false","null"],
    "cpp": ["int","float","double","char","bool","void","string","auto",
            "class","struct","namespace","using","return","if","else","for",
            "while","do","switch","case","break","continue","new","delete",
            "this","public","private","protected","include","true","false","nullptr"],
}


def classify_token(token: str, language: str = "python") -> str:
    lang_kw = KEYWORDS.get(language.lower(), KEYWORDS["python"])
    if token.startswith("#") or token.startswith("//"): return "comment"
    if (token.startswith('"') and token.endswith('"')) or \
       (token.startswith("'") and token.endswith("'")): return "string"
    if re.match(r'^-?\d+\.?\d*$', token): return "number"
    if token in ["import", "from", "#include"]: return "import"
    if token in ["return", "yield"]: return "return"
    if token in ["if", "elif", "else", "switch", "case"]: return "condition"
    if token in ["for", "while", "do", "foreach"]: return "loop"
    if token == "class": return "class"
    if token in lang_kw: return "keyword"
    if token in ["+","-","*","/","=","==","!=","<",">","<=",">=",
                 "&&","||","!","++","--","+=","-=","*=","/="]:
        return "operator"
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token): return "function"
    return "other"


def analyze_line(line: str, line_no: int, language: str = "python") -> dict:
    stripped = line.strip()
    if not stripped:
        return {"line_no": line_no, "type": "empty", "label": "Empty",
                "color": "#45475a", "bg": "transparent",
                "tokens": [], "raw": line, "description": ""}

    if stripped.startswith(("#", "//", "/*")):
        lt, label, desc = "comment", "💬 Comment", "Developer note"
    elif re.match(r'^\s*(import|from|#include)\s+', stripped, re.I):
        lt, label, desc = "import", "📦 Import", "Loading external library"
    elif re.match(r'^\s*(def|function|func|void|public|private)\s+\w+\s*\(', stripped, re.I):
        lt = "function"; label = "⚙️ Function"
        fn = re.search(r'(?:def|function|func)\s+(\w+)', stripped, re.I)
        desc = f"Defines '{fn.group(1)}'" if fn else "Function definition"
    elif re.match(r'^\s*class\s+\w+', stripped, re.I):
        lt = "class"; label = "🏛️ Class"
        cn = re.search(r'class\s+(\w+)', stripped, re.I)
        desc = f"Defines class '{cn.group(1)}'" if cn else "Class definition"
    elif re.match(r'^\s*(if|elif|else\s*:?|switch)\b', stripped, re.I):
        lt, label, desc = "condition", "🔀 Condition", "Decision branch"
    elif re.match(r'^\s*(for|while|do)\b', stripped, re.I):
        lt, label, desc = "loop", "🔄 Loop", "Repeating block"
    elif re.match(r'^\s*return\b', stripped, re.I):
        lt, label = "return", "↩️ Return"
        val = re.sub(r'^\s*return\s*', '', stripped).strip()
        desc = f"Returns: {val[:25]}" + ("..." if len(val) > 25 else "")
    elif re.match(r'^\s*(print|console\.log|System\.out|cout)\b', stripped, re.I):
        lt, label, desc = "other", "📤 Output", "Prints a value"
    elif ('=' in stripped and not stripped.startswith('==') and
          not re.match(r'^\s*(if|while|return)', stripped)):
        lt, label = "variable", "📝 Assignment"
        parts = stripped.split('=', 1)
        var = parts[0].strip().split()[-1] if parts else "?"
        desc = f"Assigns '{var}'"
    else:
        lt, label, desc = "other", "▶️ Expression", "Code statement"

    raw_tokens = re.findall(
        r'\"[^\"]*\"|\'[^\']*\'|[a-zA-Z_]\w*|\d+\.?\d*|[+\-*/=<>!&|]+',
        stripped)
    tokens = [
        {"text": tok,
         "type": classify_token(tok, language),
         "color": TOKEN_TYPES.get(classify_token(tok, language),
                                  TOKEN_TYPES["other"])["color"]}
        for tok in raw_tokens[:8]
    ]

    return {
        "line_no": line_no, "type": lt, "label": label,
        "color": TOKEN_TYPES.get(lt, TOKEN_TYPES["other"])["color"],
        "bg":    TOKEN_TYPES.get(lt, TOKEN_TYPES["other"])["bg"],
        "tokens": tokens, "raw": line, "description": desc,
        "indent": len(line) - len(line.lstrip()),
    }


def generate_visualization(code: str, language: str = "python") -> list:
    return [analyze_line(line, i, language)
            for i, line in enumerate(code.split('\n'), 1)]


def render_visualization_html(analyzed_lines: list) -> str:
    """
    Returns self-contained HTML optimized for both desktop and mobile.
    Uses scrolling=True in components.html for mobile overflow.
    """
    rows = ""
    for ld in analyzed_lines:
        if ld["type"] == "empty":
            rows += '<div style="height:5px;"></div>'
            continue

        indent_px = min(ld.get("indent", 0) * 2, 32)  # cap indent on mobile
        pills = "".join(
            f'<span style="background:rgba(255,255,255,0.08);'
            f'color:{t["color"]};padding:1px 5px;border-radius:8px;'
            f'font-size:10px;margin:1px;display:inline-block;'
            f'white-space:nowrap;">{t["text"]}</span>'
            for t in ld["tokens"][:6]
        )
        desc_escaped = ld["description"].replace('"', '&quot;')

        rows += f"""<div title="{desc_escaped}" style="
            display:flex;align-items:flex-start;margin:2px 0;
            background:{ld['bg']};border-radius:5px;
            border-left:3px solid {ld['color']};
            padding:4px 6px;margin-left:{indent_px}px;">
          <span style="color:#6c7086;min-width:24px;font-size:10px;
                       padding-top:2px;font-family:monospace;flex-shrink:0;">
            {ld['line_no']}
          </span>
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
              <span style="color:{ld['color']};font-size:10px;font-weight:bold;
                           font-family:Arial;min-width:100px;flex-shrink:0;">
                {ld['label']}
              </span>
              <div style="flex:1;min-width:0;overflow:hidden;">{pills}</div>
            </div>
            <div style="color:#6c7086;font-size:10px;font-family:Arial;
                        margin-top:1px;white-space:nowrap;overflow:hidden;
                        text-overflow:ellipsis;">
              {ld['description']}
            </div>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 8px;
    background: #1e1e2e; font-family: Arial, sans-serif;
    -webkit-text-size-adjust: 100%;
  }}
  .hdr {{
    color: #cdd6f4; font-size: 12px; margin-bottom: 8px;
    padding-bottom: 6px; border-bottom: 1px solid #313244;
  }}
</style>
</head>
<body>
<div class="hdr">📊 Line-by-Line Code Analysis</div>
{rows}
</body>
</html>"""
