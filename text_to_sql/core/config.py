"""Configuration management for the text-to-SQL system."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    
    host: str = field(default_factory=lambda: os.getenv("MYSQL_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("MYSQL_PORT", "3306")))
    user: str = field(default_factory=lambda: os.getenv("MYSQL_USER", "root"))
    password: str = field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    database: str = field(default_factory=lambda: os.getenv("MYSQL_DATABASE", ""))


@dataclass
class AppConfig:
    """Main application configuration."""
    
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    row_limit: int = field(default_factory=lambda: int(os.getenv("ROW_LIMIT", "50")))
    
    @property
    def database_url(self) -> str:
        """Get database connection URL."""
        return f"mysql+pymysql://{self.db.user}:{self.db.password}@{self.db.host}:{self.db.port}/{self.db.database}"