# app/models/base.py (Абстракция)
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseModelInterface(ABC):
    @abstractmethod
    def load(self, path: str) -> None:
        pass

    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass