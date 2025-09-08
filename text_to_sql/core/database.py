"""Database connection and schema extraction."""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.engine import Engine

from .config import DatabaseConfig


@dataclass
class TableInfo:
    """Information about a database table."""
    
    columns: List[Dict[str, Any]]
    foreign_keys: List[Dict[str, Any]]
    sample_data: List[Dict[str, Any]]


class DatabaseManager:
    """Manages database connections and schema extraction."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._engine: Optional[Engine] = None
    
    @property
    def engine(self) -> Engine:
        """Get database engine, creating if necessary."""
        if self._engine is None:
            url = f"mysql+pymysql://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
            self._engine = create_engine(url)
        return self._engine
    
    def extract_schema(self) -> Dict[str, TableInfo]:
        """Extract database schema information."""
        inspector = inspect(self.engine)
        schema_info = {}
        
        for table_name in inspector.get_table_names():
            columns = self._get_column_info(inspector, table_name)
            foreign_keys = self._get_foreign_keys(inspector, table_name)
            sample_data = self._get_sample_data(table_name)
            
            schema_info[table_name] = TableInfo(
                columns=columns,
                foreign_keys=foreign_keys,
                sample_data=sample_data
            )
        
        return schema_info
    
    def _get_column_info(self, inspector, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'default': col['default'],
                'comment': col.get('comment')
            })
        return columns
    
    def _get_foreign_keys(self, inspector, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            fks.append({
                'name': fk['name'],
                'constrained_columns': fk['constrained_columns'],
                'referred_table': fk['referred_table'],
                'referred_columns': fk['referred_columns']
            })
        return fks
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                return [dict(row._mapping) for row in result]
        except Exception:
            return []
    
    def execute_query(self, sql: str, limit: int = 50) -> tuple[List[str], List[Dict[str, Any]]]:
        """Execute SQL query and return columns and rows."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                columns = list(result.keys())
                rows = [dict(row._mapping) for row in result.fetchmany(limit)]
                return columns, rows
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")