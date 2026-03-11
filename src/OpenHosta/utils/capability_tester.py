from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime
import base64
import yaml
import os
import time
from ..core.base_model import Model, ModelCapabilities
from ..models import (
    OpenAICompatibleModel, AnthropicModel, GeminiModel, 
    OllamaModel, HuggingFaceModel, HuggingFaceReplicateModel,
    LiteLLMModel, CustomImageModel
)


# Human-readable label for each model backend class
API_TYPE_LABELS: Dict[str, str] = {
    "OpenAICompatibleModel": "OpenAI Compatible",
    "OllamaModel":           "Ollama",
    "AnthropicModel":        "Anthropic",
    "GeminiModel":           "Gemini",
    "HuggingFaceModel":      "HuggingFace",
    "HuggingFaceReplicateModel": "HuggingFace Replicate",
    "LiteLLMModel":          "LiteLLM",
    "CustomImageModel":      "Custom Image",
}

# Capabilities tested (in display order)
CAPABILITY_COLUMNS = [
    ("TEXT2TEXT",  "Text"),
    ("VISION",    "Vision"),
    ("GENERATE",  "Generate"),
    ("LOGPROBS",  "Logprobs"),
    ("TEXT2IMAGE", "Image Gen"),
    ("EMBEDDING", "Embedding"),
]

# Minimal 1×1 red PNG for vision test (avoids external files)
_TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
    "nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg=="
)


