#!/usr/bin/env python3
"""Script to train the text-to-SQL model."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.training.model_trainer import SimpleModelTrainer


def main():
    """Train the text-to-SQL model."""
    trainer = SimpleModelTrainer()
    
    try:
        print("🚀 Starting model training...")
        count = trainer.train_model()
        print(f"\n✅ Training analysis completed with {count} examples!")
        
    except FileNotFoundError:
        print("❌ Training data not found!")
        print("Please run: python scripts/generate_training_data.py first")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()