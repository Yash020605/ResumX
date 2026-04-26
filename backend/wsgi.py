"""
WSGI entry point for gunicorn / waitress.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    from app import create_app
    app = create_app()
except Exception as e:
    print(f"[FATAL] Could not create Flask app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    # Local dev fallback — use run.py for development instead
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
