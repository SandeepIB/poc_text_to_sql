#!/usr/bin/env python3
"""Fine-tune OpenAI GPT with custom schema and scenarios."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner


def main():
    """Fine-tune OpenAI GPT with schema-specific training data."""
    load_dotenv()
    
    print("🧠 Fine-tuning OpenAI GPT for Text-to-SQL")
    print("=" * 50)
    
    try:
        # Initialize components
        config = AppConfig()
        db_manager = DatabaseManager(config.db)
        fine_tuner = OpenAIFineTuner()
        
        # Extract schema
        print("📊 Extracting database schema...")
        schema_info = db_manager.extract_schema()
        print(f"Found {len(schema_info)} tables: {list(schema_info.keys())}")
        
        # Create training file
        print("\n💾 Creating OpenAI training dataset...")
        file_path = fine_tuner.save_training_file(schema_info)
        
        print(f"\n🤖 Ready to fine-tune OpenAI GPT")
        print("This will:")
        print("1. Upload training data to OpenAI")
        print("2. Create a fine-tuning job")
        print("3. Train GPT on your specific schema")
        print("4. Create a custom model for your database")
        
        print(f"\n💰 Cost estimate: ~$3-8 for gpt-3.5-turbo fine-tuning")
        
        response = input("\nProceed with OpenAI fine-tuning? (y/N): ").lower().strip()
        
        if response == 'y':
            print("\n🚀 Starting OpenAI fine-tuning...")
            job_id = fine_tuner.fine_tune_complete_workflow(schema_info)
            
            if job_id:
                print(f"\n🎉 Fine-tuning job submitted!")
                print(f"\n📋 Monitor progress:")
                print(f"   Job ID: {job_id}")
                print(f"   Status: Check OpenAI dashboard or run:")
                print(f"   python -c \"from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner; OpenAIFineTuner().check_job_status('{job_id}')\"")
                
                print(f"\n⏰ Expected completion: 10-30 minutes")
                print(f"📧 You'll receive email notification when complete")
                
            else:
                print("\n❌ Fine-tuning submission failed!")
        else:
            print("\n⏹️ Fine-tuning cancelled")
            print(f"Training file saved at: {file_path}")
            print("You can review the training data before proceeding")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check OpenAI API key in .env file")
        print("2. Ensure you have fine-tuning credits")
        print("3. Verify database connection")
        sys.exit(1)


if __name__ == "__main__":
    main()