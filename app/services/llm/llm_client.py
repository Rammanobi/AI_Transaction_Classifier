from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMClient(ABC):
    @abstractmethod
    async def classify_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Receives a list of transaction dictionaries.
        Returns a list of dictionaries with keys "txn_id" and "category".
        """
        pass

    @abstractmethod
    async def generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives aggregated data about the job.
        Returns a dict with "narrative" (string) and "risk_level" (low, medium, high).
        """
        pass
