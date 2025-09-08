#!/usr/bin/env python3
"""Basic usage examples for the Text-to-SQL system."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.generators.generator_factory import GeneratorFactory


def example_basic_usage():
    """Basic usage example."""
    print("🔍 Basic Text-to-SQL Usage Example")
    print("=" * 40)
    
    # Initialize components
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    schema_info = db_manager.extract_schema()
    factory = GeneratorFactory(schema_info)
    
    # Example questions
    questions = [
        "Which sector has the lowest exposure?",
        "Top 5 counterparties by MPE value?",
        "How many trades per counterparty?",
        "Which counterparties breached their limits?"
    ]
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        
        # Generate SQL using auto mode
        generator, used = factory.create_generator("auto")
        sql = generator.generate_sql(question)
        
        print(f"🤖 Generator: {used}")
        print(f"📝 SQL: {sql}")
        
        # Execute query (optional)
        try:
            columns, rows = db_manager.execute_query(sql, limit=3)
            print(f"📊 Results: {len(rows)} rows")
            if rows:
                print(f"   Sample: {rows[0]}")
        except Exception as e:
            print(f"⚠️ Execution failed: {e}")


def example_generator_comparison():
    """Compare different generators."""
    print("\n🔄 Generator Comparison Example")
    print("=" * 40)
    
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    schema_info = db_manager.extract_schema()
    factory = GeneratorFactory(schema_info)
    
    question = "Which sector has the minimum exposure?"
    generator_types = ["rule", "openai", "local", "custom"]
    
    for gen_type in generator_types:
        try:
            generator, used = factory.create_generator(gen_type)
            sql = generator.generate_sql(question)
            
            print(f"\n🔧 {gen_type.upper()} Generator:")
            print(f"   Used: {used}")
            print(f"   SQL: {sql[:100]}...")
            
        except Exception as e:
            print(f"\n❌ {gen_type.upper()} failed: {e}")


def example_custom_generator():
    """Example of creating custom generator."""
    print("\n🛠️ Custom Generator Example")
    print("=" * 40)
    
    from text_to_sql.generators.base import BaseSQLGenerator
    
    class SimpleGenerator(BaseSQLGenerator):
        """Simple custom generator example."""
        
        def generate_sql(self, question: str) -> str:
            """Generate simple SQL based on keywords."""
            q = question.lower()
            
            if "counterparty" in q and "exposure" in q:
                return """
                SELECT counterparty_name, 
                       CAST(mpe AS DECIMAL(15,2)) as exposure
                FROM counterparty_new 
                ORDER BY exposure DESC 
                LIMIT 10;
                """
            
            elif "sector" in q:
                return """
                SELECT counterparty_sector, 
                       COUNT(*) as count,
                       SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure
                FROM counterparty_new 
                WHERE counterparty_sector IS NOT NULL
                GROUP BY counterparty_sector
                ORDER BY total_exposure DESC;
                """
            
            else:
                return "SELECT * FROM counterparty_new LIMIT 10;"
    
    # Use custom generator
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    schema_info = db_manager.extract_schema()
    
    custom_gen = SimpleGenerator(schema_info)
    
    questions = [
        "Show counterparty exposure",
        "Analyze by sector",
        "Random question"
    ]
    
    for question in questions:
        sql = custom_gen.generate_sql(question)
        print(f"\n❓ {question}")
        print(f"📝 {sql.strip()}")


def example_training_data():
    """Example of working with training data."""
    print("\n📚 Training Data Example")
    print("=" * 40)
    
    from text_to_sql.training.data_generator import TrainingDataGenerator
    
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    schema_info = db_manager.extract_schema()
    
    # Generate training data
    generator = TrainingDataGenerator(schema_info)
    training_data = generator.generate_training_data()
    
    print(f"📊 Generated {len(training_data)} training examples")
    
    # Show sample
    if training_data:
        sample = training_data[0]
        print(f"\n📝 Sample Training Example:")
        print(f"   Question: {sample['question']}")
        print(f"   SQL: {sample['sql'][:100]}...")
        print(f"   Pattern: {sample.get('pattern_type', 'N/A')}")


if __name__ == "__main__":
    try:
        example_basic_usage()
        example_generator_comparison()
        example_custom_generator()
        example_training_data()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1)