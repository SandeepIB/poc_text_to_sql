# Text-to-SQL System

A production-ready text-to-SQL system with **AI-powered intent prediction** using LLMs, following Python coding standards with clean architecture and custom training data generation.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
cd text_to_sql_system

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# Optional: Add OpenAI API key for LLM features
OPENAI_API_KEY=your_openai_api_key
```

### 2. Test Database Connection

```bash
python scripts/test_connection.py
```

### 3. Generate Training Data

```bash
python scripts/generate_training_data.py
```

### 4. Run Application

```bash
python app.py
# Open browser: http://localhost:8000
```

## 🏗️ Architecture & Code Structure

```
text_to_sql_system/
├── 📁 text_to_sql/              # Main package
│   ├── 📁 core/                 # Core functionality
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database operations
│   │   └── llm_client.py        # LLM client factory
│   ├── 📁 generators/           # SQL generators (Strategy Pattern)
│   │   ├── base.py              # Base generator interface
│   │   ├── pattern_generator.py # Rule-based generator
│   │   ├── nlp_generator.py     # NLP-enhanced generator
│   │   ├── llm_generator.py     # LLM-powered generator
│   │   ├── custom_openai_generator.py # Custom OpenAI generator
│   │   └── generator_factory.py # Factory for creating generators
│   ├── 📁 training/             # Training & Fine-tuning
│   │   ├── data_generator.py    # Generate training data
│   │   ├── model_trainer.py     # Model training
│   │   └── openai_fine_tuner.py # OpenAI fine-tuning
│   └── 📁 api/                  # API components
│       ├── models.py            # Pydantic models
│       └── routes.py            # FastAPI routes
├── 📁 scripts/                  # Utility scripts
│   ├── test_connection.py       # Test database connection
│   ├── generate_training_data.py # Generate training data
│   ├── fine_tune_openai.py      # Fine-tune OpenAI model
│   ├── monitor_finetune.py      # Monitor fine-tuning progress
│   └── test_llm.py              # Test LLM generation
├── 📁 data/                     # Data storage
│   ├── training_data.json       # Generated training data
│   ├── schema_info.json         # Database schema
│   └── openai_training.jsonl    # OpenAI training format
├── 📁 tests/                    # Unit tests
├── 📁 configs/                  # Configuration files
├── 📁 logs/                     # Application logs
├── app.py                       # Application entry point
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## 🤖 AI-Powered SQL Generation

### **Generator Types (Strategy Pattern)**

1. **🎯 Custom Fine-tuned GPT** - Your trained model
2. **🧠 OpenAI GPT** - GPT-3.5/GPT-4 with system prompts
3. **🏠 Local LLM** - Ollama/LM Studio models
4. **📋 Rule-based** - Pattern matching fallback

### **Generator Selection Logic**
```python
# Auto mode priority:
Custom Fine-tuned → OpenAI → Local LLM → Rule-based
```

## 🔧 Development Guide

### **Adding New Generators**

1. **Create generator class** inheriting from `BaseSQLGenerator`:
```python
# text_to_sql/generators/my_generator.py
from .base import BaseSQLGenerator

class MyGenerator(BaseSQLGenerator):
    def generate_sql(self, question: str) -> str:
        # Your implementation
        return sql_query
```

2. **Register in factory**:
```python
# text_to_sql/generators/generator_factory.py
def create_generator(self, generator_type: str):
    if generator_type == "my_type":
        return MyGenerator(self.schema_info), "My Generator"
```

3. **Add to frontend dropdown**:
```html
<!-- text_to_sql/api/routes.py -->
<option value="my_type">🔥 My Generator</option>
```

### **Adding New Training Methods**

1. **Create trainer class**:
```python
# text_to_sql/training/my_trainer.py
class MyTrainer:
    def train(self, training_data):
        # Your training logic
        pass
```

2. **Add training script**:
```python
# scripts/train_my_model.py
from text_to_sql.training.my_trainer import MyTrainer
# Training script implementation
```

### **Database Schema Changes**

1. **Update schema extraction** in `database.py`
2. **Update training data generation** in `data_generator.py`
3. **Test with** `python scripts/test_connection.py`

## 🎯 Fine-tuning Custom Models

### **OpenAI Fine-tuning**

```bash
# 1. Generate training data
python scripts/generate_training_data.py

# 2. Start fine-tuning
python scripts/fine_tune_openai.py

# 3. Monitor progress
python scripts/monitor_finetune.py

# 4. Use custom model (auto-detected when complete)
```

### **Local LLM Fine-tuning**