class CapabilityTester:
    """
    Module to test model capabilities by performing real API calls.
    Outputs a YAML or Markdown report with the results.
    """
    def __init__(self, models: List[Model]):
        self.models = models
        self.results: List[Dict[str, Any]] = []

    def test_all(self):
        for model in self.models:
            class_name = model.__class__.__name__
            model_id = f"{class_name}_{model.model_name}"
            print(f"Testing capabilities for {model_id}...")

            entry: Dict[str, Any] = {
                "api_type": API_TYPE_LABELS.get(class_name, class_name),
                "class": class_name,
                "model_name": model.model_name,
                "capabilities": {},
            }

            # Test Text Generation
            try:
                model.generate([{"role": "user", "content": "hi"}], max_tokens=1)
                entry["capabilities"]["TEXT2TEXT"] = True
            except Exception as e:
                entry["capabilities"]["TEXT2TEXT"] = False
                print(f"  TEXT2TEXT failed: {str(e)}")

            # Test Logprobs
            try:
                resp = model.generate([{"role": "user", "content": "hi"}], max_tokens=1, logprobs=True)
                entry["capabilities"]["LOGPROBS"] = (
                    "choices" in resp and resp["choices"][0].get("logprobs") is not None
                )
            except Exception:
                entry["capabilities"]["LOGPROBS"] = False

            # Test Image Generation
            try:
                model.image("a small red square", size="256x256")
                entry["capabilities"]["TEXT2IMAGE"] = True
            except Exception:
                entry["capabilities"]["TEXT2IMAGE"] = False

            # Test Vision (image upload + question)
            try:
                vision_msg = [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What color is this image? Answer in one word."},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{_TINY_PNG_B64}"
                        }},
                    ],
                }]
                model.generate(vision_msg, max_tokens=5)
                entry["capabilities"]["VISION"] = True
            except Exception as e:
                entry["capabilities"]["VISION"] = False
                print(f"  VISION failed: {str(e)[:120]}")

            # Test Generate (assistant-message prefill / completion)
            try:
                prefill_msgs = [
                    {"role": "user", "content": "Count from 1 to 5."},
                    {"role": "assistant", "content": "1, 2, 3"},
                ]
                resp = model.generate(prefill_msgs, max_tokens=5)
                # Consider it supported if we get a non-empty response
                content = model.get_response_content(resp)
                entry["capabilities"]["GENERATE"] = len(content.strip()) > 0
            except Exception as e:
                entry["capabilities"]["GENERATE"] = False
                print(f"  GENERATE failed: {str(e)[:120]}")

            # Test Embedding
            try:
                model.embed(["test"])
                entry["capabilities"]["EMBEDDING"] = True
            except Exception:
                entry["capabilities"]["EMBEDDING"] = False

            self.results.append(entry)

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def export_to_yaml(self, filepath: str, version: str = ""):
        """Export results as a clean, readable YAML file."""
        doc: Dict[str, Any] = {}
        if version:
            doc["version"] = version
        doc["generated"] = datetime.now().isoformat(timespec="seconds")
        doc["models"] = []

        for entry in self.results:
            doc["models"].append({
                "api_type": entry["api_type"],
                "model": entry["model_name"],
                "capabilities": entry["capabilities"],
            })

        with open(filepath, "w") as f:
            yaml.dump(doc, f, default_flow_style=False, sort_keys=False)
        print(f"YAML exported → {filepath}")

    def export_to_markdown(self, filepath: str, version: str = ""):
        """Export results as a human-readable Markdown compatibility matrix."""
        lines: List[str] = []

        # Header
        title = f"OpenHosta v{version}" if version else "OpenHosta"
        lines.append(f"# {title} — Model Compatibility Matrix\n")
        lines.append(f"> Generated on {datetime.now().strftime('%Y-%m-%d')} by `capability_tester.py`\n")

        # Table header
        cap_headers = " | ".join(name for _, name in CAPABILITY_COLUMNS)
        lines.append(f"| API Type | Model | {cap_headers} |")
        sep = " | ".join(":---:" for _ in CAPABILITY_COLUMNS)
        lines.append(f"|----------|-------|{sep}|")

        # Table rows — group by api_type for readability
        sorted_results = sorted(self.results, key=lambda e: (e["api_type"], e["model_name"]))
        for entry in sorted_results:
            caps = entry["capabilities"]
            cells = " | ".join(
                "✅" if caps.get(key) else "❌" for key, _ in CAPABILITY_COLUMNS
            )
            lines.append(f"| {entry['api_type']} | `{entry['model_name']}` | {cells} |")

        lines.append("")  # trailing newline

        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        print(f"Markdown exported → {filepath}")

    # ------------------------------------------------------------------
    # Loading models from config
    # ------------------------------------------------------------------

    @staticmethod
    def load_from_yaml(filepath: str) -> List[Model]:
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r") as f:
            config = yaml.safe_load(f)

        models = []
        model_classes = {
            "OpenAICompatibleModel": OpenAICompatibleModel,
            "AnthropicModel": AnthropicModel,
            "GeminiModel": GeminiModel,
            "OllamaModel": OllamaModel,
            "HuggingFaceModel": HuggingFaceModel,
            "HuggingFaceReplicateModel": HuggingFaceReplicateModel,
            "LiteLLMModel": LiteLLMModel,
            "CustomImageModel": CustomImageModel,
        }

        for m_cfg in config.get("models", []):
            cls_name = m_cfg.pop("class", None)
            m_cfg.pop("id", None)  # Remove metadata ID
            if cls_name in model_classes:
                if "api_key_env" in m_cfg:
                    m_cfg["api_key"] = os.environ.get(m_cfg.pop("api_key_env"))
                models.append(model_classes[cls_name](**m_cfg))
        return models


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test OpenHosta model capabilities")
    parser.add_argument("--config", default=".models.yaml",
                        help="Path to the models YAML config (default: .models.yaml)")
    parser.add_argument("--output", default=None,
                        help="Output file path (default: auto-generated from format & version)")
    parser.add_argument("--format", choices=["md", "yaml", "both"], default="both",
                        help="Output format (default: both)")
    parser.add_argument("--version", default="",
                        help="Release version label, e.g. '3.0' or '4.0'")
    args = parser.parse_args()

    models = CapabilityTester.load_from_yaml(args.config)
    if not models:
        print(f"No models found in {args.config}. Please create it first.")
    else:
        tester = CapabilityTester(models)
        tester.test_all()

        if args.format in ("yaml", "both"):
            yaml_path = args.output if (args.output and args.format == "yaml") else "capabilities.yaml"
            tester.export_to_yaml(yaml_path, version=args.version)

        if args.format in ("md", "both"):
            if args.output and args.format == "md":
                md_path = args.output
            elif args.version:
                md_path = f"docs/compatibility/v{args.version}.md"
            else:
                md_path = "docs/compatibility/latest.md"
            tester.export_to_markdown(md_path, version=args.version)
