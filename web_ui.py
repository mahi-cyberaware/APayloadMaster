from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from database import PayloadDB

app = Flask(__name__, template_folder='assets/templates')
db = PayloadDB()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_payload():
    if request.method == 'POST':
        # Handle payload creation
        data = request.form
        # Process payload creation
        return jsonify({'status': 'success'})
    return render_template('create.html')

@app.route('/payloads')
def list_payloads():
    payloads = db.get_all_payloads()
    return render_template('payloads.html', payloads=payloads)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

def start_web_interface(port=5001):
    """Start web interface"""
    print(f"[*] Starting web interface on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
