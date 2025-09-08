#!/usr/bin/env python3
"""Retrain OpenAI model with complex SQL queries."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner


def main():
    """Retrain with enhanced complex queries."""
    load_dotenv()
    
    print("🚀 Retraining OpenAI GPT with Complex SQL Queries")
    print("=" * 55)
    
    try:
        # Initialize components
        config = AppConfig()
        db_manager = DatabaseManager(config.db)
        fine_tuner = OpenAIFineTuner()
        
        # Extract schema
        print("📊 Extracting database schema...")
        schema_info = db_manager.extract_schema()
        print(f"Found {len(schema_info)} tables: {list(schema_info.keys())}")
        
        # Create enhanced training file
        print("\n💾 Creating enhanced training dataset...")
        examples = fine_tuner.create_training_dataset(schema_info)
        print(f"📊 Generated {len(examples)} complex training examples")
        
        # Show sample complex queries
        print("\n🔍 Sample Complex Queries:")
        complex_examples = [ex for ex in examples if len(ex['messages'][2]['content']) > 200]
        for i, example in enumerate(complex_examples[:3], 1):
            question = example['messages'][1]['content']
            sql = example['messages'][2]['content']
            print(f"\n{i}. Question: {question}")
            print(f"   SQL: {sql[:100]}...")
        
        # Save training file
        file_path = fine_tuner.save_training_file(schema_info)
        
        print(f"\n🤖 Enhanced Training Features:")
        print("✅ Multi-table JOINs")
        print("✅ Complex aggregations (SUM, AVG, COUNT)")
        print("✅ Window functions (RANK, PARTITION BY)")
        print("✅ Subqueries and CTEs")
        print("✅ Percentage calculations")
        print("✅ Conditional logic (CASE WHEN)")
        print("✅ Advanced filtering")
        
        print(f"\n💰 Cost estimate: ~$5-12 for enhanced fine-tuning")
        
        response = input("\nProceed with enhanced fine-tuning? (y/N): ").lower().strip()
        
        if response == 'y':
            print("\n🚀 Starting enhanced fine-tuning...")
            job_id = fine_tuner.fine_tune_complete_workflow(schema_info)
            
            if job_id:
                print(f"\n🎉 Enhanced fine-tuning job submitted!")
                print(f"\n📋 Monitor progress:")
                print(f"   Job ID: {job_id}")
                print(f"   Command: python scripts/monitor_finetune.py")
                
                # Update monitor script with new job ID
                monitor_script = Path("scripts/monitor_finetune.py")
                if monitor_script.exists():
                    content = monitor_script.read_text()
                    updated_content = content.replace(
                        'job_id = "ftjob-9MUG8PXzlnny8OpBUWZLSA9u"',
                        f'job_id = "{job_id}"'
                    )
                    monitor_script.write_text(updated_content)
                    print(f"✅ Monitor script updated with new job ID")
                
                print(f"\n⏰ Expected completion: 15-45 minutes")
                print(f"📧 You'll receive email notification when complete")
                
            else:
                print("\n❌ Enhanced fine-tuning submission failed!")
        else:
            print("\n⏹️ Enhanced fine-tuning cancelled")
            print(f"Enhanced training file saved at: {file_path}")
            print("You can review the complex queries before proceeding")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check OpenAI API key in .env file")
        print("2. Ensure you have fine-tuning credits")
        print("3. Verify database connection")
        sys.exit(1)


if __name__ == "__main__":
    main()