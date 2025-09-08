"""Fine-tune OpenAI GPT models with custom schema and scenarios."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI


class OpenAIFineTuner:
    """Fine-tune OpenAI GPT models with schema-specific training data."""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def create_training_dataset(self, schema_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create OpenAI fine-tuning dataset in JSONL format."""
        
        schema_context = self._build_schema_context(schema_info)
        
        # Training examples in OpenAI format - minimum 10 examples required
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
                    {"role": "assistant", "content": "SELECT sector, SUM(CAST(concentration_value AS DECIMAL(15,2))) as total_concentration FROM concentration_new WHERE sector IS NOT NULL GROUP BY sector ORDER BY total_concentration DESC;"}
                ]
            }
        ]
        
        return examples
    
    def _build_schema_context(self, schema_info: Dict[str, Any]) -> str:
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
    
    def save_training_file(self, schema_info: Dict[str, Any]) -> str:
        """Save training data in JSONL format for OpenAI."""
        examples = self.create_training_dataset(schema_info)
        
        # Save as JSONL file
        training_file = Path("data/openai_training.jsonl")
        training_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(training_file, "w") as f:
            for example in examples:
                f.write(json.dumps(example) + "\n")
        
        print(f"💾 Training file saved: {training_file}")
        print(f"📊 Examples: {len(examples)}")
        
        return str(training_file)
    
    def upload_training_file(self, file_path: str) -> str:
        """Upload training file to OpenAI."""
        print("📤 Uploading training file to OpenAI...")
        
        with open(file_path, "rb") as f:
            response = self.client.files.create(
                file=f,
                purpose="fine-tune"
            )
        
        file_id = response.id
        print(f"✅ File uploaded: {file_id}")
        return file_id
    
    def create_fine_tune_job(self, file_id: str, model: str = "gpt-3.5-turbo") -> str:
        """Create fine-tuning job."""
        print(f"🚀 Starting fine-tune job for {model}...")
        
        response = self.client.fine_tuning.jobs.create(
            training_file=file_id,
            model=model,
            hyperparameters={
                "n_epochs": 1,  # Reduced epochs
                "batch_size": "auto",  # Let OpenAI choose
                "learning_rate_multiplier": "auto"  # Let OpenAI choose
            }
        )
        
        job_id = response.id
        print(f"✅ Fine-tune job created: {job_id}")
        return job_id
    
    def check_job_status(self, job_id: str) -> Dict[str, Any]:
        """Check fine-tuning job status."""
        response = self.client.fine_tuning.jobs.retrieve(job_id)
        
        status = response.status
        print(f"📊 Job {job_id}: {status}")
        
        if hasattr(response, 'fine_tuned_model') and response.fine_tuned_model:
            print(f"🎉 Fine-tuned model: {response.fine_tuned_model}")
        
        # Show error details if failed
        if status == 'failed' and hasattr(response, 'error'):
            print(f"❌ Error: {response.error}")
        
        # Show validation results if available
        if hasattr(response, 'result_files') and response.result_files:
            print(f"📋 Result files: {response.result_files}")
        
        return {
            "status": status,
            "model": getattr(response, 'fine_tuned_model', None),
            "error": getattr(response, 'error', None)
        }
    
    def fine_tune_complete_workflow(self, schema_info: Dict[str, Any]) -> str:
        """Complete fine-tuning workflow."""
        try:
            # Step 1: Create training file
            file_path = self.save_training_file(schema_info)
            
            # Step 2: Upload to OpenAI
            file_id = self.upload_training_file(file_path)
            
            # Step 3: Create fine-tune job
            job_id = self.create_fine_tune_job(file_id)
            
            print(f"\n🎯 Fine-tuning started!")
            print(f"Job ID: {job_id}")
            print(f"\n📋 Next steps:")
            print(f"1. Monitor progress: openai api fine_tuning.jobs.retrieve -i {job_id}")
            print(f"2. Wait for completion (usually 10-30 minutes)")
            print(f"3. Use your custom model in the app")
            
            return job_id
            
        except Exception as e:
            print(f"❌ Fine-tuning failed: {e}")
            return None