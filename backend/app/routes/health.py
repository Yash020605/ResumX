"""
Health check routes.
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__, url_prefix='/api')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Key pool status
    try:
        from app.core.key_manager import key_manager
        pool = key_manager.status()
    except Exception:
        pool = {"error": "key_manager not initialised"}

    # DB status
    try:
        from app.db.session import engine
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"unavailable ({exc.__class__.__name__})"

    return jsonify({
        "status":     "healthy",
        "service":    "ResumX V2 Backend",
        "groq_pool":  pool,
        "database":   db_status,
    }), 200
