"""
step_visualizer.py — Step-by-Step Code Execution Visualizer
NLP BASED CODE INTERPRETER v3.0
Like pythontutor.com — traces Python code execution showing variable states
"""

import sys
import io
import ast
import traceback
from copy import deepcopy


def safe_repr(val, max_len=40):
    """Safe string representation of a value"""
    try:
        r = repr(val)
        return r[:max_len] + "..." if len(r) > max_len else r
    except Exception:
        return "<unrepresentable>"


def trace_python_execution(code: str) -> list:
    """
    Trace Python code execution step by step.
    Returns list of steps with variable states.
    """
    steps = []
    lines = code.strip().split("\n")
    local_vars = {}
    output_lines = []

    # We'll use ast to parse and manually simulate simple code
    # For safety we use exec with tracing
    frame_data = {"steps": steps, "lines": lines, "output": output_lines}

    def tracer(frame, event, arg):
        if event == "line":
            lineno = frame.f_lineno - 1
            if 0 <= lineno < len(lines):
                line = lines[lineno]
                # Capture current local variables (filter internal ones)
                current_vars = {
                    k: safe_repr(v)
                    for k, v in frame.f_locals.items()
                    if not k.startswith("__") and not callable(v) and not isinstance(v, type)
                }
                frame_data["steps"].append({
                    "line_no": lineno + 1,
                    "line": line,
                    "variables": dict(current_vars),
                    "event": event,
                    "output": "\n".join(frame_data["output"])
                })
        return tracer

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()

    try:
        # Compile first to check syntax
        compiled = compile(code, "<string>", "exec")

        # Execute with tracing
        sys.settrace(tracer)
        exec_globals = {}
        exec(compiled, exec_globals)
        sys.settrace(None)

        # Capture final output
        output = captured.getvalue()
        if steps:
            steps[-1]["output"] = output
            steps[-1]["event"] = "final"

    except SyntaxError as e:
        steps = [{"line_no": e.lineno or 1, "line": lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else "",
                  "variables": {}, "event": "error", "output": f"Syntax Error: {e.msg}"}]
    except Exception as e:
        tb = traceback.format_exc()
        error_line = len(lines)
        for line in tb.split("\n"):
            if "line" in line.lower() and "<string>" in line:
                try:
                    error_line = int(line.strip().split("line")[1].strip().split(",")[0])
                except Exception:
                    pass
        if steps:
            steps[-1]["event"] = "error"
            steps[-1]["output"] = f"Runtime Error: {str(e)}"
        else:
            steps = [{"line_no": error_line, "line": lines[error_line - 1] if error_line <= len(lines) else "",
                      "variables": {}, "event": "error", "output": f"Runtime Error: {str(e)}"}]
    finally:
        sys.settrace(None)
        sys.stdout = old_stdout

    # Remove duplicate consecutive steps
    filtered = []
    prev = None
    for step in steps:
        if prev is None or step["line_no"] != prev["line_no"] or step["variables"] != prev["variables"]:
            filtered.append(step)
            prev = step

    return filtered[:50]  # Limit to 50 steps for performance


