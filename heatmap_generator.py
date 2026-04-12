"""
heatmap_generator.py — Code Readability Heatmap
NLP BASED CODE INTERPRETER
Scores each line for readability — pure Python, no API needed
"""

import re


def score_line(line: str) -> tuple:
    if not line.strip():
        return 100, ["Empty line"]

    stripped = line.strip()
    score = 100
    issues = []
    positives = []

    length = len(stripped)
    if length > 100:
        score -= 30
        issues.append(f"Too long ({length} chars)")
    elif length > 79:
        score -= 15
        issues.append(f"Slightly long ({length} chars)")
    else:
        positives.append("Good length")

    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
        score += 10
        positives.append("Has comment")

    magic_numbers = re.findall(r'(?<!["\'\w])\b(?!0\b|1\b)\d{2,}\b(?!["\'])', stripped)
    if magic_numbers:
        score -= len(magic_numbers) * 10
        issues.append(f"Magic numbers: {magic_numbers[:2]}")

    bad_names = re.findall(r'\b([a-wz])\s*=', stripped)
    if bad_names:
        score -= len(bad_names) * 8
        issues.append(f"Single-char vars: {bad_names}")

    good_names = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]{2,})\s*=', stripped)
    if good_names:
        positives.append("Descriptive names")

    indent = len(line) - len(line.lstrip())
    nesting = indent // 4
    if nesting >= 4:
        score -= 25
        issues.append(f"Deep nesting (level {nesting})")
    elif nesting == 3:
        score -= 10
        issues.append(f"High nesting (level {nesting})")

    score = max(0, min(100, score))
    reasons = issues if issues else positives
    return score, reasons


def get_color(score: int) -> str:
    if score >= 80: return "#10B981"
    elif score >= 60: return "#84CC16"
    elif score >= 40: return "#F59E0B"
    elif score >= 20: return "#EF4444"
    else: return "#991B1B"


def get_bg_color(score: int) -> str:
    if score >= 80: return "rgba(16,185,129,0.15)"
    elif score >= 60: return "rgba(132,204,22,0.15)"
    elif score >= 40: return "rgba(245,158,11,0.15)"
    elif score >= 20: return "rgba(239,68,68,0.15)"
    else: return "rgba(153,27,27,0.2)"


def generate_heatmap(code: str) -> tuple:
    lines = code.split('\n')
    lines_data = []
    total_score = 0
    valid_lines = 0

    for i, line in enumerate(lines, 1):
        score, reasons = score_line(line)
        lines_data.append({
            "line_no": i,
            "code": line,
            "score": score,
            "color": get_color(score),
            "bg": get_bg_color(score),
            "reasons": reasons
        })
        if line.strip():
            total_score += score
            valid_lines += 1

    overall = round(total_score / max(valid_lines, 1))
    return lines_data, overall


def render_heatmap_html(lines_data: list, overall: int) -> str:
    """Returns a complete self-contained HTML page for st.components.v1.html()"""
    rows = ""
    for ld in lines_data:
        tooltip = " | ".join(ld["reasons"][:2]) if ld["reasons"] else ""
        code_escaped = ld["code"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        code_display = code_escaped if code_escaped.strip() else "&nbsp;"
        rows += f"""
        <div title="{tooltip}" style="display:flex;align-items:center;margin:1px 0;
            background:{ld['bg']};border-radius:4px;
            border-left:3px solid {ld['color']};padding:2px 6px;">
            <span style="color:#6c7086;min-width:32px;font-size:11px;font-family:monospace;">{ld['line_no']:3d}</span>
            <span style="color:#cdd6f4;font-size:12px;flex:1;white-space:pre;overflow:hidden;font-family:monospace;">{code_display}</span>
            <span style="color:{ld['color']};font-size:11px;min-width:32px;text-align:right;font-weight:bold;">{ld['score']}</span>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
  body {{ margin:0; padding:8px; background:#1e1e2e; font-family:Arial,sans-serif; }}
  .header {{ color:#cdd6f4; font-size:13px; margin-bottom:8px; padding-bottom:6px; border-bottom:1px solid #313244; }}
  .score {{ font-size:18px; font-weight:bold; color:{get_color(overall)}; }}
</style>
</head>
<body>
<div class="header">
  Overall Readability Score: <span class="score">{overall}/100</span>
  &nbsp;&nbsp;|&nbsp;&nbsp;
  <span style="color:{get_color(overall)};font-weight:bold;">
    {"Excellent" if overall>=80 else "Good" if overall>=60 else "Fair" if overall>=40 else "Poor"}
  </span>
</div>
{rows}
</body>
</html>"""


def get_readability_summary(lines_data: list, overall: int) -> dict:
    scores = [ld["score"] for ld in lines_data]
    if not scores:
        return {}
    return {
        "overall": overall,
        "grade": "A" if overall>=85 else "B" if overall>=70 else "C" if overall>=55 else "D" if overall>=40 else "F",
        "excellent_lines": sum(1 for s in scores if s >= 80),
        "good_lines": sum(1 for s in scores if 60 <= s < 80),
        "fair_lines": sum(1 for s in scores if 40 <= s < 60),
        "poor_lines": sum(1 for s in scores if s < 40),
    }
