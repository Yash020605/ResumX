"""
Main entry point for the Flask application.
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Debug: confirm environment is loaded
print(f"FLASK_DEBUG: {os.getenv('FLASK_DEBUG')}", flush=True)
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}", flush=True)
print(f"AI_PROVIDER: {os.getenv('AI_PROVIDER')}", flush=True)

# Create Flask application
try:
    from app import create_app
    print("Successfully imported create_app", flush=True)
    
    app = create_app()
    print("Successfully created Flask app", flush=True)
except Exception as e:
    print(f"ERROR creating app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Flask with debug={debug}, port={port}", flush=True)
    try:
        app.run(debug=debug, host='127.0.0.1', port=port, use_reloader=False)
    except Exception as e:
        print(f"ERROR running Flask: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
