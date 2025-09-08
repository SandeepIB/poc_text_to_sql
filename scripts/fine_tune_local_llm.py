#!/usr/bin/env python3
"""Fine-tune local LLM with custom schema and rules."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.training.fine_tuner import LocalLLMFineTuner


def main():
    """Fine-tune local LLM with schema-specific training data."""
    load_dotenv()
    
    print("🎯 Fine-tuning Local LLM for Text-to-SQL")
    print("=" * 50)
    
    try:
        # Initialize components
        config = AppConfig()
        db_manager = DatabaseManager(config.db)
        fine_tuner = LocalLLMFineTuner("llama2")
        
        # Extract schema
        print("📊 Extracting database schema...")
        schema_info = db_manager.extract_schema()
        print(f"Found {len(schema_info)} tables: {list(schema_info.keys())}")
        
        # Save training data for review
        print("\n💾 Creating training dataset...")
        count = fine_tuner.save_training_data(schema_info)
        print(f"Generated {count} training examples")
        
        # Ask user confirmation
        print(f"\n🤖 Ready to fine-tune llama2 -> llama2-sql")
        print("This will:")
        print("1. Create a custom model with your database schema")
        print("2. Train it on your specific query patterns")
        print("3. Make it understand your table/column names")
        
        response = input("\nProceed with fine-tuning? (y/N): ").lower().strip()
        
        if response == 'y':
            print("\n🚀 Starting fine-tuning process...")
            success = fine_tuner.fine_tune_model(schema_info)
            
            if success:
                print("\n🎉 Fine-tuning completed successfully!")
                print("\n📋 Next steps:")
                print("1. Update your app to use the fine-tuned model")
                print("2. Restart your application")
                print("3. Test with complex queries")
                
                print(f"\n✨ Your custom model: llama2-sql")
                print("   - Knows your database schema")
                print("   - Understands your query patterns")
                print("   - Uses correct table/column names")
                
            else:
                print("\n❌ Fine-tuning failed!")
                print("Check the error messages above")
        else:
            print("\n⏹️ Fine-tuning cancelled")
            print("You can review the training data in: data/fine_tuning_data.json")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Check if llama2 model exists: ollama list")
        print("3. Verify database connection")
        sys.exit(1)


if __name__ == "__main__":
    main()