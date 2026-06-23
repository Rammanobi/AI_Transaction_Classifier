import json
from openai import AsyncOpenAI
from typing import List, Dict, Any
from app.core.config import settings
from app.services.llm.llm_client import LLMClient
from app.services.llm.prompt_builder import PromptBuilder
from app.services.llm.retry_handler import with_llm_retries

class OpenAIClient(LLMClient):
    def __init__(self):
        # We instantiate it directly using the config API key
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini" # Using a fast/cheap model by default

    @with_llm_retries()
    async def classify_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        if not transactions:
            return []
            
        prompt = PromptBuilder.build_classification_prompt(transactions)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        # Parse strict JSON directly, no guessing
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        # Ensure it's a list even if the LLM returned a dict with a root key
        if isinstance(result, dict) and "transactions" in result:
            return result["transactions"]
        return result

    @with_llm_retries()
    async def generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = PromptBuilder.build_summary_prompt(data)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        return result
