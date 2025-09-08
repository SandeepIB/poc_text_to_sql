#!/usr/bin/env python3
"""
Quick setup script for Text-to-SQL system
"""
import subprocess
import sys
import os

def run_command(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        sys.exit(1)

def main():
    print("Setting up Text-to-SQL system...")
    
    # Install dependencies
    print("Installing dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Check if .env is configured
    if not os.path.exists(".env"):
        print("Please create .env file with your configuration")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs("data/schemas", exist_ok=True)
    os.makedirs("data/datasets", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models/fine_tuned", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Update .env with your OpenAI API key")
    print("2. Run: python scripts/prepare_data.py")
    print("3. Run: uvicorn src.api.main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()