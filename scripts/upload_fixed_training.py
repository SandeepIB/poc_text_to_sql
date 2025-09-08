#!/usr/bin/env python3
"""Upload fixed training file to OpenAI."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner


def main():
    """Upload fixed training file and start fine-tuning."""
    load_dotenv()
    
    print("🚀 Uploading fixed training file to OpenAI...")
    
    try:
        fine_tuner = OpenAIFineTuner()
        
        # Upload the fixed file
        file_path = "data/openai_training_fixed.jsonl"
        file_id = fine_tuner.upload_training_file(file_path)
        
        # Create fine-tune job
        job_id = fine_tuner.create_fine_tune_job(file_id)
        
        print(f"\n🎉 Fine-tuning job created successfully!")
        print(f"Job ID: {job_id}")
        print(f"\n📋 Monitor progress:")
        print(f"python scripts/check_finetune_status.py")
        
        # Update the status checker with new job ID
        status_checker_path = Path("scripts/check_finetune_status.py")
        content = status_checker_path.read_text()
        updated_content = content.replace(
            'job_id = "ftjob-KQMcwbokR7mNSyHwwq8ZSjHw"',
            f'job_id = "{job_id}"'
        )
        status_checker_path.write_text(updated_content)
        
        print(f"✅ Status checker updated with new job ID")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()