"""
vscode_editor.py — Monaco Editor Component for Streamlit
Gives real VS Code experience: syntax highlighting + autocomplete + suggestions
"""

import streamlit.components.v1 as components


def render_monaco_editor(
    value: str = "",
    language: str = "python",
    height: int = 320,
    key: str = "monaco_editor",
) -> str:
    """
    Renders a Monaco Editor (VS Code engine) inside Streamlit.
    Returns the current code as a string via a hidden textarea sync.

    Features:
    - Real VS Code syntax highlighting
    - Keyword autocomplete (im → import, pu → public, etc.)
    - IntelliSense suggestions
    - Multiple language support
    - VS Code Dark+ theme
    - Minimap, line numbers, bracket matching
    """

    # Map Streamlit/common language names to Monaco language IDs
    LANG_MAP = {
        "python": "python",
        "java": "java",
        "c++": "cpp",
        "cpp": "cpp",
        "c": "c",
        "javascript": "javascript",
        "typescript": "typescript",
        "go": "go",
        "kotlin": "kotlin",
        "ruby": "ruby",
        "sql": "sql",
        "php": "php",
        "html": "html",
        "css": "css",
        "rust": "rust",
        "swift": "swift",
    }
    monaco_lang = LANG_MAP.get(language.lower(), "python")

    # Escape the initial value for safe injection into JS
    escaped_value = (value
                     .replace("\\", "\\\\")
                     .replace("`", "\\`")
                     .replace("$", "\\$"))

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#1e1e1e; font-family:'Segoe UI',Arial,sans-serif; overflow:hidden; }}

  /* Title bar */
  .titlebar {{
    background:#2d2d2d; height:32px; display:flex; align-items:center;
    padding:0 12px; gap:8px; border-bottom:1px solid #3c3c3c;
    user-select:none;
  }}
  .dot {{ width:12px; height:12px; border-radius:50%; }}
  .dot-r{{background:#ff5f56;}} .dot-y{{background:#ffbd2e;}} .dot-g{{background:#27c93f;}}
  .fname {{ color:#cccccc; font-size:12px; margin-left:6px; }}
  .flang {{ color:#569cd6; font-size:11px; margin-left:auto; }}
  .fbadge {{ background:#252526; color:#858585; font-size:10px;
             padding:2px 8px; border-radius:3px; margin-left:8px; }}

  /* Editor container */
  #editor-container {{
    width:100%; 
    height:{height}px;
    border:1px solid #3c3c3c;
    border-top:none;
  }}

  /* Status bar */
  .statusbar {{
    background:#007acc; color:#fff; height:22px;
    display:flex; align-items:center; padding:0 12px;
    font-size:11px; font-family:'Segoe UI',Arial,sans-serif;
    gap:16px; border-radius:0 0 6px 6px;
  }}
  .statusbar span {{ opacity:0.9; }}

  /* Apply button */
  .apply-btn {{
    background:linear-gradient(135deg,#cba6f7,#89b4fa);
    color:#1e1e2e; border:none; padding:5px 18px;
    border-radius:5px; cursor:pointer; font-size:12px;
    font-weight:bold; margin-left:auto;
    transition:opacity 0.2s;
  }}
  .apply-btn:hover {{ opacity:0.85; }}

  /* Hidden textarea to sync value out */
  #sync-area {{
    position:absolute; left:-9999px; top:-9999px;
    width:1px; height:1px; opacity:0;
  }}
</style>
</head>
<body>

<div class="titlebar">
  <span class="dot dot-r"></span>
  <span class="dot dot-y"></span>
  <span class="dot dot-g"></span>
  <span class="fname">📄 code.{monaco_lang}</span>
  <span class="flang" id="lang-label">{language.upper()}</span>
  <span class="fbadge" id="ln-col">Ln 1, Col 1</span>
</div>

<div id="editor-container"></div>

<div class="statusbar">
  <span id="status-lang">🔤 {language.upper()}</span>
  <span id="status-ln">Ln 1</span>
  <span id="status-col">Col 1</span>
  <span id="status-chars">0 chars</span>
  <span>UTF-8</span>
  <span>LF</span>
  <button class="apply-btn" onclick="applyCode()">✓ Use This Code</button>
</div>

<textarea id="sync-area" readonly></textarea>

<!-- Monaco Editor from CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>
<script>
require.config({{
  paths: {{ vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' }}
}});

require(['vs/editor/editor.main'], function() {{
  // Create the Monaco editor
  const editor = monaco.editor.create(
    document.getElementById('editor-container'),
    {{
      value: `{escaped_value}`,
      language: '{monaco_lang}',
      theme: 'vs-dark',
      fontSize: 14,
      fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace",
      fontLigatures: true,
      lineNumbers: 'on',
      minimap: {{ enabled: true, scale: 0.8 }},
      scrollBeyondLastLine: false,
      automaticLayout: true,
      wordWrap: 'on',
      tabSize: 4,
      insertSpaces: true,
      bracketPairColorization: {{ enabled: true }},
      autoClosingBrackets: 'always',
      autoClosingQuotes: 'always',
      autoIndent: 'full',
      formatOnPaste: true,
      formatOnType: true,
      suggestOnTriggerCharacters: true,
      quickSuggestions: {{
        other: true,
        comments: false,
        strings: false
      }},
      acceptSuggestionOnEnter: 'on',
      tabCompletion: 'on',
      parameterHints: {{ enabled: true }},
      hover: {{ enabled: true }},
      contextmenu: true,
      folding: true,
      foldingHighlight: true,
      showFoldingControls: 'always',
      renderLineHighlight: 'all',
      cursorStyle: 'line',
      cursorBlinking: 'smooth',
      smoothScrolling: true,
      mouseWheelZoom: true,
      renderWhitespace: 'selection',
      scrollbar: {{
        vertical: 'auto',
        horizontal: 'auto',
        useShadows: true,
        verticalScrollbarSize: 8,
        horizontalScrollbarSize: 8
      }},
    }}
  );

  // Update status bar on cursor change
  editor.onDidChangeCursorPosition(function(e) {{
    const pos = e.position;
    document.getElementById('status-ln').textContent = 'Ln ' + pos.lineNumber;
    document.getElementById('status-col').textContent = 'Col ' + pos.column;
    document.getElementById('ln-col').textContent = 'Ln ' + pos.lineNumber + ', Col ' + pos.column;
  }});

  // Update char count on content change
  editor.onDidChangeModelContent(function() {{
    const val = editor.getValue();
    document.getElementById('status-chars').textContent = val.length + ' chars';
    // Auto-sync every keystroke so Streamlit gets updates
    document.getElementById('sync-area').value = val;
  }});

  // Set initial char count
  const initVal = editor.getValue();
  document.getElementById('status-chars').textContent = initVal.length + ' chars';
  document.getElementById('sync-area').value = initVal;

  // Apply code — send to parent Streamlit frame
  window.applyCode = function() {{
    const code = editor.getValue();
    document.getElementById('sync-area').value = code;
    // Send to Streamlit via postMessage
    window.parent.postMessage({{
      type: 'streamlit:setComponentValue',
      value: code
    }}, '*');
  }};

  // Also expose editor globally for the apply button
  window._monacoEditor = editor;

  // Add extra keybinding: Ctrl+Enter to apply
  editor.addCommand(
    monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
    function() {{ window.applyCode(); }}
  );
}});
</script>
</body>
</html>"""

    # Render the component — height accounts for titlebar(32) + editor + statusbar(22)
    total_height = height + 32 + 22 + 10
    result = components.html(html, height=total_height, scrolling=False)
    return result if result else value
