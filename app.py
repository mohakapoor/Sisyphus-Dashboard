#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, send_from_directory
import sys, os
from datetime import datetime, timedelta

sys.path.append(os.path.expanduser("~/scripts"))
import stats

app = Flask(__name__)

# Production optimizations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files
app.secret_key = "sisyphus_secret_key_change_this_in_production"  # Change this in production

# Access code - you can change this
ACCESS_CODE = "Sisy69"

def is_authenticated():
    return session.get('authenticated', False)

# Add performance headers
@app.after_request
def add_performance_headers(response):
    # Enable compression
    if 'gzip' not in response.headers.get('Content-Encoding', ''):
        response.headers['Vary'] = 'Accept-Encoding'
    
    # Security headers for production
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Cache static files aggressively
    if request.endpoint == 'static' or request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
        response.headers['Expires'] = (datetime.utcnow() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Cache API responses briefly
    elif request.path == '/api/stats':
        response.headers['Cache-Control'] = 'private, max-age=2'  # 2 seconds
    
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
    data = request.get_json()
    access_code = data.get('access_code', '')
    
    if access_code == ACCESS_CODE:
        session['authenticated'] = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 401

@app.route("/dashboard")
def dashboard():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('home'))

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/api/stats", methods=["GET"])
def get_stats():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    data = stats.get_stats()
    return jsonify(data)

if __name__ == "__main__":
    # Production mode - no debug, optimized
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
