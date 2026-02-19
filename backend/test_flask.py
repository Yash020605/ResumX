#!/usr/bin/env python
"""Test Flask startup."""
import sys
import os

print("Python version:", sys.version, flush=True)
print("Current directory:", os.getcwd(), flush=True)

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("AI_PROVIDER:", os.getenv("AI_PROVIDER"), flush=True)
print("GROQ_API_KEY set:", bool(os.getenv("GROQ_API_KEY")), flush=True)

# Try to import the app
try:
    print("Importing create_app...", flush=True)
    from app import create_app
    print("Successfully imported create_app", flush=True)
    
    print("Creating Flask app...", flush=True)
    app = create_app()
    print("Successfully created Flask app", flush=True)
    
    print("Starting Flask server...", flush=True)
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc(flush=True)
    sys.exit(1)
