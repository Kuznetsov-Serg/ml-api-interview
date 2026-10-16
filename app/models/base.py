# app/models/base.py (Абстракция)
from abc import ABC, abstractmethod
from typing import Any


class BaseModelInterface(ABC):
    @abstractmethod
    def load(self, path: str) -> None:
        pass

    @abstractmethod
    def predict(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
