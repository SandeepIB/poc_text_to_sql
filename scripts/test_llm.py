#!/usr/bin/env python3
"""Test LLM-powered SQL generation."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.core.llm_client import get_available_llm
from text_to_sql.generators.llm_generator import LLMSQLGenerator


def main():
    """Test LLM SQL generation."""
    load_dotenv()
    
    # Initialize components
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    llm_client, llm_config = get_available_llm()
    
    # Get schema
    schema_info = db_manager.extract_schema()
    
    # Create generator
    generator = LLMSQLGenerator(schema_info, llm_client)
    
    # Test questions
    test_questions = [
        "Which sector has the lower exposure?",
        "Which sector has the minimum exposure?",
        "Show me the industry with smallest risk",
        "What counterparty has the most trades?",
        "Which client has highest notional?",
        "Average exposure by sector",
        "Count trades per counterparty"
    ]
    
    print("🤖 Testing LLM-powered SQL generation...\n")
    
    for question in test_questions:
        print(f"Question: {question}")
        sql = generator.generate_sql(question)
        print(f"Generated SQL: {sql[:100]}...")
        print("-" * 50)
    
    print("\n✅ LLM testing complete!")


if __name__ == "__main__":
    main()