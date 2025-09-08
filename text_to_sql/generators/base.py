"""Base SQL generator interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSQLGenerator(ABC):
    """Abstract base class for SQL generators."""
    
    def __init__(self, schema_info: Dict[str, Any]):
        self.schema_info = schema_info
    
    @abstractmethod
    def generate_sql(self, question: str) -> str:
        """Generate SQL query from natural language question."""
        pass