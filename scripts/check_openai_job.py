#!/usr/bin/env python3
"""Check OpenAI fine-tuning job status."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner


def main():
    """Check OpenAI fine-tuning job status."""
    load_dotenv()
    
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_openai_job.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    try:
        fine_tuner = OpenAIFineTuner()
        result = fine_tuner.check_job_status(job_id)
        
        if result["status"] == "succeeded" and result["model"]:
            print(f"\n🎉 Fine-tuning completed!")
            print(f"Custom model: {result['model']}")
            print(f"\n📋 Next steps:")
            print(f"1. Update your .env file:")
            print(f"   OPENAI_FINE_TUNED_MODEL={result['model']}")
            print(f"2. Restart your app")
            print(f"3. Test with complex queries")
            
        elif result["status"] == "running":
            print(f"\n⏳ Fine-tuning in progress...")
            print(f"Check again in a few minutes")
            
        elif result["status"] == "failed":
            print(f"\n❌ Fine-tuning failed!")
            print(f"Check OpenAI dashboard for details")
            
        else:
            print(f"\n📊 Status: {result['status']}")
            
    except Exception as e:
        print(f"❌ Error checking job: {e}")


if __name__ == "__main__":
    main()