```bash
# 1. Setup local LLM
python scripts/setup_local_llm.py

# 2. Fine-tune local model
python scripts/fine_tune_local_llm.py

# 3. Test local model
python scripts/test_llm.py
```

## 📊 Supported Query Patterns

### **Natural Language Understanding**
- **Ranking**: "Which sector has the lowest exposure?"
- **Aggregation**: "Average notional by sector"
- **Counting**: "How many trades per counterparty?"
- **Breach Analysis**: "Which counterparties exceeded limits?"
- **Distribution**: "Breakdown of counterparties by rating"

### **Semantic Mapping**
- `lower/minimum/smallest` → `lowest`
- `industry/segment` → `sector`
- `client/customer` → `counterparty`
- `risk/MPE` → `exposure`

## 🧪 Testing

### **Unit Tests**
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_generators.py

# Run with coverage
python -m pytest --cov=text_to_sql tests/
```

### **Integration Tests**
```bash
# Test database connection
python scripts/test_connection.py

# Test LLM integration
python scripts/test_llm.py

# Test custom model option
python scripts/test_custom_option.py
```

## 🔍 Debugging & Monitoring

### **Logs**
```bash
# Application logs
tail -f logs/app.log

# Database query logs
tail -f logs/database.log

# LLM interaction logs
tail -f logs/llm.log
```

### **Debug Mode**
```bash
# Run with debug logging
DEBUG=true python app.py

# Test specific generator
python -c "
from text_to_sql.generators.generator_factory import GeneratorFactory
from text_to_sql.core.database import DatabaseManager
from text_to_sql.core.config import AppConfig

config = AppConfig()
db = DatabaseManager(config.db)
schema = db.extract_schema()
factory = GeneratorFactory(schema)
generator, used = factory.create_generator('openai')
print(generator.generate_sql('Which sector has lowest exposure?'))
"
```

## 🚀 Deployment

### **Production Setup**
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment
export ENVIRONMENT=production

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### **Docker Deployment**
```bash
# Build image
docker build -t text-to-sql .

# Run container
docker run -p 8000:8000 --env-file .env text-to-sql
```

## 📈 Performance Optimization

### **Database Optimization**
- Use connection pooling
- Add query result caching
- Optimize schema extraction

### **LLM Optimization**
- Cache LLM responses
- Use streaming for long responses
- Implement request batching

### **Frontend Optimization**
- Add query result pagination
- Implement query history
- Add export functionality

## 🔒 Security

### **Environment Variables**
- Never commit `.env` files
- Use secrets management in production
- Rotate API keys regularly

### **Database Security**
- Use read-only database user
- Implement query timeouts
- Add SQL injection protection

### **API Security**
- Add rate limiting
- Implement authentication
- Use HTTPS in production

## 🤝 Contributing

### **Code Style**
- Follow PEP 8
- Use type hints
- Add docstrings
- Write unit tests

### **Pull Request Process**
1. Fork repository
2. Create feature branch
3. Add tests
4. Update documentation
5. Submit pull request

### **Development Workflow**
```bash
# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run tests before commit
python -m pytest
```

## 📚 API Documentation

### **Endpoints**
- `GET /` - Web interface
- `POST /query` - Generate SQL from question
- `GET /schema` - Get database schema
- `GET /status` - Get available generators

### **Request/Response Models**
```python
# Query Request
{
    "question": "Which sector has lowest exposure?",
    "generator_type": "auto"  # auto, custom, openai, local, rule
}

# Query Response
{
    "sql_query": "SELECT ...",
    "columns": ["sector", "exposure"],
    "rows": [{"sector": "Tech", "exposure": 1000}],
    "generator_used": "Custom Fine-tuned GPT"
}
```

## 🆘 Troubleshooting

### **Common Issues**

**Database Connection Failed**
```bash
# Check credentials
python scripts/test_connection.py

# Verify database is running
mysql -h localhost -u username -p
```

**OpenAI API Issues**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API connection
python scripts/test_llm.py
```

**Fine-tuning Failed**
```bash
# Check training data format
python scripts/check_finetune_status.py

# Monitor job progress
python scripts/monitor_finetune.py
```

**Local LLM Not Working**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull required model
ollama pull llama2
```

## 📞 Support

- **Issues**: Create GitHub issue
- **Documentation**: Check `/docs` folder
- **Examples**: See `/examples` folder
- **Community**: Join Discord server

---

Built for financial risk analysis with counterparty, trade, and exposure data. Supports multiple LLM providers and custom fine-tuning for optimal performance.