def render_step_visualizer(steps: list, code: str) -> str:
    """Render interactive step-by-step visualizer as HTML"""
    if not steps:
        return "<p style='color:#cdd6f4;font-family:Arial;'>No steps to visualize.</p>"

    lines = code.split("\n")
    steps_json = []
    for s in steps:
        steps_json.append({
            "line_no": s.get("line_no", 1),
            "line": s.get("line", "").replace("`", "'").replace("\\", "\\\\"),
            "variables": s.get("variables", {}),
            "event": s.get("event", "line"),
            "output": s.get("output", "").replace("`", "'").replace("\\", "\\\\")
        })

    import json
    steps_data = json.dumps(steps_json)
    lines_data = json.dumps(lines)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #1e1e2e; font-family: Arial, sans-serif; color: #cdd6f4; padding: 10px; }}
  .container {{ display: flex; gap: 12px; height: 480px; }}
  .left {{ flex: 1; display: flex; flex-direction: column; gap: 8px; }}
  .right {{ width: 280px; display: flex; flex-direction: column; gap: 8px; }}
  .panel {{ background: #313244; border-radius: 8px; padding: 10px; overflow-y: auto; }}
  .panel-title {{ font-size: 12px; font-weight: bold; color: #cba6f7; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }}
  .code-area {{ flex: 1; font-family: 'Courier New', monospace; font-size: 13px; overflow-y: auto; }}
  .code-line {{ display: flex; padding: 2px 6px; border-radius: 3px; align-items: flex-start; }}
  .code-line .ln {{ color: #6c7086; min-width: 28px; font-size: 11px; padding-top: 1px; }}
  .code-line .code {{ white-space: pre; color: #cdd6f4; }}
  .code-line.active {{ background: rgba(203,166,247,0.25); border-left: 3px solid #cba6f7; }}
  .code-line.error {{ background: rgba(243,139,168,0.2); border-left: 3px solid #f38ba8; }}
  .code-line.final {{ background: rgba(166,227,161,0.2); border-left: 3px solid #a6e3a1; }}
  .var-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  .var-table th {{ background: #45475a; color: #89dceb; padding: 4px 8px; text-align: left; font-size: 11px; }}
  .var-table td {{ padding: 4px 8px; border-bottom: 1px solid #45475a; color: #cdd6f4; word-break: break-all; }}
  .var-table tr:hover td {{ background: rgba(203,166,247,0.1); }}
  .no-vars {{ color: #6c7086; font-size: 12px; font-style: italic; padding: 8px; }}
  .output-box {{ font-family: monospace; font-size: 12px; color: #a6e3a1; white-space: pre-wrap; min-height: 40px; }}
  .controls {{ display: flex; gap: 8px; align-items: center; padding: 8px; background: #313244; border-radius: 8px; }}
  .btn {{ background: linear-gradient(135deg, #cba6f7, #89b4fa); color: #1e1e2e; border: none;
           padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 13px; }}
  .btn:hover {{ opacity: 0.85; }}
  .btn:disabled {{ background: #45475a; color: #6c7086; cursor: not-allowed; }}
  .step-info {{ font-size: 12px; color: #bac2de; flex: 1; text-align: center; }}
  .progress {{ height: 4px; background: #45475a; border-radius: 2px; overflow: hidden; }}
  .progress-bar {{ height: 100%; background: linear-gradient(90deg, #cba6f7, #89b4fa); transition: width 0.3s; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }}
  .badge-line {{ background: rgba(137,220,235,0.2); color: #89dceb; }}
  .badge-error {{ background: rgba(243,139,168,0.2); color: #f38ba8; }}
  .badge-final {{ background: rgba(166,227,161,0.2); color: #a6e3a1; }}
</style>
</head>
<body>
<div class="controls">
  <button class="btn" id="firstBtn" onclick="goFirst()">⏮</button>
  <button class="btn" id="prevBtn" onclick="goPrev()">◀ Prev</button>
  <button class="btn" id="nextBtn" onclick="goNext()">Next ▶</button>
  <button class="btn" id="lastBtn" onclick="goLast()">⏭</button>
  <span class="step-info" id="stepInfo">Step 1 of {len(steps)}</span>
  <span id="eventBadge" class="badge badge-line">line</span>
</div>
<div class="progress" style="margin:6px 0;">
  <div class="progress-bar" id="progressBar" style="width:0%"></div>
</div>
<div class="container">
  <div class="left">
    <div class="panel-title">📄 Code Execution</div>
    <div class="panel code-area" id="codeArea"></div>
  </div>
  <div class="right">
    <div class="panel-title">📦 Variables</div>
    <div class="panel" id="varPanel" style="flex:1;"></div>
    <div class="panel-title">📤 Output</div>
    <div class="panel" style="height:100px;">
      <div class="output-box" id="outputBox">No output yet</div>
    </div>
  </div>
</div>

<script>
const steps = {steps_data};
const lines = {lines_data};
let current = 0;

function render() {{
  const step = steps[current];
  const totalSteps = steps.length;

  // Update step info
  document.getElementById('stepInfo').textContent = `Step ${{current + 1}} of ${{totalSteps}}`;
  document.getElementById('progressBar').style.width = `${{((current + 1) / totalSteps) * 100}}%`;

  // Update badge
  const badge = document.getElementById('eventBadge');
  badge.textContent = step.event;
  badge.className = 'badge ' + (step.event === 'error' ? 'badge-error' : step.event === 'final' ? 'badge-final' : 'badge-line');

  // Render code with highlighted line
  let codeHtml = '';
  lines.forEach((line, idx) => {{
    const lineNo = idx + 1;
    let cls = 'code-line';
    if (lineNo === step.line_no) {{
      cls += ' ' + (step.event === 'error' ? 'error' : step.event === 'final' ? 'final' : 'active');
    }}
    const escaped = line.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    codeHtml += `<div class="${{cls}}"><span class="ln">${{lineNo}}</span><span class="code">${{escaped || '&nbsp;'}}</span></div>`;
  }});
  document.getElementById('codeArea').innerHTML = codeHtml;

  // Scroll active line into view
  const activeEl = document.querySelector('.code-line.active, .code-line.error, .code-line.final');
  if (activeEl) activeEl.scrollIntoView({{ block: 'center', behavior: 'smooth' }});

  // Render variables
  const vars = step.variables;
  const keys = Object.keys(vars);
  if (keys.length === 0) {{
    document.getElementById('varPanel').innerHTML = '<div class="no-vars">No variables yet</div>';
  }} else {{
    let tableHtml = '<table class="var-table"><tr><th>Variable</th><th>Value</th></tr>';
    keys.forEach(k => {{
      tableHtml += `<tr><td><b>${{k}}</b></td><td>${{vars[k]}}</td></tr>`;
    }});
    tableHtml += '</table>';
    document.getElementById('varPanel').innerHTML = tableHtml;
  }}

  // Render output
  const out = step.output || '';
  document.getElementById('outputBox').textContent = out || 'No output yet';

  // Update buttons
  document.getElementById('firstBtn').disabled = current === 0;
  document.getElementById('prevBtn').disabled = current === 0;
  document.getElementById('nextBtn').disabled = current === totalSteps - 1;
  document.getElementById('lastBtn').disabled = current === totalSteps - 1;
}}

function goNext() {{ if (current < steps.length - 1) {{ current++; render(); }} }}
function goPrev() {{ if (current > 0) {{ current--; render(); }} }}
function goFirst() {{ current = 0; render(); }}
function goLast() {{ current = steps.length - 1; render(); }}

// Keyboard navigation
document.addEventListener('keydown', (e) => {{
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') goNext();
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') goPrev();
}});

render();
</script>
</body>
</html>"""
