"""Enhanced LLM generator with better schema-aware prompts."""

from typing import Dict, Any
from .llm_generator import LLMSQLGenerator


class EnhancedLLMGenerator(LLMSQLGenerator):
    """Enhanced LLM generator with schema-specific prompts."""
    
    def _build_llm_prompt(self, question: str) -> str:
        """Build enhanced prompt with schema context and examples."""
        
        # Build detailed schema context
        schema_context = "Database Schema:\n"
        for table_name, table_info in self.schema_info.items():
            schema_context += f"\nTable: {table_name}\n"
            for col in table_info.columns[:10]:  # Limit columns
                schema_context += f"  - {col['name']} ({col['type']})\n"
        
        # Add critical rules
        rules = """
CRITICAL RULES:
- For sector queries: Use counterparty_sector from counterparty_new table
- For exposure queries: Use mpe column from counterparty_new table  
- For notional queries: Use notional_usd from trade_new table
- Join tables: counterparty_new.counterparty_id = trade_new.reporting_counterparty_id
- Always use table aliases: cp for counterparty_new, t for trade_new
- Use CAST(column AS DECIMAL(15,2)) for numeric calculations
- For minimum/lowest: ORDER BY column ASC LIMIT 1
- For maximum/highest: ORDER BY column DESC LIMIT 1
"""
        
        # Specific examples for common patterns
        examples = """
EXAMPLES:

Question: Which sector has the minimum exposure?
SQL: SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;

Question: Which counterparties have the highest notional?
SQL: SELECT cp.counterparty_name, SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional FROM counterparty_new cp JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY total_notional DESC LIMIT 20;

Question: How many trades per counterparty?
SQL: SELECT cp.counterparty_name, COUNT(t.id) as trade_count FROM counterparty_new cp LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY trade_count DESC;
"""
        
        return f"""{schema_context}

{rules}

{examples}

Question: {question}
Generate ONLY the SQL query without explanation:"""