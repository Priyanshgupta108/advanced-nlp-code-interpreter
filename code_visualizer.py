"""
code_visualizer.py — Line-by-Line Code Visualizer
NLP BASED CODE INTERPRETER
"""

import re

TOKEN_TYPES = {
    "keyword":    {"color": "#cba6f7", "bg": "rgba(203,166,247,0.15)", "label": "Keyword"},
    "function":   {"color": "#89dceb", "bg": "rgba(137,220,235,0.15)", "label": "Function"},
    "variable":   {"color": "#a6e3a1", "bg": "rgba(166,227,161,0.15)", "label": "Variable"},
    "string":     {"color": "#f9e2af", "bg": "rgba(249,226,175,0.15)", "label": "String"},
    "number":     {"color": "#fab387", "bg": "rgba(250,179,135,0.15)", "label": "Number"},
    "operator":   {"color": "#f38ba8", "bg": "rgba(243,139,168,0.15)", "label": "Operator"},
    "comment":    {"color": "#6c7086", "bg": "rgba(108,112,134,0.15)", "label": "Comment"},
    "class":      {"color": "#74c7ec", "bg": "rgba(116,199,236,0.15)", "label": "Class"},
    "import":     {"color": "#b4befe", "bg": "rgba(180,190,254,0.15)", "label": "Import"},
    "return":     {"color": "#eba0ac", "bg": "rgba(235,160,172,0.15)", "label": "Return"},
    "condition":  {"color": "#e8d44d", "bg": "rgba(232,212,77,0.15)",  "label": "Condition"},
    "loop":       {"color": "#94e2d5", "bg": "rgba(148,226,213,0.15)", "label": "Loop"},
    "other":      {"color": "#cdd6f4", "bg": "rgba(205,214,244,0.10)", "label": "Code"},
}

KEYWORDS = {
    "python": ["def","class","if","elif","else","for","while","return","import","from",
               "try","except","with","as","pass","break","continue","lambda","yield",
               "None","True","False","and","or","not","in","is","global","nonlocal","raise","del"],
    "java":   ["public","private","protected","class","interface","extends","implements",
               "static","final","void","return","if","else","for","while","do","switch",
               "case","break","continue","new","this","super","try","catch","finally",
               "throw","throws","import","package","true","false","null"],
    "javascript": ["var","let","const","function","return","if","else","for","while","do",
                   "switch","case","break","continue","class","new","this","import","export",
                   "default","try","catch","finally","throw","async","await","true","false","null"],
    "cpp":    ["int","float","double","char","bool","void","string","auto","class","struct",
               "namespace","using","return","if","else","for","while","do","switch","case",
               "break","continue","new","delete","this","public","private","protected",
               "include","true","false","nullptr"],
}


def classify_token(token: str, language: str = "python") -> str:
    lang_keywords = KEYWORDS.get(language.lower(), KEYWORDS["python"])
    if token.startswith("#") or token.startswith("//"): return "comment"
    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")): return "string"
    if re.match(r'^-?\d+\.?\d*$', token): return "number"
    if token in ["import","from","#include"]: return "import"
    if token in ["return","yield"]: return "return"
    if token in ["if","elif","else","switch","case"]: return "condition"
    if token in ["for","while","do","foreach"]: return "loop"
    if token == "class": return "class"
    if token in lang_keywords: return "keyword"
    if token in ["+","-","*","/","=","==","!=","<",">","<=",">=","&&","||","!","++","--","+=","-=","*=","/="]: return "operator"
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token): return "function"
    return "other"


