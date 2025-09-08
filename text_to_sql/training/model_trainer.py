"""Simple model training using the generated data."""

import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class TrainingConfig:
    """Configuration for model training."""
    model_name: str = "microsoft/DialoGPT-small"
    max_length: int = 512
    batch_size: int = 4
    epochs: int = 3
    learning_rate: float = 5e-5


class SimpleModelTrainer:
    """Simple trainer for text-to-SQL model."""
    
    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        
    def load_training_data(self, data_path: str = "data/training_data.json") -> List[Dict[str, Any]]:
        """Load training data from JSON file."""
        with open(data_path, 'r') as f:
            return json.load(f)
    
    def prepare_training_text(self, examples: List[Dict[str, Any]]) -> List[str]:
        """Prepare training text from examples."""
        training_texts = []
        
        for example in examples:
            # Format: Question: <question> SQL: <sql>
            text = f"Question: {example['question']}\nSQL: {example['sql']}<|endoftext|>"
            training_texts.append(text)
        
        return training_texts
    
    def train_model(self, data_path: str = "data/training_data.json"):
        """Train the model (placeholder implementation)."""
        print("Loading training data...")
        examples = self.load_training_data(data_path)
        
        print(f"Loaded {len(examples)} training examples")
        
        # Prepare training texts
        training_texts = self.prepare_training_text(examples)
        
        print("Training texts prepared:")
        for i, text in enumerate(training_texts[:3]):
            print(f"\nExample {i+1}:")
            print(text[:200] + "..." if len(text) > 200 else text)
        
        print(f"\n📊 Training Statistics:")
        print(f"   Total examples: {len(examples)}")
        print(f"   Average question length: {sum(len(ex['question']) for ex in examples) / len(examples):.1f} chars")
        print(f"   Average SQL length: {sum(len(ex['sql']) for ex in examples) / len(examples):.1f} chars")
        
        # Pattern analysis
        patterns = {}
        for ex in examples:
            pattern = ex.get('pattern_type', 'unknown')
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        print(f"\n🎯 Pattern Distribution:")
        for pattern, count in sorted(patterns.items()):
            print(f"   {pattern}: {count} examples")
        
        print(f"\n✅ Training data analysis complete!")
        print("Note: Actual model training requires GPU and additional dependencies.")
        print("For production use, consider fine-tuning with transformers library.")
        
        return len(examples)