"""Open-source LLM wrapper with offline-safe fallback."""

from __future__ import annotations


SAFE_REFUSAL = (
    "I can't help with bypassing safety controls or enabling harm. "
    "I can help with safe alternatives such as defensive analysis, policy explanation, or risk mitigation."
)


class LLMWrapper:
    """Wraps Llama-3.2-3B-Instruct or a deterministic safe stub."""

    def __init__(self, backend: str = "stub", model_name: str = "meta-llama/Llama-3.2-3B-Instruct") -> None:
        self.backend = backend
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        if backend == "hf":
            self._load_hf()

    def _load_hf(self) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, device_map="auto")

    def generate(self, messages: list[dict[str, str]]) -> str:
        if self.backend == "hf" and self.model is not None and self.tokenizer is not None:
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(**inputs, max_new_tokens=256, do_sample=False)
            return self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1] :], skip_special_tokens=True)

        latest = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
        if any(term in latest.lower() for term in ["ignore previous", "jailbreak", "bypass", "illegal", "malware"]):
            return SAFE_REFUSAL
        return "Safe response: I can help with this at a high level and keep the guidance constructive."

