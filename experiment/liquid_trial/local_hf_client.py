"""Direct Hugging Face client for the tiny Liquid AI trial.

The harness only needs a ``chat()`` method with the same shape as the
OpenRouter/CLI clients. This client loads LFM2 locally and returns generated
text plus approximate token usage.
"""

from __future__ import annotations

import time
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LocalHFClient:
    backend = "hf-local"

    def __init__(self, model_id: str, max_new_tokens: int = 256) -> None:
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16)
            .to(self.device)
            .eval()
        )

    def chat(
        self,
        model: str | list[str],
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 700,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        enc = self.tokenizer(text, return_tensors="pt")
        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)
        kwargs: dict[str, Any] = {
            "max_new_tokens": min(int(max_tokens), self.max_new_tokens),
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        if temperature and temperature > 0:
            kwargs.update(do_sample=True, temperature=max(float(temperature), 0.01), top_p=0.9)
        else:
            kwargs.update(do_sample=False)

        started = time.time()
        with torch.no_grad():
            out = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                **kwargs,
            )
        new_ids = out[0, input_ids.shape[1]:]
        generated = self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        return {
            "text": generated,
            "reasoning": "",
            "usage": {
                "prompt_tokens": int(input_ids.shape[1]),
                "completion_tokens": int(new_ids.shape[0]),
                "total_tokens": int(input_ids.shape[1] + new_ids.shape[0]),
                "cost": 0.0,
            },
            "model": self.model_id,
            "raw": {"elapsed_sec": round(time.time() - started, 2)},
        }
