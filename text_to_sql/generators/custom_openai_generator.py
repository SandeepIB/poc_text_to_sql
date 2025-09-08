"""Custom OpenAI generator with schema-specific system prompts."""

import os
from typing import Dict, Any
from .llm_generator import LLMSQLGenerator


class CustomOpenAIGenerator(LLMSQLGenerator):
    """Custom OpenAI generator that mimics fine-tuning with system prompts."""
    
    def __init__(self, schema_info: Dict[str, Any], llm_client):
        super().__init__(schema_info, llm_client)
        self.system_prompt = self._build_system_prompt()
        self.custom_model = None
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with schema and rules."""
        
        # Schema context
        schema_context = "You are a SQL expert for this specific database:\n\n"
        for table_name, table_info in self.schema_info.items():
            schema_context += f"Table: {table_name}\n"
            for col in table_info.columns:
                schema_context += f"  - {col['name']} ({col['type']})\n"
            schema_context += "\n"
        
        # Critical rules
        rules = """CRITICAL RULES:
- For sector queries: ALWAYS use counterparty_sector from counterparty_new table
- For exposure queries: ALWAYS use mpe column from counterparty_new table
- For notional queries: ALWAYS use notional_usd from trade_new table
- Join tables: counterparty_new.counterparty_id = trade_new.reporting_counterparty_id
- Use table aliases: cp for counterparty_new, t for trade_new
- Use CAST(column AS DECIMAL(15,2)) for numeric calculations
- For minimum/lowest: ORDER BY column ASC LIMIT 1
- For maximum/highest: ORDER BY column DESC LIMIT 1

EXAMPLES:
Q: Which sector has minimum exposure?
A: SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;

Q: Top 5 counterparties by MPE?
A: SELECT counterparty_name, CAST(mpe AS DECIMAL(15,2)) as mpe_value FROM counterparty_new ORDER BY CAST(mpe AS DECIMAL(15,2)) DESC LIMIT 5;

Generate ONLY the SQL query, no explanation."""
        
        return schema_context + rules
    
    def set_custom_model(self, model_name: str):
        """Set custom fine-tuned model name."""
        self.custom_model = model_name
    
    def _generate_with_llm(self, question: str) -> str:
        """Generate SQL using custom system prompt or fine-tuned model."""
        try:
            model = self.custom_model if self.custom_model else "gpt-3.5-turbo"
            model_type = "Fine-tuned" if self.custom_model else "Custom OpenAI"
            print(f"🎯 Using {model_type} ({model}) for query: {question}")
            
            # For fine-tuned models, use minimal prompt since it's already trained
            if self.custom_model:
                messages = [
                    {"role": "user", "content": question}
                ]
            else:
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question}
                ]
            
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,  # More deterministic
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract SQL from response
            sql = self._extract_sql(content)
            
            # Validate it looks like SQL
            if not self._is_valid_sql(sql):
                print(f"⚠️ Invalid SQL from fine-tuned model: {sql}")
                return self._generate_with_rules(question)
            
            return sql
            
        except Exception as e:
            print(f"⚠️ Custom OpenAI failed: {e}")
            return self._generate_with_rules(question)
    
    def _build_schema_context(self) -> str:
        """Build concise schema context."""
        context = "Database Schema:\n"
        for table_name, table_info in self.schema_info.items():
            context += f"\nTable: {table_name}\n"
            for col in table_info.columns[:8]:  # Limit columns
                context += f"  - {col['name']} ({col['type']})\n"
        return context
    
    def _extract_sql(self, content: str) -> str:
        """Extract SQL from response content."""
        # Remove code blocks
        if '```sql' in content:
            start = content.find('```sql') + 6
            end = content.find('```', start)
            if end != -1:
                return content[start:end].strip()
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            if end != -1:
                return content[start:end].strip()
        
        # Look for SELECT statement
        lines = content.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SELECT'):
                in_sql = True
            if in_sql:
                sql_lines.append(line)
                if line.endswith(';'):
                    break
        
        if sql_lines:
            return '\n'.join(sql_lines)
        
        return content.strip()
    
    def _is_valid_sql(self, sql: str) -> bool:
        """Check if response looks like valid SQL."""
        sql_upper = sql.upper().strip()
        return (
            sql_upper.startswith('SELECT') and
            ('FROM' in sql_upper) and
            len(sql) > 10 and
            not any(phrase in sql.lower() for phrase in [
                'the answer is', 'group c', 'total exposure of', 
                'lowest aggregate', 'concentration group'
            ])
        )