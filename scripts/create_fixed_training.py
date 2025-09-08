#!/usr/bin/env python3
"""Create fixed training file with 10+ examples."""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager


def create_training_examples(schema_info):
    """Create 10+ training examples."""
    
    schema_context = build_schema_context(schema_info)
    
    examples = [
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "Which sector has the minimum exposure?"},
                {"role": "assistant", "content": "SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "Which sector has the lowest exposure?"},
                {"role": "assistant", "content": "SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "Which are the top 5 counterparties by MPE value?"},
                {"role": "assistant", "content": "SELECT counterparty_name, counterparty_id, CAST(mpe AS DECIMAL(15,2)) as mpe_value FROM counterparty_new ORDER BY CAST(mpe AS DECIMAL(15,2)) DESC LIMIT 5;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "Which counterparties have the highest total notional exposure?"},
                {"role": "assistant", "content": "SELECT cp.counterparty_name, SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional FROM counterparty_new cp JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY total_notional DESC LIMIT 20;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "How many trades exist per counterparty?"},
                {"role": "assistant", "content": "SELECT cp.counterparty_name, COUNT(t.id) as trade_count FROM counterparty_new cp LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY trade_count DESC;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "Which counterparties have breached their MPE limits?"},
                {"role": "assistant", "content": "SELECT counterparty_name, CAST(mpe AS DECIMAL(15,2)) as current_mpe, CAST(mpe_limit AS DECIMAL(15,2)) as mpe_limit FROM counterparty_new WHERE CAST(mpe AS DECIMAL(15,2)) > CAST(mpe_limit AS DECIMAL(15,2)) ORDER BY current_mpe DESC;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "What is the distribution of counterparties by rating?"},
                {"role": "assistant", "content": "SELECT internal_rating, COUNT(*) as count, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE internal_rating IS NOT NULL GROUP BY internal_rating ORDER BY total_exposure DESC;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "What is the average trade notional exposure by sector?"},
                {"role": "assistant", "content": "SELECT cp.counterparty_sector, AVG(CAST(t.notional_usd AS DECIMAL(15,2))) as avg_notional FROM trade_new t JOIN counterparty_new cp ON t.reporting_counterparty_id = cp.counterparty_id WHERE cp.counterparty_sector IS NOT NULL GROUP BY cp.counterparty_sector ORDER BY avg_notional DESC;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "Show me all counterparties with high risk rating"},
                {"role": "assistant", "content": "SELECT counterparty_name, internal_rating, CAST(mpe AS DECIMAL(15,2)) as exposure FROM counterparty_new WHERE internal_rating IN ('High', 'HIGH') ORDER BY CAST(mpe AS DECIMAL(15,2)) DESC;"}
            ]
        },
        {
            "messages": [
                {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                {"role": "user", "content": "What is the total concentration by sector?"},
                {"role": "assistant", "content": "SELECT reporting_group as sector, SUM(CAST(concentration_value AS DECIMAL(15,2))) as total_concentration FROM concentration_new WHERE reporting_group IS NOT NULL GROUP BY reporting_group ORDER BY total_concentration DESC;"}
            ]
        }
    ]
    
    return examples


def build_schema_context(schema_info):
    """Build schema context for training."""
    context = "Database Schema:\n"
    
    for table_name, table_info in schema_info.items():
        context += f"\nTable: {table_name}\n"
        for col in table_info.columns:
            context += f"  - {col['name']} ({col['type']})\n"
    
    context += "\nRules:\n"
    context += "- Use counterparty_sector from counterparty_new for sector queries\n"
    context += "- Use CAST(mpe AS DECIMAL(15,2)) for MPE calculations\n"
    context += "- Join: counterparty_new.counterparty_id = trade_new.reporting_counterparty_id\n"
    
    return context


def main():
    """Create fixed training file."""
    load_dotenv()
    
    print("🔧 Creating fixed training file with 10 examples...")
    
    try:
        # Initialize components
        config = AppConfig()
        db_manager = DatabaseManager(config.db)
        
        # Extract schema
        schema_info = db_manager.extract_schema()
        
        # Create examples
        examples = create_training_examples(schema_info)
        
        # Save as JSONL file
        training_file = Path("data/openai_training_fixed.jsonl")
        training_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(training_file, "w") as f:
            for example in examples:
                f.write(json.dumps(example) + "\n")
        
        print(f"✅ Fixed training file saved: {training_file}")
        print(f"📊 Examples: {len(examples)}")
        
        # Verify file
        with open(training_file, "r") as f:
            lines = f.readlines()
            print(f"🔍 Verified: {len(lines)} lines in file")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()