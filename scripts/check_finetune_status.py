#!/usr/bin/env python3
"""Check OpenAI fine-tuning job status."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner


def main():
    """Check fine-tuning job status."""
    load_dotenv()
    
    job_id = "ftjob-9MUG8PXzlnny8OpBUWZLSA9u"  # Your job ID
    
    print(f"🔍 Checking fine-tuning job: {job_id}")
    print("=" * 50)
    
    try:
        fine_tuner = OpenAIFineTuner()
        status_info = fine_tuner.check_job_status(job_id)
        
        print(f"\n📊 Status: {status_info['status']}")
        
        if status_info['model']:
            print(f"🎉 Fine-tuned model ready: {status_info['model']}")
            print("\n📝 To use this model, update your .env file:")
            print(f"OPENAI_MODEL={status_info['model']}")
        elif status_info['status'] == 'running':
            print("⏳ Fine-tuning in progress... Check again in a few minutes")
        elif status_info['status'] == 'failed':
            print("❌ Fine-tuning failed. Check OpenAI dashboard for details")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()