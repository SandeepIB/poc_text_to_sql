#!/usr/bin/env python3
"""Setup local LLM using Ollama."""

import subprocess
import sys
import time
import requests


def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Ollama not found")
    return False


def install_ollama():
    """Install Ollama."""
    print("📥 Installing Ollama...")
    
    # For macOS/Linux
    try:
        subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], 
                      stdout=subprocess.PIPE, check=True)
        subprocess.run(['sh'], input=subprocess.PIPE, check=True)
        print("✅ Ollama installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install Ollama: {e}")
        print("Please install manually from: https://ollama.ai")
        return False


def start_ollama_service():
    """Start Ollama service."""
    print("🚀 Starting Ollama service...")
    
    try:
        # Start Ollama in background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        time.sleep(3)
        
        # Check if service is running
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                print("✅ Ollama service is running")
                return True
        except:
            pass
            
        print("❌ Failed to start Ollama service")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False


def pull_model(model_name="llama2"):
    """Pull a model from Ollama."""
    print(f"📦 Pulling {model_name} model...")
    
    try:
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {model_name} model downloaded successfully")
            return True
        else:
            print(f"❌ Failed to pull {model_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout pulling {model_name} - this may take a while")
        return False
    except Exception as e:
        print(f"❌ Error pulling {model_name}: {e}")
        return False


def test_local_llm():
    """Test local LLM."""
    print("🧪 Testing local LLM...")
    
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        
        from text_to_sql.core.llm_client import LLMClientFactory, LLMConfig
        
        config = LLMConfig(provider="local", model="llama2")
        client = LLMClientFactory.create_client(config)
        
        if client:
            response = client.chat.completions.create(
                model="llama2",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            print("✅ Local LLM is working!")
            return True
        else:
            print("❌ Failed to create local LLM client")
            return False
            
    except Exception as e:
        print(f"❌ Local LLM test failed: {e}")
        return False


def main():
    """Setup local LLM step by step."""
    print("🏠 Setting up Local LLM with Ollama\n")
    
    # Step 1: Check/Install Ollama
    if not check_ollama_installed():
        if not install_ollama():
            sys.exit(1)
    
    # Step 2: Start Ollama service
    if not start_ollama_service():
        print("\n💡 Try manually:")
        print("   ollama serve")
        sys.exit(1)
    
    # Step 3: Pull model
    models_to_try = ["llama2", "codellama", "mistral"]
    model_pulled = False
    
    for model in models_to_try:
        print(f"\n📦 Trying to pull {model}...")
        if pull_model(model):
            model_pulled = True
            break
        else:
            print(f"⚠️ {model} failed, trying next...")
    
    if not model_pulled:
        print("❌ No models could be downloaded")
        print("\n💡 Try manually:")
        print("   ollama pull llama2")
        sys.exit(1)
    
    # Step 4: Test
    print("\n🧪 Testing setup...")
    if test_local_llm():
        print("\n🎉 Local LLM setup complete!")
        print("\n🚀 Now restart your app:")
        print("   python app.py")
        print("\n✨ You should see 'Local LLM' option available!")
    else:
        print("\n❌ Setup completed but test failed")
        print("Check Ollama service: ollama list")


if __name__ == "__main__":
    main()