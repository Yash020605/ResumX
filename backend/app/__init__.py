"""
ResumeX Backend Application – V2 Multi-Tenant SaaS
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def _rate_limit_handler(e):
    """OWASP: Return a clean 429 with Retry-After header instead of default HTML."""
    return jsonify({
        "error": "Too many requests. Please slow down.",
        "retry_after": str(e.description)
    }), 429


def create_app():
    """Application factory for creating Flask app."""
    app = Flask(__name__)

    # OWASP: Rate limiting prevents brute-force, DoS, and credential stuffing
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        headers_enabled=True,           # Return X-RateLimit-* headers
        on_breach=_rate_limit_handler,  # Custom 429 response
    )

    # Register custom 429 error handler
    app.register_error_handler(RateLimitExceeded, _rate_limit_handler)

    # Enable CORS for all routes
    cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    if cors_origins_env == "*":
        cors_origins = "*"
    else:
        cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
        # Always include localhost for dev convenience
        for _o in ["http://localhost:3000", "http://127.0.0.1:3000"]:
            if _o not in cors_origins:
                cors_origins.append(_o)

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # OWASP: Add security headers to every response
    @app.after_request
    def set_security_headers(response):
        """OWASP: Add security headers to every response."""
        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Don't send referrer to external sites
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Remove server fingerprint
        response.headers.pop("Server", None)
        return response

    # Register blueprints
    from app.routes.analysis import analysis_bp
    from app.routes.health import health_bp
    from app.routes.agents import agents_bp
    from app.routes.auth import auth_bp
    from app.routes.tpo import tpo_bp
    from app.routes.sessions import sessions_bp
    from app.routes.tpo_sessions import tpo_sessions_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tpo_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(tpo_sessions_bp)

    # Tighter limits on auth endpoints to prevent brute-force
    limiter.limit("10 per minute")(auth_bp)
    limiter.limit("5 per minute; 20 per hour")(tpo_sessions_bp)

    # Initialise DB tables (idempotent – safe to run on every startup)
    try:
        from app.db.session import init_db
        init_db()
    except Exception as exc:
        print(f"[App] DB init skipped (no Postgres configured): {exc}")

    return app
