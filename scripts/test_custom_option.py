#!/usr/bin/env python3
"""Test custom model option availability."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from text_to_sql.core.config import AppConfig
from text_to_sql.core.database import DatabaseManager
from text_to_sql.generators.generator_factory import GeneratorFactory


def main():
    """Test custom model option."""
    load_dotenv()
    
    print("🧪 Testing Custom Model Option")
    print("=" * 40)
    
    try:
        # Initialize components
        config = AppConfig()
        db_manager = DatabaseManager(config.db)
        schema_info = db_manager.extract_schema()
        factory = GeneratorFactory(schema_info)
        
        # Test status endpoint
        print("📊 Available Generators:")
        print(f"  Custom: {factory._has_custom_model()}")
        print(f"  OpenAI: {factory._openai_client is not None}")
        print(f"  Local: {factory._local_client is not None}")
        print(f"  Rule: True")
        
        if factory._custom_model:
            print(f"\n🎯 Custom Model: {factory._custom_model}")
        else:
            print(f"\n⏳ Custom Model: Not ready yet (fine-tuning in progress)")
        
        # Test generator creation
        print(f"\n🔧 Testing Generator Creation:")
        
        # Test custom generator
        try:
            generator, used = factory.create_generator("custom")
            print(f"  Custom: ✅ {used}")
        except Exception as e:
            print(f"  Custom: ❌ {e}")
        
        # Test auto generator
        try:
            generator, used = factory.create_generator("auto")
            print(f"  Auto: ✅ {used}")
        except Exception as e:
            print(f"  Auto: ❌ {e}")
        
        print(f"\n✅ Frontend will show custom option when fine-tuning completes")
        print(f"📋 Monitor progress: python scripts/monitor_finetune.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()