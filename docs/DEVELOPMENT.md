# Development Guide

## 🏗️ Architecture Overview

The Text-to-SQL system follows a **clean architecture** pattern with clear separation of concerns:

### **Core Principles**
- **Strategy Pattern**: Multiple SQL generators with common interface
- **Factory Pattern**: Dynamic generator selection based on availability
- **Dependency Injection**: Configurable components
- **Single Responsibility**: Each class has one clear purpose

### **Layer Architecture**
```
┌─────────────────┐
│   API Layer     │ ← FastAPI routes, request/response models
├─────────────────┤
│ Business Logic  │ ← Generators, training, core logic
├─────────────────┤
│ Data Access     │ ← Database operations, schema extraction
├─────────────────┤
│ Infrastructure  │ ← LLM clients, configuration, utilities
└─────────────────┘
```

## 🔧 Adding New Features

### **1. Adding New SQL Generator**

**Step 1**: Create generator class
```python
# text_to_sql/generators/my_generator.py
from .base import BaseSQLGenerator
from typing import Dict, Any

class MyCustomGenerator(BaseSQLGenerator):
    """My custom SQL generator."""
    
    def __init__(self, schema_info: Dict[str, Any], **kwargs):
        super().__init__(schema_info)
        self.custom_param = kwargs.get('custom_param')
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question."""
        # Your custom logic here
        return self._build_custom_query(question)
    
    def _build_custom_query(self, question: str) -> str:
        """Build custom SQL query."""
        # Implementation details
        pass
```

**Step 2**: Register in factory
```python
# text_to_sql/generators/generator_factory.py
from .my_generator import MyCustomGenerator

class GeneratorFactory:
    def create_generator(self, generator_type: str):
        if generator_type == "my_custom":
            return MyCustomGenerator(
                self.schema_info, 
                custom_param="value"
            ), "My Custom Generator"
```

**Step 3**: Add to frontend
```html
<!-- In routes.py HTML template -->
<option value="my_custom">🔥 My Custom Generator</option>
```

**Step 4**: Add tests
```python
# tests/test_my_generator.py
def test_my_generator():
    generator = MyCustomGenerator(schema_info)
    sql = generator.generate_sql("test question")
    assert sql is not None
```

### **2. Adding New Training Method**

**Step 1**: Create trainer class
```python
# text_to_sql/training/my_trainer.py
class MyTrainer:
    """Custom model trainer."""
    
    def __init__(self, config):
        self.config = config
    
    def prepare_data(self, schema_info):
        """Prepare training data."""
        pass
    
    def train(self, training_data):
        """Train the model."""
        pass
    
    def save_model(self, model_path):
        """Save trained model."""
        pass
```

**Step 2**: Create training script
```python
# scripts/train_my_model.py
from text_to_sql.training.my_trainer import MyTrainer

def main():
    trainer = MyTrainer(config)
    trainer.train(training_data)
    trainer.save_model("models/my_model")

if __name__ == "__main__":
    main()
```

### **3. Adding New LLM Provider**

**Step 1**: Extend LLM client factory
```python
# text_to_sql/core/llm_client.py
class LLMClientFactory:
    @staticmethod
    def create_client(config: LLMConfig):
        if config.provider == "my_provider":
            return MyProviderClient(config)
```

**Step 2**: Implement client
```python
# text_to_sql/core/my_provider_client.py
class MyProviderClient:
    def __init__(self, config):
        self.config = config
    
    def chat_completion(self, messages, **kwargs):
        """Implement chat completion."""
        pass
```

## 🧪 Testing Guidelines

### **Test Structure**
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests
├── fixtures/       # Test data and fixtures
└── conftest.py     # Pytest configuration
```

### **Writing Tests**
```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    def setup_method(self):
        """Setup before each test."""
        self.component = MyComponent()
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = self.component.do_something()
        assert result == expected_value
    
    @patch('external.dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependencies."""
        mock_dependency.return_value = "mocked"
        result = self.component.use_dependency()
        assert result == "expected"
```

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=text_to_sql

# Run specific test file
pytest tests/test_generators.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_generator"
```

## 📊 Code Quality

### **Code Style**
- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Add **docstrings** for all classes and methods
- Keep functions **small and focused**

### **Example Code Style**
```python
from typing import Dict, List, Optional, Any

class ExampleClass:
    """Example class following coding standards."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize with configuration.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._private_var: Optional[str] = None
    
    def process_data(self, data: List[Dict[str, Any]]) -> List[str]:
        """Process input data and return results.
        
        Args:
            data: List of data dictionaries
            
        Returns:
            List of processed strings
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        results = []
        for item in data:
            processed = self._process_item(item)
            results.append(processed)
        
        return results
    
    def _process_item(self, item: Dict[str, Any]) -> str:
        """Private method to process single item."""
        return str(item.get('value', ''))
```

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🔍 Debugging

### **Logging Setup**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.info("Processing query: %s", question)
logger.error("Failed to generate SQL: %s", str(e))
```

### **Debug Mode**
```python
# Enable debug mode
import os
os.environ['DEBUG'] = 'true'

# Debug specific component
if os.getenv('DEBUG'):
    print(f"Debug: Generated SQL = {sql}")
```

### **Performance Profiling**
```python
import cProfile
import pstats

# Profile function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = expensive_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## 🚀 Deployment

### **Environment Configuration**
```python
# configs/environments/production.py
class ProductionConfig:
    DEBUG = False
    DATABASE_POOL_SIZE = 10
    CACHE_TIMEOUT = 3600
    LOG_LEVEL = "INFO"

# configs/environments/development.py
class DevelopmentConfig:
    DEBUG = True
    DATABASE_POOL_SIZE = 2
    CACHE_TIMEOUT = 60
    LOG_LEVEL = "DEBUG"
```

### **Docker Setup**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py"]
```

### **Health Checks**
```python
# Add to routes.py
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db_manager.test_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## 📈 Performance Optimization

### **Database Optimization**
```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)

# Query caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_schema_info():
    return db_manager.extract_schema()
```

### **LLM Response Caching**
```python
import hashlib
import json

class LLMCache:
    def __init__(self):
        self.cache = {}
    
    def get_cache_key(self, question: str, generator_type: str) -> str:
        """Generate cache key."""
        data = f"{question}:{generator_type}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """Get cached response."""
        return self.cache.get(key)
    
    def set(self, key: str, value: str) -> None:
        """Cache response."""
        self.cache[key] = value
```

## 🔒 Security Best Practices

### **Input Validation**
```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    question: str
    generator_type: str = "auto"
    
    @validator('question')
    def validate_question(cls, v):
        if len(v) > 500:
            raise ValueError('Question too long')
        return v.strip()
    
    @validator('generator_type')
    def validate_generator_type(cls, v):
        allowed = ['auto', 'custom', 'openai', 'local', 'rule']
        if v not in allowed:
            raise ValueError(f'Invalid generator type: {v}')
        return v
```

### **SQL Injection Prevention**
```python
# Use parameterized queries
def execute_safe_query(self, sql: str, params: Dict = None):
    """Execute SQL with parameter binding."""
    try:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
```

### **API Rate Limiting**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/query")
@limiter.limit("10/minute")
async def generate_sql(request: Request, query: QueryRequest):
    """Rate-limited query endpoint."""
    pass
```

This development guide provides comprehensive information for new developers to understand the codebase, contribute effectively, and maintain code quality standards.