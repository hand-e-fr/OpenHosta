#!/usr/bin/env python3
"""Generate presets documentation page as HTML for openhosta.com integration."""

import os
os.environ["PYTHONPATH"] = "/home/ebatt/hand-e/products/OpenHosta/src"
import sys
sys.path.insert(0, "/home/ebatt/hand-e/products/OpenHosta/src")

import json
import html
from dataclasses import dataclass, field

from openhosta.presets import (
    vllm, sglang, openai, anthropic, gemini, openrouter, ollama, transformers, scaleway, litellm,
    _Caps, _IntersectionCaps,
    _M_QWEN3_6, _M_LLAMA, _M_MISTRAL, _M_CLAUDE, _M_GPT4, _M_OSERIES, _M_GEMINI,
    _B_VLLM, _B_SGLang, _B_Transformers, _B_Ollama,
    _B_OpenAI, _B_OpenAI_O, _B_Anthro, _B_Gemini,
    _B_LiteLLM, _B_OpenRouter, _B_Scaleway,
)


@dataclass
class PresetEntry:
    name: str
    params: dict
    doc: str = ""


@dataclass
class FamilyEntry:
    name: str
    presets: list[PresetEntry] = field(default_factory=list)


@dataclass
class ModelEntry:
    name: str
    families: list[FamilyEntry] = field(default_factory=list)
    caps: dict[str, bool] | None = None


@dataclass
class BackendEntry:
    name: str
    icon: str
    models: list[ModelEntry] = field(default_factory=list)
    desc: str = ""


def discover_presets(backend_obj, backend_name: str) -> ModelEntry:
    """Discover presets for a backend model."""
    model_entry = ModelEntry(name=backend_name)
    
    # Discover families
    for attr_name in dir(backend_obj):
        if attr_name.startswith("_") or attr_name == "capabilities":
            continue
        obj = getattr(backend_obj, attr_name)
        
        if isinstance(obj, _IntersectionCaps):
            model_entry.caps = obj.supports
            continue
        
        # Skip if it's a class (not an instance)
        if not hasattr(obj, "__class__"):
            continue
        
        # Check if this is a preset family (has dict-like attributes)
        family = FamilyEntry(name=attr_name)
        for preset_name in dir(obj):
            if preset_name.startswith("_"):
                continue
            preset = getattr(obj, preset_name)
            if isinstance(preset, dict):
                entry = PresetEntry(
                    name=preset_name,
                    params=preset,
                    doc=getattr(obj, preset_name, "").__doc__ or "" if hasattr(preset, "__doc__") else ""
                )
                family.presets.append(entry)
        
        if family.presets:
            model_entry.families.append(family)
    
    return model_entry


def discover_backend(backend_obj, name: str, icon: str, desc: str) -> BackendEntry:
    """Discover all models and their presets for a backend."""
    backend = BackendEntry(name=name, icon=icon, desc=desc)
    
    for attr_name in dir(backend_obj):
        if attr_name.startswith("_"):
            continue
        model_obj = getattr(backend_obj, attr_name)
        
        if not hasattr(model_obj, "__class__"):
            continue
        
        me = discover_presets(model_obj, attr_name)
        if me.families or me.caps is not None:
            backend.models.append(me)
    
    return backend


def get_all_backends():
    """Get all backends with their metadata."""
    return [
        discover_backend(vllm, "vllm", "🚀", "vLLM — high-performance inference server"),
        discover_backend(sglang, "sglang", "🔥", "SGLang — structured generation engine"),
        discover_backend(transformers, "transformers", "🤗", "HuggingFace Transformers"),
        discover_backend(ollama, "ollama", "🌊", "Ollama — local model runner"),
        discover_backend(openai, "openai", "🟢", "OpenAI — GPT-4, o-series"),
        discover_backend(anthropic, "anthropic", "🟠", "Anthropic — Claude"),
        discover_backend(gemini, "gemini", "🔵", "Google Gemini"),
        discover_backend(litellm, "litellm", "🔗", "LiteLLM proxy"),
        discover_backend(openrouter, "openrouter", "🔀", "OpenRouter gateway"),
        discover_backend(scaleway, "scaleway", "⚡", "Scaleway ML (vLLM + extensions)"),
    ]


