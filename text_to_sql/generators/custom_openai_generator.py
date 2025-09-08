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
            
            # For fine-tuned models, use simpler prompt
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
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up response
            if content.startswith('```sql'):
                content = content[6:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            return content
            
        except Exception as e:
            print(f"⚠️ Custom OpenAI failed: {e}")
            return self._generate_with_rules(question)