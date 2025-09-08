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
        """Create generic training dataset based on actual schema."""
        
        schema_context = self._build_schema_context(schema_info)
        
        # Generate generic training examples based on schema
        examples = self._generate_generic_examples(schema_info, schema_context)
        
        return examples
    
    def _generate_generic_examples(self, schema_info: Dict[str, Any], schema_context: str) -> List[Dict[str, Any]]:
        """Generate generic training examples based on schema analysis."""
        examples = []
        
        # Analyze schema to identify patterns
        tables = list(schema_info.keys())
        
        # Find numeric columns for aggregation
        numeric_cols = self._find_numeric_columns(schema_info)
        
        # Find categorical columns for grouping
        categorical_cols = self._find_categorical_columns(schema_info)
        
        # Find relationship columns for joins
        join_cols = self._find_join_columns(schema_info)
        
        # Generate basic aggregation examples
        examples.extend(self._generate_aggregation_examples(schema_context, tables, numeric_cols, categorical_cols))
        
        # Generate join examples
        examples.extend(self._generate_join_examples(schema_context, tables, join_cols, numeric_cols))
        
        # Generate ranking examples
        examples.extend(self._generate_ranking_examples(schema_context, tables, numeric_cols, categorical_cols))
        
        # Generate filtering examples
        examples.extend(self._generate_filtering_examples(schema_context, tables, numeric_cols, categorical_cols))
        
        return examples
    
    def _find_numeric_columns(self, schema_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Find numeric columns in each table."""
        numeric_types = ['DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'INT', 'BIGINT', 'SMALLINT']
        numeric_cols = {}
        
        for table_name, table_info in schema_info.items():
            numeric_cols[table_name] = []
            for col in table_info.columns:
                if any(num_type in col['type'].upper() for num_type in numeric_types):
                    numeric_cols[table_name].append(col['name'])
        
        return numeric_cols
    
    def _find_categorical_columns(self, schema_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Find categorical columns for grouping."""
        categorical_cols = {}
        
        for table_name, table_info in schema_info.items():
            categorical_cols[table_name] = []
            for col in table_info.columns:
                if 'VARCHAR' in col['type'].upper() or 'TEXT' in col['type'].upper():
                    # Skip ID columns and very long text fields
                    if not col['name'].lower().endswith('_id') and 'id' not in col['name'].lower():
                        categorical_cols[table_name].append(col['name'])
        
        return categorical_cols
    
    def _find_join_columns(self, schema_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Find potential join columns (ID fields)."""
        join_cols = {}
        
        for table_name, table_info in schema_info.items():
            join_cols[table_name] = []
            for col in table_info.columns:
                if col['name'].lower().endswith('_id') or col['name'].lower() == 'id':
                    join_cols[table_name].append(col['name'])
        
        return join_cols
    
    def _generate_aggregation_examples(self, schema_context: str, tables: List[str], 
                                     numeric_cols: Dict, categorical_cols: Dict) -> List[Dict]:
        """Generate aggregation query examples."""
        examples = []
        
        for table in tables:
            if numeric_cols.get(table) and categorical_cols.get(table):
                num_col = numeric_cols[table][0]
                cat_col = categorical_cols[table][0]
                
                # Sum aggregation
                examples.append({
                    "messages": [
                        {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                        {"role": "user", "content": f"What is the total {num_col} by {cat_col}?"},
                        {"role": "assistant", "content": f"SELECT {cat_col}, SUM(CAST({num_col} AS DECIMAL(15,2))) as total_{num_col} FROM {table} WHERE {cat_col} IS NOT NULL GROUP BY {cat_col} ORDER BY total_{num_col} DESC;"}
                    ]
                })
                
                # Average aggregation
                examples.append({
                    "messages": [
                        {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                        {"role": "user", "content": f"What is the average {num_col} by {cat_col}?"},
                        {"role": "assistant", "content": f"SELECT {cat_col}, AVG(CAST({num_col} AS DECIMAL(15,2))) as avg_{num_col} FROM {table} WHERE {cat_col} IS NOT NULL GROUP BY {cat_col} ORDER BY avg_{num_col} DESC;"}
                    ]
                })
        
        return examples
    
    def _generate_join_examples(self, schema_context: str, tables: List[str], 
                              join_cols: Dict, numeric_cols: Dict) -> List[Dict]:
        """Generate JOIN query examples."""
        examples = []
        
        # Find potential join relationships
        for table1 in tables:
            for table2 in tables:
                if table1 != table2:
                    # Look for matching ID columns
                    table1_ids = join_cols.get(table1, [])
                    table2_ids = join_cols.get(table2, [])
                    
                    for id1 in table1_ids:
                        for id2 in table2_ids:
                            if id1 == id2 or id1.replace('_id', '') in id2 or id2.replace('_id', '') in id1:
                                if numeric_cols.get(table2):
                                    num_col = numeric_cols[table2][0]
                                    
                                    examples.append({
                                        "messages": [
                                            {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                                            {"role": "user", "content": f"Show total {num_col} for each record in {table1}"},
                                            {"role": "assistant", "content": f"SELECT t1.*, SUM(CAST(t2.{num_col} AS DECIMAL(15,2))) as total_{num_col} FROM {table1} t1 LEFT JOIN {table2} t2 ON t1.{id1} = t2.{id2} GROUP BY t1.{id1} ORDER BY total_{num_col} DESC;"}
                                        ]
                                    })
                                    break
                            if len(examples) >= 3:  # Limit join examples
                                return examples
        
        return examples
    
    def _generate_ranking_examples(self, schema_context: str, tables: List[str], 
                                 numeric_cols: Dict, categorical_cols: Dict) -> List[Dict]:
        """Generate ranking query examples."""
        examples = []
        
        for table in tables:
            if numeric_cols.get(table) and categorical_cols.get(table):
                num_col = numeric_cols[table][0]
                cat_col = categorical_cols[table][0]
                
                # Top N query
                examples.append({
                    "messages": [
                        {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                        {"role": "user", "content": f"Show top 5 records by {num_col}"},
                        {"role": "assistant", "content": f"SELECT *, CAST({num_col} AS DECIMAL(15,2)) as {num_col}_value FROM {table} ORDER BY CAST({num_col} AS DECIMAL(15,2)) DESC LIMIT 5;"}
                    ]
                })
                
                # Window function ranking
                examples.append({
                    "messages": [
                        {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                        {"role": "user", "content": f"Rank records by {num_col} within each {cat_col}"},
                        {"role": "assistant", "content": f"SELECT *, CAST({num_col} AS DECIMAL(15,2)) as {num_col}_value, RANK() OVER (PARTITION BY {cat_col} ORDER BY CAST({num_col} AS DECIMAL(15,2)) DESC) as rank_in_{cat_col} FROM {table} WHERE {cat_col} IS NOT NULL ORDER BY {cat_col}, rank_in_{cat_col};"}
                    ]
                })
                break  # Limit to one table
        
        return examples
    
    def _generate_filtering_examples(self, schema_context: str, tables: List[str], 
                                   numeric_cols: Dict, categorical_cols: Dict) -> List[Dict]:
        """Generate filtering query examples."""
        examples = []
        
        for table in tables:
            if numeric_cols.get(table):
                num_col = numeric_cols[table][0]
                
                # Threshold filtering
                examples.append({
                    "messages": [
                        {"role": "system", "content": f"You are a SQL expert. Generate accurate SQL queries based on this database schema:\n\n{schema_context}"},
                        {"role": "user", "content": f"Show records with high {num_col} values"},
                        {"role": "assistant", "content": f"SELECT * FROM {table} WHERE CAST({num_col} AS DECIMAL(15,2)) > (SELECT AVG(CAST({num_col} AS DECIMAL(15,2))) FROM {table} WHERE {num_col} IS NOT NULL) ORDER BY CAST({num_col} AS DECIMAL(15,2)) DESC;"}
                    ]
                })
                break  # Limit to one example
        
        return examples
    
    def _build_schema_context(self, schema_info: Dict[str, Any]) -> str:
        """Build schema context for training."""
        context = "Database Schema:\n"
        
        for table_name, table_info in schema_info.items():
            context += f"\nTable: {table_name}\n"
            for col in table_info.columns:
                context += f"  - {col['name']} ({col['type']})\n"
        
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
                "n_epochs": 1,
                "batch_size": "auto",
                "learning_rate_multiplier": "auto"
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