from __future__ import annotations
from typing import List, Dict, Any
import yaml
import os
import time
from ..core.base_model import Model, ModelCapabilities
from ..models import (
    OpenAICompatibleModel, AnthropicModel, GeminiModel, 
    OllamaModel, HuggingFaceModel, LiteLLMModel, CustomImageModel
)

class CapabilityTester:
    """
    Module to test model capabilities by performing real API calls.
    Outputs a YAML file with the results.
    """
    def __init__(self, models: List[Model]):
        self.models = models
        self.results = {}

    def test_all(self):
        for model in self.models:
            model_id = f"{model.__class__.__name__}_{model.model_name}"
            print(f"Testing capabilities for {model_id}...")
            
            self.results[model_id] = {
                "class": model.__class__.__name__,
                "model_name": model.model_name,
                "capabilities": {}
            }
            
            # Test Text Generation
            try:
                model.generate([{"role": "user", "content": "hi"}], max_tokens=1)
                self.results[model_id]["capabilities"]["TEXT2TEXT"] = True
            except Exception as e:
                self.results[model_id]["capabilities"]["TEXT2TEXT"] = False
                print(f"  TEXT2TEXT failed: {str(e)}")

            # Test Logprobs
            try:
                resp = model.generate([{"role": "user", "content": "hi"}], max_tokens=1, logprobs=True)
                # Check if logprobs are actually in the response
                self.results[model_id]["capabilities"]["LOGPROBS"] = "choices" in resp and resp["choices"][0].get("logprobs") is not None
            except Exception:
                self.results[model_id]["capabilities"]["LOGPROBS"] = False

            # Test Image Generation
            try:
                model.image("a small red square", size="256x256")
                self.results[model_id]["capabilities"]["TEXT2IMAGE"] = True
            except Exception:
                self.results[model_id]["capabilities"]["TEXT2IMAGE"] = False

            # Test Embedding
            try:
                model.embed(["test"])
                self.results[model_id]["capabilities"]["EMBEDDING"] = True
            except Exception:
                self.results[model_id]["capabilities"]["EMBEDDING"] = False

    def export_to_yaml(self, filepath: str):
        with open(filepath, 'w') as f:
            yaml.dump(self.results, f, default_flow_style=False)
        print(f"Results exported to {filepath}")

    @staticmethod
    def load_from_yaml(filepath: str) -> List[Model]:
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r') as f:
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
            m_cfg.pop("id", None) # Remove metadata ID
            if cls_name in model_classes:
                # Resolve api_key from env if provided as api_key_env
                if "api_key_env" in m_cfg:
                    m_cfg["api_key"] = os.environ.get(m_cfg.pop("api_key_env"))
                
                models.append(model_classes[cls_name](**m_cfg))
        return models

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".models.yaml")
    parser.add_argument("--output", default="capabilities.yaml")
    args = parser.parse_args()

    models = CapabilityTester.load_from_yaml(args.config)
    if not models:
        print(f"No models found in {args.config}. Please create it first.")
    else:
        tester = CapabilityTester(models)
        tester.test_all()
        tester.export_to_yaml(args.output)
