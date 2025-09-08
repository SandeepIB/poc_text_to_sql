"""Fine-tune local LLM with custom training data."""

import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class LocalLLMFineTuner:
    """Fine-tune local LLM with schema-specific training data."""
    
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.custom_model_name = f"{model_name}-sql"
        
    def create_training_dataset(self, schema_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create comprehensive training dataset with schema context."""
        
        # Build schema context
        schema_context = self._build_schema_context(schema_info)
        
        # Training examples with correct schema
        examples = [
            {
                "input": f"{schema_context}\n\nQuestion: Which sector has the minimum exposure?\nGenerate SQL:",
                "output": "SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: Which sector has the lowest exposure?\nGenerate SQL:",
                "output": "SELECT counterparty_sector, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE counterparty_sector IS NOT NULL GROUP BY counterparty_sector ORDER BY total_exposure ASC LIMIT 1;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: Which are the top 5 counterparties by MPE value?\nGenerate SQL:",
                "output": "SELECT counterparty_name, counterparty_id, CAST(mpe AS DECIMAL(15,2)) as mpe_value FROM counterparty_new ORDER BY CAST(mpe AS DECIMAL(15,2)) DESC LIMIT 5;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: Which counterparties have the highest total notional exposure?\nGenerate SQL:",
                "output": "SELECT cp.counterparty_name, SUM(CAST(t.notional_usd AS DECIMAL(15,2))) as total_notional FROM counterparty_new cp JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY total_notional DESC LIMIT 20;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: How many trades exist per counterparty?\nGenerate SQL:",
                "output": "SELECT cp.counterparty_name, COUNT(t.id) as trade_count FROM counterparty_new cp LEFT JOIN trade_new t ON cp.counterparty_id = t.reporting_counterparty_id GROUP BY cp.counterparty_id, cp.counterparty_name ORDER BY trade_count DESC;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: Which counterparties have breached their MPE limits?\nGenerate SQL:",
                "output": "SELECT counterparty_name, CAST(mpe AS DECIMAL(15,2)) as current_mpe, CAST(mpe_limit AS DECIMAL(15,2)) as mpe_limit FROM counterparty_new WHERE CAST(mpe AS DECIMAL(15,2)) > CAST(mpe_limit AS DECIMAL(15,2)) ORDER BY current_mpe DESC;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: What is the distribution of counterparties by rating?\nGenerate SQL:",
                "output": "SELECT internal_rating, COUNT(*) as count, SUM(CAST(mpe AS DECIMAL(15,2))) as total_exposure FROM counterparty_new WHERE internal_rating IS NOT NULL GROUP BY internal_rating ORDER BY total_exposure DESC;"
            },
            {
                "input": f"{schema_context}\n\nQuestion: What is the average trade notional exposure by sector?\nGenerate SQL:",
                "output": "SELECT cp.counterparty_sector, AVG(CAST(t.notional_usd AS DECIMAL(15,2))) as avg_notional FROM trade_new t JOIN counterparty_new cp ON t.reporting_counterparty_id = cp.counterparty_id WHERE cp.counterparty_sector IS NOT NULL GROUP BY cp.counterparty_sector ORDER BY avg_notional DESC;"
            }
        ]
        
        return examples
    
    def _build_schema_context(self, schema_info: Dict[str, Any]) -> str:
        """Build schema context for training."""
        context = "Database Schema:\n"
        
        for table_name, table_info in schema_info.items():
            context += f"\nTable: {table_name}\n"
            context += "Columns:\n"
            
            for col in table_info.columns:
                context += f"  - {col['name']} ({col['type']})\n"
            
            if table_info.foreign_keys:
                context += "Foreign Keys:\n"
                for fk in table_info.foreign_keys:
                    context += f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"
        
        context += "\nImportant Rules:\n"
        context += "- Use counterparty_sector from counterparty_new table for sector queries\n"
        context += "- Use CAST(mpe AS DECIMAL(15,2)) for MPE calculations\n"
        context += "- Join counterparty_new and trade_new on counterparty_id = reporting_counterparty_id\n"
        context += "- Always use proper table aliases (cp for counterparty_new, t for trade_new)\n"
        
        return context
    
    def create_modelfile(self, training_examples: List[Dict[str, str]]) -> str:
        """Create Ollama Modelfile for fine-tuning."""
        
        # Create system prompt with examples
        system_prompt = "You are a SQL expert. Generate accurate SQL queries based on the provided database schema. "
        system_prompt += "Always use the correct table and column names from the schema. "
        system_prompt += "Follow the examples provided for similar query patterns."
        
        # Add few examples to system prompt
        system_prompt += "\n\nExamples:\n"
        for i, example in enumerate(training_examples[:3]):
            system_prompt += f"\nExample {i+1}:\n{example['input']}\n{example['output']}\n"
        
        modelfile_content = f"""FROM {self.model_name}

SYSTEM \"\"\"{system_prompt}\"\"\"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER stop "Question:"
PARAMETER stop "Generate SQL:"
"""
        
        return modelfile_content
    
    def fine_tune_model(self, schema_info: Dict[str, Any]) -> bool:
        """Fine-tune the local model with schema-specific data."""
        
        try:
            print("🔧 Creating training dataset...")
            training_examples = self.create_training_dataset(schema_info)
            
            print("📝 Creating Modelfile...")
            modelfile_content = self.create_modelfile(training_examples)
            
            # Save Modelfile
            modelfile_path = Path("data/Modelfile")
            modelfile_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(modelfile_path, "w") as f:
                f.write(modelfile_content)
            
            print(f"🚀 Fine-tuning {self.model_name} -> {self.custom_model_name}...")
            
            # Create custom model with Ollama
            result = subprocess.run([
                "ollama", "create", self.custom_model_name, "-f", str(modelfile_path)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Successfully created {self.custom_model_name}")
                
                # Test the model
                print("🧪 Testing fine-tuned model...")
                test_result = subprocess.run([
                    "ollama", "run", self.custom_model_name, 
                    "Which sector has the minimum exposure?"
                ], capture_output=True, text=True, timeout=30)
                
                if test_result.returncode == 0:
                    print("✅ Fine-tuned model is working!")
                    print(f"Test response: {test_result.stdout[:200]}...")
                    return True
                else:
                    print(f"❌ Model test failed: {test_result.stderr}")
                    return False
            else:
                print(f"❌ Fine-tuning failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Fine-tuning timeout - this may take a while")
            return False
        except Exception as e:
            print(f"❌ Fine-tuning error: {e}")
            return False
    
    def save_training_data(self, schema_info: Dict[str, Any]):
        """Save training data for manual review."""
        training_examples = self.create_training_dataset(schema_info)
        
        output_path = Path("data/fine_tuning_data.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(training_examples, f, indent=2)
        
        print(f"💾 Training data saved to {output_path}")
        return len(training_examples)