CAPABILITY_MATRIX = [
    ("thinking", "Thinking"), ("tool_calling", "Tool Calling"),
    ("structured_output", "Structured Output"), ("logprobs", "Logprobs"),
    ("prompt_caching", "Prompt Caching"), ("parallel_tool_calls", "Parallel Tools"),
    ("vision", "Vision"), ("audio", "Audio"),
    ("function_calling", "Function Calling"), ("json_schema", "JSON Schema"),
    ("stream_options", "Streaming"), ("stop_sequences", "Stop Sequences"),
]


def generate_html(backends: list[BackendEntry]) -> str:
    """Generate complete HTML page."""
    
    # Build capability matrix HTML
    cap_rows = []
    for feat, display in CAPABILITY_MATRIX:
        cells = []
        for b in backends:
            if b.models[0].caps:
                val = b.models[0].caps.get(feat, False)
                icon = "✅" if val else "❌"
            else:
                icon = "—"
            cells.append(f"<td class=\"cap-cell\" title=\"{b.name}\">{icon}</td>")
        cap_rows.append(f"<tr><td class=\"cap-name\">{display}</td>{''.join(cells)}</tr>")
    
    cap_matrix = f"""
    <div class=\"card\">
        <h2 class=\"card-title\">Capability Matrix — qwen3_6</h2>
        <div class=\"matrix-scroll\">
            <table class=\"cap-table\">
                <thead>
                    <tr>
                        <th class=\"cap-name\">Feature</th>
                        {''.join(f'<th class=\"cap-back">{b.icon} {b.name}</th>' for b in backends)}
                    </tr>
                </thead>
                <tbody>{''.join(cap_rows)}</tbody>
            </table>
        </div>
    </div>"""
    
    # Build families reference HTML
    families_html = f"""
    <div class=\"card\">
        <h2 class=\"card-title\">Preset Families Reference</h2>
        
        <h3>Thinking / Reasoning</h3>
        <table class=\"ref-table\">
            <thead><tr><th>Preset</th><th>Effect</th><th>Budget Tokens</th></tr></thead>
            <tbody>
                <tr><td>disabled</td><td>No thinking</td><td>0</td></tr>
                <tr><td>minimal</td><td>Quick reasoning</td><td>128</td></tr>
                <tr><td>low</td><td>Moderate</td><td>1024</td></tr>
                <tr><td>medium</td><td>Standard</td><td>4096</td></tr>
                <tr><td>high</td><td>Extended</td><td>8192</td></tr>
                <tr><td>max</td><td>Maximum</td><td>16384</td></tr>
            </tbody>
        </table>
        
        <h3>Sampling</h3>
        <table class=\"ref-table\">
            <thead><tr><th>Preset</th><th>temp</th><th>top_p</th><th>top_k</th><th>Description</th></tr></thead>
            <tbody>
                <tr><td>creative</td><td>1.0</td><td>0.95</td><td>20</td><td>Maximum diversity</td></tr>
                <tr><td>general</td><td>1.0</td><td>0.95</td><td>20</td><td>Balanced defaults</td></tr>
                <tr><td>coding</td><td>0.6</td><td>0.95</td><td>20</td><td>Code generation</td></tr>
                <tr><td>instruct</td><td>0.7</td><td>0.80</td><td>20</td><td>Instruction following</td></tr>
                <tr><td>precise</td><td>0.2</td><td>0.50</td><td>10</td><td>Deterministic output</td></tr>
            </tbody>
        </table>
        
        <h3>Output Length</h3>
        <table class=\"ref-table\">
            <thead><tr><th>Preset</th><th>max_tokens</th></tr></thead>
            <tbody>
                <tr><td>short</td><td>256</td></tr>
                <tr><td>medium</td><td>2048</td></tr>
                <tr><td>long</td><td>8192</td></tr>
            </tbody>
        </table>
    </div>"""
    
    # Build backend detail HTML
    backend_details = []
    for b in backends:
        models_html = []
        for m in b.models:
            families_html = []
            for fam in m.families:
                presets_html = []
                for p in fam.presets:
                    params_str = json.dumps(p.params, indent=2, default=str)
                    presets_html.append(f"""
                    <div class=\"preset\">
                        <code class=\"preset-name\">{fam.name}.{p.name}</code>
                        <pre>{params_str}</pre>
                    </div>""")
                
                if presets_html:
                    families_html.append(f"""
                    <h4 class=\"family-name\">{fam.name}</h4>
                    {"".join(presets_html)}""")
            
            caps_html = ""
            if m.caps:
                caps_items = []
                for k, v in m.caps.items():
                    icon = "✅" if v else "❌"
                    caps_items.append(f"{icon} {k}")
                caps_html = f"""
                    <div class=\"caps-badge\">
                        <strong>Capabilities:</strong> {', '.join(caps_items)}
                    </div>"""
            
            if families_html:
                models_html.append(f"""
                <h3 class=\"model-name\">{m.name}</h3>
                {caps_html}
                {"".join(families_html)}""")
        
        if models_html:
            backend_details.append(f"""
            <div class=\"backend-card\">
                <h2 class=\"backend-title\">{b.icon} {b.name}</h2>
                <p class=\"backend-desc\">{b.desc}</p>
                {"".join(models_html)}
            </div>""")
    
    # Build examples HTML
    examples_html = """
    <div class=\"card\">
        <h2 class=\"card-title\">Usage Examples</h2>
        
        <h3>Chaining presets</h3>
        <pre><code class=\"language-python\">from openhosta.presets import vllm, anthropic, openai

body = (vllm.qwen3_6.thinking.disabled
        | vllm.qwen3_6.sampling.coding
        | vllm.qwen3_6.length.short)

# Merge with custom params
body | {"seed": 42, "stop_sequences": ["\\n"]}</code></pre>
        
        <h3>Guard by capabilities</h3>
        <pre><code class=\"language-python\">from openhosta.presets import vllm

if vllm.qwen3_6.capabilities.supports["thinking"]:
    body = vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding
</code></pre>
        
        <h3>Integration with BackendModel</h3>
        <pre><code class=\"language-python\">from openhosta import BackendModel
from openhosta.presets import vllm

model = BackendModel(
    provider="ikoula",
    model_name="Qwen3.6-8B",
    base_url="http://ikoula.example.com/v1",
    api_key="none",
    body=vllm.qwen3_6.thinking.disabled | vllm.qwen3_6.sampling.coding,
)</code></pre>
    </div>"""
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenHosta Presets — Parameter Library</title>
    <style>
        :root {{
            --oh-bg: #0a0a0f;
            --oh-surface: #12121a;
            --oh-card: #1a1a2e;
            --oh-border: #2a2a3e;
            --oh-text: #e0e0f0;
            --oh-text-muted: #8888aa;
            --oh-accent: #6366f1;
            --oh-accent-hover: #818cf8;
            --oh-success: #22c55e;
            --oh-warning: #f59e0b;
            --oh-danger: #ef4444;
            --oh-code: #1e1e2e;
            --oh-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --oh-font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: var(--oh-bg);
            color: var(--oh-text);
            font-family: var(--oh-font);
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 3rem 0;
            border-bottom: 1px solid var(--oh-border);
            margin-bottom: 3rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .subtitle {{
            font-size: 1.25rem;
            color: var(--oh-text-muted);
            margin-bottom: 1.5rem;
        }}
        
        .code-inline {{
            background: var(--oh-code);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: var(--oh-font-mono);
            font-size: 0.9rem;
        }}
        
        .card {{
            background: var(--oh-surface);
            border: 1px solid var(--oh-border);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        
        .card-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--oh-accent);
        }}
        
        .backend-card {{
            background: var(--oh-card);
            border: 1px solid var(--oh-border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: border-color 0.2s;
        }}
        
        .backend-card:hover {{
            border-color: var(--oh-accent);
        }}
        
        .backend-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .backend-desc {{
            color: var(--oh-text-muted);
            margin-bottom: 1rem;
        }}
        
        .model-name {{
            font-size: 1.1rem;
            font-weight: 500;
            margin: 1rem 0;
            color: var(--oh-accent-hover);
        }}
        
        .family-name {{
            font-size: 0.9rem;
            font-weight: 500;
            margin: 0.75rem 0 0.5rem;
            color: var(--oh-text-muted);
            text-transform: uppercase;
        }}
        
        .preset {{
            background: var(--oh-code);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border-left: 3px solid var(--oh-accent);
        }}
        
        .preset-name {{
            font-family: var(--oh-font-mono);
            font-size: 0.8rem;
            color: var(--oh-success);
        }}
        
        pre {{
            background: var(--oh-code);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
            font-family: var(--oh-font-mono);
            font-size: 0.85rem;
            line-height: 1.5;
            color: var(--oh-text);
        }}
        
        .caps-badge {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0.75rem 0;
            font-size: 0.8rem;
        }}
        
        .matrix-scroll {{
            overflow-x: auto;
        }}
        
        .cap-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .cap-table th {{
            padding: 0.75rem;
            text-align: left;
            font-weight: 500;
            background: var(--oh-code);
            position: sticky;
            left: 0;
        }}
        
        .cap-name {{
            min-width: 150px;
            position: sticky;
            left: 0;
            background: var(--oh-surface);
            font-weight: 500;
        }}
        
        .cap-cell {{
            padding: 0.5rem;
            text-align: center;
        }}
        
        .ref-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        .ref-table th, .ref-table td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--oh-border);
        }}
        
        .ref-table th {{
            background: var(--oh-code);
            font-weight: 500;
        }}
        
        .ref-table td {{
            font-family: var(--oh-font-mono);
            font-size: 0.9rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .badge-primary {{ background: var(--oh-accent); color: white; }}
        .badge-success {{ background: var(--oh-success); color: white; }}
        .badge-warning {{ background: var(--oh-warning); color: black; }}
        
        nav {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }}
        
        nav a {{
            background: var(--oh-card);
            color: var(--oh-text);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            border: 1px solid var(--oh-border);
            transition: all 0.2s;
        }}
        
        nav a:hover {{
            border-color: var(--oh-accent);
            color: var(--oh-accent-hover);
        }}
        
        footer {{
            text-align: center;
            padding: 2rem 0;
            color: var(--oh-text-muted);
            font-size: 0.9rem;
            margin-top: 4rem;
            border-top: 1px solid var(--oh-border);
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            h1 {{ font-size: 1.75rem; }}
            .card {{ padding: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>OpenHosta Presets</h1>
            <p class="subtitle">Unified parameter library for LLM backends • Chain with <span class="code-inline">|</span> • Guard with <span class="code-inline">.capabilities</span></p>
            <nav>
                <a href="#usage">Usage</a>
                <a href="#families">Families</a>
                <a href="#matrix">Cap Matrix</a>
                <a href="#backends">Backends</a>
            </nav>
        </header>
        
        {examples_html}
        
        <a name="families"></a>
        {families_html}
        
        <a name="matrix"></a>
        {cap_matrix}
        
        <a name="backends"></a>
        <div class="card">
            <h2 class="card-title">Backend Details</h2>
            {"".join(backend_details)}
        </div>
        
        <footer>
            <p>OpenHosta V5 — Presets documentation • Generated automatically</p>
        </footer>
    </div>
</body>
</html>"""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate OpenHosta presets HTML documentation")
    parser.add_argument("-o", "--output", default="presets.html", help="Output HTML file path (default: presets.html)")
    args = parser.parse_args()
    
    backends = get_all_backends()
    html_content = generate_html(backends)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Generated {args.output} ({len(html_content)} bytes)")
    print(f"Backends: {len(backends)}")
    total_models = sum(len(b.models) for b in backends)
    print(f"Models: {total_models}")
    total_presets = 0
    for b in backends:
        for m in b.models:
            total_presets += sum(len(f.presets) for f in m.families)
    print(f"Total presets: {total_presets}")


if __name__ == "__main__":
    main()