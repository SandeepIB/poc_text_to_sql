"""Factory for creating different types of SQL generators."""

import os
from typing import Dict, Any, Optional, Tuple
from .custom_openai_generator import CustomOpenAIGenerator
from .enhanced_llm_generator import EnhancedLLMGenerator
from .pattern_generator import PatternSQLGenerator
from ..core.llm_client import LLMClientFactory, LLMConfig


class GeneratorFactory:
    """Factory for creating SQL generators based on type."""
    
    def __init__(self, schema_info: Dict[str, Any]):
        self.schema_info = schema_info
        self._openai_client = None
        self._local_client = None
        self._custom_model = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup available LLM clients."""
        try:
            # Try OpenAI
            openai_config = LLMConfig(provider="openai", model="gpt-3.5-turbo")
            self._openai_client = LLMClientFactory.create_client(openai_config)
            if self._openai_client:
                print("✅ OpenAI client available")
                # Check for custom fine-tuned model
                self._custom_model = self._get_custom_model()
                if self._custom_model:
                    print(f"✅ Custom fine-tuned model available: {self._custom_model}")
        except Exception as e:
            print(f"❌ OpenAI client failed: {e}")
            
        try:
            # Try local LLM
            local_config = LLMConfig(provider="local", model="llama2")
            self._local_client = LLMClientFactory.create_client(local_config)
            if self._local_client:
                print("✅ Local LLM client available")
        except Exception as e:
            print(f"❌ Local LLM client failed: {e}")
            
        print("✅ Rule-based generator always available")
    
    def _get_custom_model(self) -> Optional[str]:
        """Get custom fine-tuned model name from environment or file."""
        # Check environment variable first
        custom_model = os.getenv("OPENAI_CUSTOM_MODEL")
        if custom_model:
            return custom_model
        
        # Check for completed fine-tuning job
        try:
            from ..training.openai_fine_tuner import OpenAIFineTuner
            fine_tuner = OpenAIFineTuner()
            
            # Check the latest job status
            job_id = "ftjob-9MUG8PXzlnny8OpBUWZLSA9u"  # Latest job ID
            status_info = fine_tuner.check_job_status(job_id)
            
            if status_info.get('model'):
                return status_info['model']
        except Exception:
            pass
        
        return None
    
    def _has_custom_model(self) -> bool:
        """Check if custom fine-tuned model is available."""
        return self._custom_model is not None
    
    def create_generator(self, generator_type: str) -> Tuple[Any, str]:
        """Create generator based on type and return (generator, actual_type_used)."""
        
        if generator_type == "openai":
            if self._openai_client:
                return CustomOpenAIGenerator(self.schema_info, self._openai_client), "Custom OpenAI GPT"
            else:
                print("OpenAI not available, falling back to rule-based")
                return PatternSQLGenerator(self.schema_info), "Rule-based (OpenAI unavailable)"
        
        elif generator_type == "local":
            if self._local_client:
                return EnhancedLLMGenerator(self.schema_info, self._local_client), "Local LLM (Enhanced)"
            else:
                print("Local LLM not available, falling back to rule-based")
                return PatternSQLGenerator(self.schema_info), "Rule-based (Local LLM unavailable)"
        
        elif generator_type == "rule":
            return PatternSQLGenerator(self.schema_info), "Rule-based"
        
        elif generator_type == "custom":
            if self._custom_model and self._openai_client:
                generator = CustomOpenAIGenerator(self.schema_info, self._openai_client)
                generator.set_custom_model(self._custom_model)
                return generator, f"Custom Fine-tuned GPT ({self._custom_model})"
            else:
                print("Custom model not available, falling back to OpenAI")
                if self._openai_client:
                    return CustomOpenAIGenerator(self.schema_info, self._openai_client), "OpenAI GPT (Custom unavailable)"
                else:
                    return PatternSQLGenerator(self.schema_info), "Rule-based (Custom unavailable)"
        
        elif generator_type == "auto":
            # Auto: Try Custom -> OpenAI -> Local -> Rule-based
            if self._custom_model and self._openai_client:
                generator = CustomOpenAIGenerator(self.schema_info, self._openai_client)
                generator.set_custom_model(self._custom_model)
                return generator, f"Custom Fine-tuned GPT (Auto)"
            elif self._openai_client:
                return CustomOpenAIGenerator(self.schema_info, self._openai_client), "OpenAI GPT (Auto)"
            elif self._local_client:
                return EnhancedLLMGenerator(self.schema_info, self._local_client), "Local LLM (Auto)"
            else:
                return PatternSQLGenerator(self.schema_info), "Rule-based (Auto)"
        
        else:
            # Default to rule-based
            return PatternSQLGenerator(self.schema_info), "Rule-based (Default)"