"""LLM-powered SQL generator with intent prediction."""

import json
import re
from typing import Dict, Any, Optional
from .base import BaseSQLGenerator


class LLMSQLGenerator(BaseSQLGenerator):
    """SQL generator using LLM for intent prediction and semantic mapping."""
    
    def __init__(self, schema_info: Dict[str, Any], llm_client=None):
        super().__init__(schema_info)
        self.llm_client = llm_client
        self._setup_schema_context()
        self._setup_examples()
    
    def _setup_schema_context(self):
        """Setup schema context for LLM."""
        self.schema_context = "Database Schema:\n"
        for table_name, table_info in self.schema_info.items():
            self.schema_context += f"\nTable: {table_name}\n"
            for col in table_info.columns[:10]:  # Limit columns
                self.schema_context += f"  - {col['name']} ({col['type']})\n"
    
    def _setup_examples(self):
        """Setup few-shot examples for LLM."""
        self.examples = [
            {
                "question": "Which counterparties have the highest total notional exposure?",
                "intent": "ranking_query",
                "entity": "counterparty",
                "metric": "notional",
                "direction": "highest",
                "sql": "SELECT cp.counterparty_name, SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional FROM counterparty_new cp JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY total_notional DESC LIMIT 20;"
            },
            {
                "question": "Which sector has the lowest exposure?",
                "intent": "ranking_query", 
                "entity": "sector",
                "metric": "exposure",
                "direction": "lowest",
                "sql": "SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;"
            },
            {
                "question": "How many trades per counterparty?",
                "intent": "count_query",
                "entity": "counterparty",
                "metric": "trades",
                "sql": "SELECT cp.counterparty_name, COUNT(t.id) as trade_count FROM counterparty_new cp LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY trade_count DESC;"
            }
        ]
    
    def generate_sql(self, question: str) -> str:
        """Generate SQL using LLM intent prediction."""
        if self.llm_client:
            return self._generate_with_llm(question)
        else:
            return self._generate_with_rules(question)
    
    def _generate_with_llm(self, question: str) -> str:
        """Generate SQL using LLM."""
        prompt = self._build_llm_prompt(question)
        
        try:
            print(f"🤖 Using LLM for query: {question}")
            
            # Determine model based on client type
            if hasattr(self.llm_client, 'base_url') and "localhost" in str(self.llm_client.base_url):
                # Try fine-tuned model first, fallback to base model
                model = "llama2-sql" if self._model_exists("llama2-sql") else "llama2"
                print(f"🏠 Using local model: {model}")
            else:
                model = "gpt-3.5-turbo"  # Use OpenAI model
                print(f"🧠 Using OpenAI model: {model}")
            
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract SQL from response
            sql_match = re.search(r'```sql\n(.*?)\n```', content, re.DOTALL)
            if sql_match:
                return sql_match.group(1).strip()
            
            # Fallback: look for SQL keywords
            if 'SELECT' in content.upper():
                lines = content.split('\n')
                sql_lines = []
                in_sql = False
                for line in lines:
                    if 'SELECT' in line.upper():
                        in_sql = True
                    if in_sql:
                        sql_lines.append(line)
                        if line.strip().endswith(';'):
                            break
                return '\n'.join(sql_lines)
            
        except Exception as e:
            print(f"⚠️ LLM generation failed: {e}")
        
        # Fallback to rule-based
        print(f"🔄 Falling back to rule-based generation for: {question}")
        return self._generate_with_rules(question)
    
    def _build_llm_prompt(self, question: str) -> str:
        """Build prompt for LLM."""
        examples_text = ""
        for ex in self.examples:
            examples_text += f"\nQuestion: {ex['question']}\n"
            examples_text += f"Intent: {ex['intent']}\n"
            examples_text += f"SQL: ```sql\n{ex['sql']}\n```\n"
        
        return f"""{self.schema_context}

Examples:
{examples_text}

Now generate SQL for this question:
Question: {question}

Analyze the intent and generate appropriate SQL query. Return only the SQL query in ```sql``` blocks."""
    
    def _generate_with_rules(self, question: str) -> str:
        """Fallback rule-based generation with enhanced semantic mapping."""
        q = question.lower()
        
        # Enhanced semantic mapping
        intent = self._predict_intent(q)
        entity = self._extract_entity(q)
        metric = self._extract_metric(q)
        direction = self._extract_direction(q)
        
        # Generate based on intent
        if intent == "ranking_query":
            return self._build_ranking_query(entity, metric, direction, q)
        elif intent == "count_query":
            return self._build_count_query(entity)
        elif intent == "aggregation_query":
            return self._build_aggregation_query(entity, metric, q)
        elif intent == "breach_query":
            return self._build_breach_query()
        else:
            return self._build_default_query(entity)
    
    def _predict_intent(self, question: str) -> str:
        """Predict query intent."""
        if any(word in question for word in ['highest', 'lowest', 'top', 'bottom', 'minimum', 'maximum', 'most', 'least', 'lower', 'higher', 'smaller', 'larger']):
            return "ranking_query"
        elif any(word in question for word in ['how many', 'count', 'number of']):
            return "count_query"
        elif any(word in question for word in ['average', 'mean', 'sum', 'total']):
            return "aggregation_query"
        elif any(word in question for word in ['breach', 'exceed', 'violate', 'limit']):
            return "breach_query"
        elif any(word in question for word in ['distribution', 'breakdown']):
            return "distribution_query"
        else:
            return "basic_query"
    
    def _extract_entity(self, question: str) -> str:
        """Extract main entity from question."""
        if any(word in question for word in ['counterparty', 'counterparties', 'client', 'customer']):
            return "counterparty"
        elif any(word in question for word in ['sector', 'industry', 'segment']):
            return "sector"
        elif any(word in question for word in ['rating', 'grade', 'score']):
            return "rating"
        elif any(word in question for word in ['trade', 'transaction', 'deal']):
            return "trade"
        else:
            return "counterparty"
    
    def _extract_metric(self, question: str) -> str:
        """Extract metric from question."""
        if any(word in question for word in ['exposure', 'risk', 'mpe']):
            return "exposure"
        elif any(word in question for word in ['notional', 'nominal', 'principal']):
            return "notional"
        elif any(word in question for word in ['trade', 'transaction']):
            return "trades"
        else:
            return "exposure"
    
    def _extract_direction(self, question: str) -> str:
        """Extract direction (highest/lowest) from question."""
        if any(word in question for word in ['lowest', 'minimum', 'least', 'smallest', 'lower', 'min']):
            return "lowest"
        else:
            return "highest"
    
    def _build_ranking_query(self, entity: str, metric: str, direction: str, question: str) -> str:
        """Build ranking query based on extracted components."""
        order = "ASC" if direction == "lowest" else "DESC"
        
        if entity == "counterparty" and metric == "notional":
            return f"""SELECT 
    cp.counterparty_name, 
    SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional 
FROM counterparty_new cp 
JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.counterparty_id, cp.counterparty_name 
ORDER BY total_notional {order} 
LIMIT 20;"""
        
        elif entity == "counterparty" and metric == "exposure":
            return f"""SELECT 
    counterparty_name, 
    CAST(mpe AS DECIMAL(15,2)) as mpe_value 
FROM counterparty_new 
ORDER BY CAST(mpe AS DECIMAL(15,2)) {order} 
LIMIT 20;"""
        
        elif entity == "sector" and metric == "exposure":
            return f"""SELECT 
    counterparty_sector, 
    SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure 
FROM counterparty_new 
WHERE counterparty_sector IS NOT NULL 
GROUP BY counterparty_sector 
ORDER BY total_exposure {order} 
LIMIT 1;"""
        
        elif entity == "rating" and metric == "notional":
            return f"""SELECT 
    cp.internal_rating, 
    SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional 
FROM counterparty_new cp 
JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.internal_rating 
ORDER BY total_notional {order} 
LIMIT 1;"""
        
        return self._build_default_query(entity)
    
    def _build_count_query(self, entity: str) -> str:
        """Build count query."""
        if entity == "counterparty":
            return """SELECT 
    cp.counterparty_name, 
    COUNT(t.id) as trade_count 
FROM counterparty_new cp 
LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id 
GROUP BY cp.counterparty_id, cp.counterparty_name 
ORDER BY trade_count DESC;"""
        return self._build_default_query(entity)
    
    def _build_aggregation_query(self, entity: str, metric: str, question: str) -> str:
        """Build aggregation query."""
        if "average" in question and entity == "sector":
            return """SELECT 
    cp.counterparty_sector, 
    AVG(CAST(t.notional_usd AS DECIMAL(15,2))) as avg_notional 
FROM trade_new t 
JOIN counterparty_new cp ON t.reporting_counterparty_id = cp.counterparty_id 
WHERE cp.counterparty_sector IS NOT NULL 
GROUP BY cp.counterparty_sector 
ORDER BY avg_notional DESC;"""
        return self._build_default_query(entity)
    
    def _build_breach_query(self) -> str:
        """Build breach query."""
        return """SELECT 
    counterparty_name, 
    CAST(mpe AS DECIMAL(15,2)) as current_mpe, 
    CAST(mpe_limit AS DECIMAL(15,2)) as mpe_limit 
FROM counterparty_new 
WHERE CAST(mpe AS DECIMAL(15,2)) > CAST(mpe_limit AS DECIMAL(15,2)) 
ORDER BY current_mpe DESC;"""
    
    def _model_exists(self, model_name: str) -> bool:
        """Check if model exists in Ollama."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'].startswith(model_name) for model in models)
        except:
            pass
        return False
    
    def _build_default_query(self, entity: str) -> str:
        """Build default query."""
        if entity == "counterparty":
            return "SELECT * FROM counterparty_new LIMIT 20;"
        elif entity == "trade":
            return "SELECT * FROM trade_new LIMIT 20;"
        else:
            return "SELECT * FROM concentration_new LIMIT 20;"