"""Pydantic models for API requests and responses."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for SQL query generation."""
    
    question: str = Field(..., description="Natural language question")
    generator_type: str = Field(default="auto", description="Generator type: auto, openai, local, rule")


class QueryResponse(BaseModel):
    """Response model for SQL query generation."""
    
    sql_query: str = Field(..., description="Generated SQL query")
    columns: List[str] = Field(default_factory=list, description="Result column names")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="Query result rows")
    error: Optional[str] = Field(None, description="Error message if query failed")
    generator_used: str = Field(..., description="Generator type used for this query")


class SchemaResponse(BaseModel):
    """Response model for database schema."""
    
    tables: Dict[str, List[str]] = Field(..., description="Tables and their columns")