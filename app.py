#!/usr/bin/env python3
"""Main application entry point."""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from text_to_sql.api.routes import router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Text-to-SQL System",
    description="Convert natural language questions to SQL queries",
    version="1.0.0"
)

# Include routes
app.include_router(router)


def main():
    """Run the application."""
    print("Starting Text-to-SQL Interface...")
    print("Open your browser and go to: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()