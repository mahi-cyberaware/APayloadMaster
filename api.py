from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from modules.payload_creator import PayloadCreator
from modules.binder import Binder
from database import PayloadDB

app = Flask(__name__)
CORS(app)
db = PayloadDB()

@app.route('/api/v1/payloads', methods=['GET'])
def get_payloads():
    """Get all payloads"""
    payloads = db.get_all_payloads()
    return jsonify(payloads)

@app.route('/api/v1/payloads', methods=['POST'])
def create_payload():
    """Create a new payload"""
    data = request.json
    
    creator = PayloadCreator(db)
    payload = creator.create_payload(
        choice=data.get('type'),
        lhost=data.get('lhost'),
        lport=data.get('lport', 4444),
        encrypt=data.get('encrypt', False),
        obfuscate=data.get('obfuscate', False)
    )
    
    if payload:
        return jsonify(payload), 201
    else:
        return jsonify({'error': 'Payload creation failed'}), 500

@app.route('/api/v1/payloads/<int:payload_id>', methods=['GET'])
def get_payload(payload_id):
    """Get specific payload"""
    payload = db.get_payload(payload_id)
    if payload:
        return jsonify(payload)
    else:
        return jsonify({'error': 'Payload not found'}), 404

@app.route('/api/v1/download/<string:file_id>', methods=['GET'])
def download_file(file_id):
    """Download file by ID"""
    filepath = f"server/uploads/{file_id}"
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/v1/upload', methods=['POST'])
def upload_file():
    """Upload file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    file_id = str(uuid.uuid4())[:8]
    filename = file.filename
    filepath = f"server/uploads/{file_id}"
    
    file.save(filepath)
    
    return jsonify({
        'file_id': file_id,
        'filename': filename,
        'download_url': f'/api/v1/download/{file_id}'
    }), 201

def start_api_server(port=5000):
    """Start the API server"""
    print(f"[*] Starting API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
