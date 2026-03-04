"""
Simple script to run the Arca server directly
"""
import os
import sys
import time
import uvicorn
from pathlib import Path

# Add the current directory to the path so we can import arca
sys.path.insert(0, os.path.abspath("."))

try:
    from fasthtml import FastHTML
except ImportError:
    print("FastHTML is not installed. Please run 'poetry install' to install dependencies.")
    sys.exit(1)

# Import the app from arca.app
from arca.app import app

if __name__ == "__main__":
    print("Starting Arca server...")
    print(f"Server URL: http://localhost:8000")
    
    try:
        # Run the server directly with uvicorn
        # This should block and keep the server running
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"ERROR starting server: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc()) 