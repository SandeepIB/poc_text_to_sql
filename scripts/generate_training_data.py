#!/usr/bin/env python3
"""Script to generate training data from database schema."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.training.data_generator import TrainingDataGenerator


def main():
    """Generate training data from database schema."""
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    data_generator = TrainingDataGenerator(db_manager)
    
    try:
        # Test database connection
        print("Testing database connection...")
        schema_info = db_manager.extract_schema()
        print(f"Found {len(schema_info)} tables: {list(schema_info.keys())}")
        
        # Generate training data
        print("\nGenerating training data...")
        examples = data_generator.generate_training_data()
        
        # Save training data
        print("\nSaving training data...")
        count = data_generator.save_training_data(examples)
        
        print(f"\n✅ Successfully generated {count} training examples!")
        print("Files created:")
        print("  - data/training_data.json")
        print("  - data/schema_info.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease check:")
        print("1. Database connection settings in .env file")
        print("2. Database is running and accessible")
        print("3. Tables exist in the database")
        sys.exit(1)


if __name__ == "__main__":
    main()