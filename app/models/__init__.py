# app/models/__init__.py
from .base import BaseModelInterface
from .model_type_a import SideModelA
from .model_type_b import SideModelB
from .dummy_models import DummyPickleModel

__all__ = [
    "BaseModelInterface",
    "SideModelA",
    "SideModelB",
    "DummyPickleModel",
]