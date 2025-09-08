#!/usr/bin/env python3
"""Test database connection and show schema."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager


def main():
    """Test database connection."""
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    config = AppConfig()
    db_manager = DatabaseManager(config.db)
    
    try:
        print("Testing database connection...")
        print(f"Host: {config.db.host}")
        print(f"Port: {config.db.port}")
        print(f"Database: {config.db.database}")
        print(f"User: {config.db.user}")
        
        # Test connection
        schema_info = db_manager.extract_schema()
        
        print(f"\n✅ Connection successful!")
        print(f"Found {len(schema_info)} tables:")
        
        for table_name, table_info in schema_info.items():
            print(f"\n📋 Table: {table_name}")
            print(f"   Columns: {len(table_info.columns)}")
            print(f"   Sample rows: {len(table_info.sample_data)}")
            
            # Show first few columns
            for i, col in enumerate(table_info.columns[:5]):
                print(f"   - {col['name']} ({col['type']})")
            
            if len(table_info.columns) > 5:
                print(f"   ... and {len(table_info.columns) - 5} more columns")
        
        print(f"\n🎯 Ready to generate training data!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease check:")
        print("1. Create .env file with database credentials")
        print("2. Ensure database is running")
        print("3. Verify connection details")
        sys.exit(1)


if __name__ == "__main__":
    main()