#!/usr/bin/env python3
"""Monitor fine-tuning job and update .env when complete."""

import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.training.openai_fine_tuner import OpenAIFineTuner


def update_env_file(model_name: str):
    """Update .env file with custom model name."""
    env_path = Path(".env")
    
    if env_path.exists():
        content = env_path.read_text()
        
        # Add or update OPENAI_CUSTOM_MODEL
        if "OPENAI_CUSTOM_MODEL=" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("OPENAI_CUSTOM_MODEL="):
                    lines[i] = f"OPENAI_CUSTOM_MODEL={model_name}"
                    break
            content = '\n'.join(lines)
        else:
            content += f"\nOPENAI_CUSTOM_MODEL={model_name}\n"
        
        env_path.write_text(content)
        print(f"✅ Updated .env file with custom model: {model_name}")
    else:
        print("❌ .env file not found")


def main():
    """Monitor fine-tuning job."""
    load_dotenv()
    
    job_id = "ftjob-9MUG8PXzlnny8OpBUWZLSA9u"
    
    print(f"🔍 Monitoring fine-tuning job: {job_id}")
    print("Will check every 2 minutes until completion...")
    
    fine_tuner = OpenAIFineTuner()
    
    while True:
        try:
            status_info = fine_tuner.check_job_status(job_id)
            status = status_info['status']
            
            if status == 'succeeded':
                model_name = status_info.get('model')
                if model_name:
                    print(f"🎉 Fine-tuning completed! Model: {model_name}")
                    update_env_file(model_name)
                    print("\n🚀 Custom model is now available in the frontend!")
                    print("Restart the app to use the new model:")
                    print("python app.py")
                    break
                else:
                    print("❌ Fine-tuning succeeded but no model name found")
                    break
            
            elif status == 'failed':
                error = status_info.get('error', 'Unknown error')
                print(f"❌ Fine-tuning failed: {error}")
                break
            
            elif status in ['running', 'validating_files']:
                print(f"⏳ Status: {status} - checking again in 2 minutes...")
                time.sleep(120)  # Wait 2 minutes
            
            else:
                print(f"❓ Unknown status: {status}")
                time.sleep(120)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            time.sleep(120)


if __name__ == "__main__":
    main()