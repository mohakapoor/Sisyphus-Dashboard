#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, send_from_directory
import sys, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import stats

app = Flask(__name__)

# No production optimizations - keep it simple

# Load configuration from environment variables - NO FALLBACKS!
app.secret_key = os.getenv('FLASK_SECRET_KEY')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST')
FLASK_PORT = int(os.getenv('FLASK_PORT'))

# Generate new secret key on each restart to invalidate all sessions
import uuid
app.secret_key = app.secret_key + str(uuid.uuid4())

# Access codes from environment variables - NO FALLBACKS!
VIEWER_CODE = os.getenv('VIEWER_ACCESS_CODE')
ADMIN_CODE = os.getenv('ADMIN_ACCESS_CODE')

# Single admin session tracking
ACTIVE_ADMIN_SESSION = None

def is_authenticated():
    return session.get('authenticated', False)

def get_user_role():
    return session.get('role', 'none')

def is_admin():
    return session.get('role') == 'admin'

def is_viewer_or_admin():
    return session.get('role') in ['viewer', 'admin']

def is_valid_admin_session():
    global ACTIVE_ADMIN_SESSION
    if session.get('role') == 'admin':
        current_session_id = session.get('session_id')
        return ACTIVE_ADMIN_SESSION == current_session_id
    return False

def set_admin_session():
    global ACTIVE_ADMIN_SESSION
    import uuid
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    ACTIVE_ADMIN_SESSION = session_id
    return session_id

def clear_admin_session():
    global ACTIVE_ADMIN_SESSION
    if session.get('session_id') == ACTIVE_ADMIN_SESSION:
        ACTIVE_ADMIN_SESSION = None

# Force HTTPS redirect
@app.before_request
def force_https():
    if not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
        if 'sisyphus.mohakapoor.in' in request.host:
            return redirect(request.url.replace('http://', 'https://'), code=301)

# Add performance headers
@app.after_request
def add_security_headers(response):
    # Basic security headers only
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # NUCLEAR OPTION: Force no caching for static files
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['ETag'] = str(hash(str(datetime.utcnow())))
    
    return response

@app.route("/")
def home():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/login")
def login_page():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    global ACTIVE_ADMIN_SESSION
    data = request.get_json()
    access_code = data.get('access_code', '')
    
    if access_code == ADMIN_CODE:
        # Check if admin session already exists
        if ACTIVE_ADMIN_SESSION is not None:
            return jsonify({"success": False, "error": "Admin session already active. Only one admin allowed."}), 409
        
        session['authenticated'] = True
        session['role'] = 'admin'
        set_admin_session()
        return jsonify({"success": True, "role": "admin"})
    elif access_code == VIEWER_CODE:
        session['authenticated'] = True
        session['role'] = 'viewer'
        return jsonify({"success": True, "role": "viewer"})
    else:
        return jsonify({"success": False, "error": "Invalid access code"}), 401

@app.route("/dashboard")
def dashboard():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template("index.html", user_role=get_user_role())

@app.route("/logout")
def logout():
    clear_admin_session()
    session.pop('authenticated', None)
    session.pop('role', None)
    session.pop('session_id', None)
    return redirect(url_for('home'))

# Removed custom static route - let Flask handle it normally

@app.route("/api/stats", methods=["GET"])
def get_stats():
    if not is_viewer_or_admin():
        return jsonify({"error": "Not authenticated"}), 401
    data = stats.get_stats()
    return jsonify(data)

# Admin check endpoint (no sensitive action)
@app.route("/api/admin/check", methods=["GET"])
def admin_check():
    if is_admin():  # Same check as title uses
        return jsonify({"admin": True})
    else:
        return jsonify({"admin": False}), 403

# Admin-only API endpoints
@app.route("/api/admin/shutdown", methods=["POST"])
def admin_shutdown():
    if not is_valid_admin_session():
        return jsonify({"error": "Valid admin session required"}), 403
    
    # Require re-authentication
    data = request.get_json()
    admin_code = data.get('admin_code', '')
    
    if admin_code != ADMIN_CODE:
        return jsonify({"error": "Admin code required for shutdown"}), 403
    
    try:
        # Use systemd socket for secure shutdown
        import socket
        import os
        
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect('/var/run/sisyphus-shutdown.sock')
        sock.send(b'shutdown_request')
        sock.close()
        
        # Log the action
        import logging
        logging.warning(f"Shutdown initiated by admin session {session.get('session_id')} from IP {request.remote_addr}")
        
        return jsonify({"success": True, "message": "Pi shutdown initiated securely"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Shutdown failed: {str(e)}"}), 500

@app.route("/api/admin/restart", methods=["POST"])
def admin_restart():
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    # Future: Add restart functionality
    return jsonify({"message": "Restart functionality coming soon", "admin": True})

@app.route("/api/docs")
def api_docs():
    """API Documentation page"""
    if not is_authenticated():
        return redirect(url_for('login_page'))
    
    docs = {
        "title": "Sisyphus Dashboard API",
        "version": "1.0.0",
        "base_url": "https://sisyphus.mohakapoor.in",
        "authentication": "Session-based with access codes",
        "endpoints": {
            "Authentication": {
                "POST /authenticate": {
                    "description": "Login with access code",
                    "body": {"access_code": "string"},
                    "responses": {
                        "200": {"success": True, "role": "admin|viewer"},
                        "401": {"success": False, "error": "Invalid access code"},
                        "409": {"success": False, "error": "Admin session already active"}
                    }
                },
                "GET /logout": {
                    "description": "Logout and clear session",
                    "responses": {"302": "Redirect to login"}
                }
            },
            "Data": {
                "GET /api/stats": {
                    "description": "Get system statistics",
                    "auth_required": "viewer or admin",
                    "response": {
                        "cpu_percent": "number",
                        "cpu_cores": ["number"],
                        "memory_percent": "number", 
                        "disk_percent": "number",
                        "temperature": "number",
                        "uptime": "string",
                        "hostname": "string"
                    }
                }
            },
            "Admin": {
                "GET /api/admin/check": {
                    "description": "Check if user has admin privileges",
                    "auth_required": "admin session",
                    "responses": {
                        "200": {"admin": True},
                        "403": {"admin": False}
                    }
                },
                "POST /api/admin/shutdown": {
                    "description": "Shutdown the Raspberry Pi",
                    "auth_required": "admin session + re-authentication",
                    "body": {"admin_code": "string"},
                    "responses": {
                        "200": {"success": True, "message": "Pi shutdown initiated securely"},
                        "403": {"error": "Valid admin session required"}
                    }
                },
                "POST /api/admin/restart": {
                    "description": "Restart the Raspberry Pi (not implemented)",
                    "auth_required": "admin session",
                    "responses": {
                        "200": {"message": "Restart functionality coming soon"}
                    }
                }
            }
        }
    }
    return jsonify(docs)

if __name__ == "__main__":
    # Use environment variables for Flask configuration
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT, threaded=True)
