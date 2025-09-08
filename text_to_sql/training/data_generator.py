"""Generate training data from database schema and patterns."""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

from ..core.database import DatabaseManager, TableInfo
from ..generators.pattern_generator import PatternSQLGenerator


@dataclass
class TrainingExample:
    """A single training example."""
    question: str
    sql: str
    pattern_type: str


class TrainingDataGenerator:
    """Generate training data from schema and patterns."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def generate_training_data(self) -> List[TrainingExample]:
        """Generate training examples from database schema."""
        schema_info = self.db_manager.extract_schema()
        sql_generator = PatternSQLGenerator(schema_info)
        
        # Define question templates
        questions = [
            ("Which are the top 5 counterparties by MPE value?", "top_counterparty_mpe"),
            ("Which are the top 10 counterparties by MPE value?", "top_counterparty_mpe"),
            ("Show me top counterparties by MPE", "top_counterparty_mpe"),
            
            ("Which rating bucket has the highest total notional exposure?", "rating_notional"),
            ("What rating has the most notional exposure?", "rating_notional"),
            ("Which rating group has highest notional?", "rating_notional"),
            
            ("Which counterparties have the highest total notional exposure?", "counterparty_highest_notional"),
            ("Which counterparties have the lowest total notional exposure?", "counterparty_lowest_notional"),
            ("Show counterparties with highest notional", "counterparty_highest_notional"),
            ("Show counterparties with lowest notional", "counterparty_lowest_notional"),
            
            ("How many trades exist per counterparty?", "trade_count"),
            ("Trade count by counterparty", "trade_count"),
            ("Number of trades per counterparty", "trade_count"),
            ("Count trades for each counterparty", "trade_count"),
            
            ("What is the highest single trade notional?", "highest_trade"),
            ("Largest trade by notional value", "highest_trade"),
            ("Show the biggest trade", "highest_trade"),
            
            ("Which counterparties have breached their MPE limits?", "limit_breach"),
            ("Show limit breaches", "limit_breach"),
            ("Counterparties exceeding limits", "limit_breach"),
            ("Who has breached limits?", "limit_breach"),
            
            ("What is the distribution of counterparties by rating?", "rating_distribution"),
            ("Rating distribution", "rating_distribution"),
            ("Show counterparties by rating", "rating_distribution"),
            
            ("What is the average trade notional exposure by sector?", "sector_average"),
            ("Average notional by sector", "sector_average"),
            ("Sector average exposure", "sector_average"),
            
            ("Which sector has the lowest exposure?", "sector_lowest"),
            ("Which sector has the minimum exposure?", "sector_lowest"),
            ("Sector with smallest exposure", "sector_lowest"),
            ("Which sector has least exposure?", "sector_lowest"),
            ("Sector with minimum exposure", "sector_lowest"),
            
            ("Which sector has the largest concentration exposure?", "sector_highest"),
            ("Sector with highest exposure", "sector_highest"),
            ("Which sector has most exposure?", "sector_highest"),
            ("Largest sector exposure", "sector_highest"),
        ]
        
        # Generate training examples
        examples = []
        for question, pattern_type in questions:
            sql = sql_generator.generate_sql(question)
            examples.append(TrainingExample(
                question=question,
                sql=sql,
                pattern_type=pattern_type
            ))
        
        return examples
    
    def save_training_data(self, examples: List[TrainingExample], output_dir: str = "data"):
        """Save training data to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionaries
        data = [
            {
                "question": ex.question,
                "sql": ex.sql,
                "pattern_type": ex.pattern_type
            }
            for ex in examples
        ]
        
        # Save as JSON
        with open(output_path / "training_data.json", "w") as f:
            json.dump(data, f, indent=2)
        
        # Save schema info
        schema_info = self.db_manager.extract_schema()
        schema_dict = {}
        for table_name, table_info in schema_info.items():
            schema_dict[table_name] = {
                "columns": table_info.columns,
                "foreign_keys": table_info.foreign_keys,
                "sample_data": table_info.sample_data
            }
        
        with open(output_path / "schema_info.json", "w") as f:
            json.dump(schema_dict, f, indent=2, default=str)
        
        print(f"Generated {len(examples)} training examples")
        print(f"Saved to {output_path}/training_data.json")
        print(f"Schema saved to {output_path}/schema_info.json")
        
        return len(examples)