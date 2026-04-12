"""
visualizer.py — Code Flowchart Generator
NLP BASED CODE INTERPRETER
Uses: Code Parsing, Control Flow Analysis, Graph Generation
"""

import re
import graphviz


# ─────────────────────────────────────────────
# NLP CONCEPT: Structural Parsing
# Extracts control flow structures from code
# like a syntactic parser extracts grammar
# ─────────────────────────────────────────────

def parse_control_flow(code: str) -> list:
    """
    Parse code and extract control flow elements.
    Returns list of (type, label, indent_level) tuples.
    """
    nodes = []
    lines = code.split('\n')

    nodes.append(('start', 'START', 0))

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            continue

        # Calculate indent level
        indent = len(line) - len(line.lstrip())
        level = indent // 4 + 1  # normalize to levels

        # Detect control structures (NLP: keyword recognition)
        if re.match(r'^\s*(def|function|func|sub)\s+(\w+)', line, re.I):
            match = re.search(r'(def|function|func|sub)\s+(\w+)', line, re.I)
            fname = match.group(2) if match else 'function'
            nodes.append(('function', f'Function: {fname}()', level))

        elif re.match(r'^\s*(class)\s+(\w+)', line, re.I):
            match = re.search(r'class\s+(\w+)', line, re.I)
            cname = match.group(1) if match else 'Class'
            nodes.append(('class', f'Class: {cname}', level))

        elif re.match(r'^\s*(if|elif|else if)\b', line, re.I):
            cond = re.sub(r'^\s*(if|elif|else if)\s*', '', stripped, flags=re.I)
            cond = re.sub(r'[:{]?\s*$', '', cond).strip()
            label = f'IF: {cond[:30]}...' if len(cond) > 30 else f'IF: {cond}'
            nodes.append(('decision', label, level))

        elif re.match(r'^\s*else\b', line, re.I):
            nodes.append(('decision', 'ELSE', level))

        elif re.match(r'^\s*(for|foreach)\b', line, re.I):
            cond = re.sub(r'^\s*(for|foreach)\s*', '', stripped, flags=re.I)
            cond = re.sub(r'[:{]?\s*$', '', cond).strip()
            label = f'FOR: {cond[:25]}...' if len(cond) > 25 else f'FOR: {cond}'
            nodes.append(('loop', label, level))

        elif re.match(r'^\s*while\b', line, re.I):
            cond = re.sub(r'^\s*while\s*', '', stripped, flags=re.I)
            cond = re.sub(r'[:{]?\s*$', '', cond).strip()
            label = f'WHILE: {cond[:25]}...' if len(cond) > 25 else f'WHILE: {cond}'
            nodes.append(('loop', label, level))

        elif re.match(r'^\s*return\b', line, re.I):
            val = re.sub(r'^\s*return\s*', '', stripped).strip()
            label = f'RETURN: {val[:20]}...' if len(val) > 20 else f'RETURN: {val}'
            nodes.append(('return', label, level))

        elif re.match(r'^\s*(print|println|printf|console\.log|System\.out)\b', line, re.I):
            label = stripped[:35] + '...' if len(stripped) > 35 else stripped
            nodes.append(('output', f'OUTPUT: {label}', level))

        elif '=' in stripped and not stripped.startswith('==') and not stripped.startswith('!'):
            label = stripped[:35] + '...' if len(stripped) > 35 else stripped
            nodes.append(('process', label, level))

    nodes.append(('end', 'END', 0))
    return nodes


def generate_flowchart(code: str, language: str = '') -> bytes:
    """
    Generate a flowchart from code and return as PNG bytes.
    """
    nodes = parse_control_flow(code)

    # Limit nodes for readability
    if len(nodes) > 20:
        nodes = nodes[:18] + [('end', 'END', 0)]

    dot = graphviz.Digraph(
        name='CodeFlowchart',
        comment=f'NLP Code Interpreter — {language} Flowchart',
        format='png'
    )

    dot.attr(
        rankdir='TB',
        bgcolor='#1e1e2e',
        fontname='Arial',
        splines='ortho',
        nodesep='0.6',
        ranksep='0.8'
    )

    dot.attr('node', fontname='Arial', fontsize='11', margin='0.3,0.2')
    dot.attr('edge', color='#89b4fa', penwidth='1.5', fontname='Arial', fontsize='9')

    # Shape and color map by node type
    style_map = {
        'start':    {'shape': 'oval',      'fillcolor': '#a6e3a1', 'fontcolor': '#1e1e2e', 'style': 'filled', 'penwidth': '2'},
        'end':      {'shape': 'oval',      'fillcolor': '#f38ba8', 'fontcolor': '#1e1e2e', 'style': 'filled', 'penwidth': '2'},
        'decision': {'shape': 'diamond',   'fillcolor': '#fab387', 'fontcolor': '#1e1e2e', 'style': 'filled'},
        'loop':     {'shape': 'diamond',   'fillcolor': '#cba6f7', 'fontcolor': '#1e1e2e', 'style': 'filled'},
        'function': {'shape': 'rectangle', 'fillcolor': '#89dceb', 'fontcolor': '#1e1e2e', 'style': 'filled,rounded'},
        'class':    {'shape': 'rectangle', 'fillcolor': '#74c7ec', 'fontcolor': '#1e1e2e', 'style': 'filled,rounded'},
        'process':  {'shape': 'rectangle', 'fillcolor': '#585b70', 'fontcolor': '#cdd6f4', 'style': 'filled'},
        'output':   {'shape': 'parallelogram', 'fillcolor': '#f9e2af', 'fontcolor': '#1e1e2e', 'style': 'filled'},
        'return':   {'shape': 'rectangle', 'fillcolor': '#a6e3a1', 'fontcolor': '#1e1e2e', 'style': 'filled'},
    }

    # Add nodes
    for i, (ntype, label, level) in enumerate(nodes):
        style = style_map.get(ntype, style_map['process'])
        node_id = f'node_{i}'
        dot.node(node_id, label=label, **style)

    # Add edges
    for i in range(len(nodes) - 1):
        src = f'node_{i}'
        dst = f'node_{i+1}'
        ntype = nodes[i][0]

        if ntype == 'decision':
            dot.edge(src, dst, label='Yes', color='#a6e3a1')
        elif ntype == 'loop':
            dot.edge(src, dst, label='Loop', color='#cba6f7')
        else:
            dot.edge(src, dst)

    # Render to PNG bytes
    return dot.pipe(format='png')
