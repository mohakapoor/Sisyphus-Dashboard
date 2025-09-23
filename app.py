#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, send_from_directory
import sys, os

sys.path.append(os.path.expanduser("~/scripts"))
import stats

app = Flask(__name__)
app.secret_key = "sisyphus_secret_key_change_this_in_production"  # Change this in production

# Access code - you can change this
ACCESS_CODE = "SuckMahBalls"

def is_authenticated():
    return session.get('authenticated', False)

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
    app.run(host="0.0.0.0", port=5000)