def analyze_line(line: str, line_no: int, language: str = "python") -> dict:
    stripped = line.strip()
    if not stripped:
        return {"line_no": line_no, "type": "empty", "label": "Empty line",
                "color": "#45475a", "bg": "transparent", "tokens": [],
                "raw": line, "description": "Blank line for spacing"}

    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
        line_type, label, description = "comment", "💬 Comment", "Developer note — not executed"
    elif re.match(r'^\s*(import|from|#include)\s+', stripped, re.I):
        line_type, label, description = "import", "📦 Import", "Loading external library"
    elif re.match(r'^\s*(def|function|func|void|public|private)\s+\w+\s*\(', stripped, re.I):
        line_type = "function"
        label = "⚙️ Function Definition"
        fname = re.search(r'(?:def|function|func)\s+(\w+)', stripped, re.I)
        description = f"Defines function '{fname.group(1)}'" if fname else "Function definition"
    elif re.match(r'^\s*class\s+\w+', stripped, re.I):
        line_type = "class"
        label = "🏛️ Class Definition"
        cname = re.search(r'class\s+(\w+)', stripped, re.I)
        description = f"Defines class '{cname.group(1)}'" if cname else "Class definition"
    elif re.match(r'^\s*(if|elif|else\s*:?|switch)\b', stripped, re.I):
        line_type, label, description = "condition", "🔀 Condition", "Decision branch"
    elif re.match(r'^\s*(for|while|do)\b', stripped, re.I):
        line_type, label, description = "loop", "🔄 Loop", "Repeating block of code"
    elif re.match(r'^\s*return\b', stripped, re.I):
        line_type, label = "return", "↩️ Return"
        val = re.sub(r'^\s*return\s*', '', stripped).strip()
        description = f"Returns: {val[:30]}" + ("..." if len(val) > 30 else "")
    elif re.match(r'^\s*(print|console\.log|System\.out|cout)\b', stripped, re.I):
        line_type, label, description = "output", "📤 Output", "Prints a value"
    elif '=' in stripped and not stripped.startswith('==') and not re.match(r'^\s*(if|while|return)', stripped):
        line_type, label = "assignment", "📝 Assignment"
        parts = stripped.split('=', 1)
        var = parts[0].strip().split()[-1] if parts else "?"
        description = f"Assigns value to '{var}'"
    else:
        line_type, label, description = "expression", "▶️ Expression", "Code statement"

    raw_tokens = re.findall(r'\"[^\"]*\"|\'[^\']*\'|[a-zA-Z_]\w*|\d+\.?\d*|[+\-*/=<>!&|]+', stripped)
    tokens = [{"text": tok, "type": classify_token(tok, language),
               "color": TOKEN_TYPES.get(classify_token(tok, language), TOKEN_TYPES["other"])["color"]}
              for tok in raw_tokens[:10]]

    color = TOKEN_TYPES.get(line_type, TOKEN_TYPES["other"])["color"]
    bg = TOKEN_TYPES.get(line_type, TOKEN_TYPES["other"])["bg"]

    return {"line_no": line_no, "type": line_type, "label": label, "color": color,
            "bg": bg, "tokens": tokens, "raw": line, "description": description,
            "indent": len(line) - len(line.lstrip())}


def generate_visualization(code: str, language: str = "python") -> list:
    return [analyze_line(line, i, language) for i, line in enumerate(code.split('\n'), 1)]


def render_visualization_html(analyzed_lines: list) -> str:
    """Returns complete self-contained HTML for st.components.v1.html()"""
    rows = ""
    for ld in analyzed_lines:
        if ld["type"] == "empty":
            rows += '<div style="height:6px;"></div>'
            continue

        indent_px = ld.get("indent", 0) * 2
        token_pills = ""
        for tok in ld["tokens"][:8]:
            token_pills += f'<span style="background:rgba(255,255,255,0.08);color:{tok["color"]};padding:1px 6px;border-radius:10px;font-size:11px;margin:1px;display:inline-block;">{tok["text"]}</span>'

        rows += f"""
        <div title="{ld['description']}" style="display:flex;align-items:flex-start;margin:2px 0;
            background:{ld['bg']};border-radius:6px;border-left:3px solid {ld['color']};
            padding:5px 8px;margin-left:{indent_px}px;">
            <span style="color:#6c7086;min-width:28px;font-size:11px;padding-top:2px;font-family:monospace;">{ld['line_no']}</span>
            <div style="flex:1;">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span style="color:{ld['color']};font-size:11px;font-weight:bold;font-family:Arial;min-width:140px;">{ld['label']}</span>
                    <div>{token_pills}</div>
                </div>
                <div style="color:#6c7086;font-size:11px;font-family:Arial;margin-top:2px;">{ld['description']}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
  body {{ margin:0;padding:8px;background:#1e1e2e;font-family:Arial,sans-serif; }}
  .header {{ color:#cdd6f4;font-size:13px;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #313244; }}
</style>
</head>
<body>
<div class="header">📊 Line-by-Line Code Analysis — Hover over any line for details</div>
{rows}
</body>
</html>"""
