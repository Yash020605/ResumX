#!/usr/bin/env python
"""
Production Flask runner for Windows.
This directly runs the Flask app without using Flask's development server.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import and create app
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use waitress (pure Python WSGI server, Windows compatible)
    try:
        from waitress import serve
        port = int(os.getenv('PORT', 5000))
        print(f"Starting server on http://127.0.0.1:{port}")
        serve(app, host='0.0.0.0', port=port)
    except ImportError:
        # Fallback to Flask if waitress not available
        print("Using Flask development server")
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
