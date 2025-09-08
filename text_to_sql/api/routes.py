"""API routes for the text-to-SQL system."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from .models import QueryRequest, QueryResponse, SchemaResponse
from ..core.config import AppConfig
from ..core.database import DatabaseManager
from ..generators.generator_factory import GeneratorFactory

# Initialize components
config = AppConfig()
db_manager = DatabaseManager(config.db)
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Text-to-SQL Interface</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a87; }
        .result { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007cba; }
        .sql-code { background: #f8f8f8; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; white-space: pre-wrap; line-height: 1.4; }
        .schema { background: #e8f4f8; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .results-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        .results-table th, .results-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .results-table th { background-color: #007cba; color: white; font-weight: bold; }
        .results-table tr:nth-child(even) { background-color: #f9f9f9; }
        .results-table tr:hover { background-color: #f5f5f5; }
        .no-results { color: #666; font-style: italic; }
        .error { color: #d32f2f; background: #ffebee; padding: 10px; border-radius: 5px; }
        .status-indicator { background: #e3f2fd; padding: 8px 12px; border-radius: 20px; margin: 10px 0; font-size: 12px; }
        .status-llm { background: #c8e6c9; color: #2e7d32; }
        .status-nlp { background: #fff3e0; color: #ef6c00; }
        .status-fallback { background: #f3e5f5; color: #7b1fa2; }
        .generator-select { padding: 8px 12px; margin: 0 10px; border: 1px solid #ddd; border-radius: 5px; background: white; }
        .generator-used { background: #e8f5e8; padding: 5px 10px; border-radius: 15px; font-size: 11px; color: #2e7d32; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Text-to-SQL Interface</h1>
        <p>Ask questions about your database in natural language!</p>
        <div id="generator-status" class="status-indicator"></div>
        
        <div>
            <input type="text" id="question" placeholder="e.g., Which counterparties have the highest total notional exposure?" />
            <select id="generatorType" class="generator-select">
                <option value="auto">🤖 Auto (Best Available)</option>
                <option value="custom">🎯 Custom Fine-tuned GPT</option>
                <option value="openai">🧠 OpenAI GPT</option>
                <option value="local">🏠 Local LLM</option>
                <option value="rule">📋 Rule-based</option>
            </select>
            <button onclick="askQuestion()">Generate SQL</button>
        </div>
        
        <div id="result"></div>
        
        <div class="schema">
            <h3>📊 Database Schema</h3>
            <div id="schema"></div>
        </div>
    </div>

    <script>
        async function askQuestion() {
            const question = document.getElementById('question').value;
            const generatorType = document.getElementById('generatorType').value;
            if (!question) return;
            
            document.getElementById('result').innerHTML = '<p>Generating SQL...</p>';
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        question: question,
                        generator_type: generatorType
                    })
                });
                
                const data = await response.json();
                
                let resultsHtml = '';
                if (data.error) {
                    resultsHtml = `<div class="error">Error: ${data.error}</div>`;
                } else if (data.rows && data.rows.length > 0) {
                    resultsHtml = `
                        <h3>Query Results:</h3>
                        <table class="results-table">
                            <thead>
                                <tr>${data.columns.map(col => `<th>${col}</th>`).join('')}</tr>
                            </thead>
                            <tbody>
                                ${data.rows.map(row => 
                                    `<tr>${data.columns.map(col => `<td>${row[col] || ''}</td>`).join('')}</tr>`
                                ).join('')}
                            </tbody>
                        </table>
                    `;
                } else {
                    resultsHtml = '<p class="no-results">No results returned</p>';
                }
                
                document.getElementById('result').innerHTML = `
                    <div class="result">
                        <h3>Question:</h3>
                        <p>${question}</p>
                        <h3>Generated SQL: <span class="generator-used">Used: ${data.generator_used}</span></h3>
                        <div class="sql-code">${data.sql_query}</div>
                        ${resultsHtml}
                    </div>
                `;
            } catch (error) {
                document.getElementById('result').innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function loadSchema() {
            try {
                const response = await fetch('/schema');
                const data = await response.json();
                
                let schemaHtml = '';
                for (const [table, columns] of Object.entries(data.tables)) {
                    schemaHtml += `<strong>${table}:</strong> ${columns.join(', ')}<br>`;
                }
                
                document.getElementById('schema').innerHTML = schemaHtml;
            } catch (error) {
                document.getElementById('schema').innerHTML = 'Error loading schema';
            }
        }
        
        async function loadGeneratorStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                const statusDiv = document.getElementById('generator-status');
                let statusClass = 'status-fallback';
                let statusText = '📋 Available: Rule-based';
                
                if (data.available_generators) {
                    const available = [];
                    if (data.available_generators.custom) available.push('🎯 Custom GPT');
                    if (data.available_generators.openai) available.push('🧠 OpenAI');
                    if (data.available_generators.local) available.push('🏠 Local LLM');
                    if (data.available_generators.rule) available.push('📋 Rule-based');
                    
                    if (available.length > 1) {
                        statusClass = 'status-llm';
                        statusText = `🎆 Available: ${available.join(', ')}`;
                    } else {
                        statusText = `📋 Available: ${available.join(', ')}`;
                    }
                }
                
                statusDiv.className = `status-indicator ${statusClass}`;
                statusDiv.innerHTML = statusText;
            } catch (error) {
                document.getElementById('generator-status').innerHTML = '📋 Available: Rule-based';
                document.getElementById('generator-status').className = 'status-indicator status-fallback';
            }
        }
        
        loadSchema();
        loadGeneratorStatus();
        
        document.getElementById('question').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askQuestion();
            }
        });
    </script>
</body>
</html>
    """


@router.post("/query", response_model=QueryResponse)
async def generate_sql(request: QueryRequest):
    """Generate SQL query from natural language question."""
    try:
        # Extract schema and create generator
        schema_info = db_manager.extract_schema()
        factory = GeneratorFactory(schema_info)
        sql_generator, generator_used = factory.create_generator(request.generator_type)
        
        # Generate SQL
        sql = sql_generator.generate_sql(request.question)
        
        # Execute query
        try:
            columns, rows = db_manager.execute_query(sql, limit=config.row_limit)
            return QueryResponse(
                sql_query=sql,
                columns=columns,
                rows=rows,
                generator_used=generator_used
            )
        except Exception as e:
            return QueryResponse(
                sql_query=sql,
                error=str(e),
                generator_used=generator_used
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema", response_model=SchemaResponse)
async def get_schema():
    """Get database schema information."""
    try:
        schema_info = db_manager.extract_schema()
        tables = {
            name: [col['name'] for col in info.columns] 
            for name, info in schema_info.items()
        }
        return SchemaResponse(tables=tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get available generator types."""
    try:
        schema_info = db_manager.extract_schema()
        factory = GeneratorFactory(schema_info)
        
        # Test each generator type
        available = {
            "custom": factory._has_custom_model(),
            "openai": factory._openai_client is not None,
            "local": factory._local_client is not None,
            "rule": True  # Always available
        }
        
        return {
            "available_generators": available,
            "default": "auto"
        }
    except Exception as e:
        return {
            "available_generators": {"rule": True},
            "default": "rule",
            "error": str(e)
        }