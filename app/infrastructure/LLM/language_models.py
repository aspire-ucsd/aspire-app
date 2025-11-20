import os
import requests
import httpx

from typing import Any, Dict, List, Optional

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

class TritonGPT(LLM):
    n: int = 1
    max_tokens: int = 768
    temperature: float = 0.2
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        
        url = "https://traip13.dsmlp.ucsd.edu/v1/chat/completions"
        api_key = os.getenv('TRITON_API_KEY')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "messages": prompt,
            "model": "llama-3",
            "max_tokens": self.max_tokens,
            "stream": False,
            "n": self.n,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }

        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:

        url = "https://traip13.dsmlp.ucsd.edu/v1/chat/completions"
        api_key = os.getenv('TRITON_API_KEY')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "messages": prompt,
            "model": "llama-3",
            "max_tokens": self.max_tokens,
            "stream": False,
            "n": self.n,
            "temperature": self.temperature,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "TritonGPT",
        }
    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom - TritonGPT"