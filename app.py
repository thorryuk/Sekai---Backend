from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
import os

# Initialize Flask app
app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://mlzgmdvhttyvworhfziu.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1semdtZHZodHR5dndvcmhmeml1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQ1ODMyMDEsImV4cCI6MjA1MDE1OTIwMX0._lLiB5d0_QF7GDYyBEt2w60zRX-cpRiNkZIe-j_e-ng')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# JWT configuration
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'  # Replace with a strong secret key
app.config['JWT_VERIFY_SUB'] = False
jwt = JWTManager(app)

# Routes

### Authentication ###
@app.route('/login', methods=['POST'])
def login():
    """Authenticate user and generate JWT."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    try:
        # Fetch user from Supabase
        response = supabase.table('users').select('*').eq('username', username).execute()
        if not response.data:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user = response.data[0]
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Generate JWT tokens
        access_token = create_access_token(identity={'id': str(user['id']), 'role': user['role']})
        refresh_token = create_refresh_token(identity={'id': str(user['id']), 'role': user['role']})
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh the JWT access token."""
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_access_token}), 200

### Store Data Module ###
@app.route('/stores', methods=['GET'])
@jwt_required()
def get_stores():   
    """Fetch all stores."""
    try:
        response = supabase.table('stores').select('*').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stores', methods=['POST'])
@jwt_required()
def create_store():
    """Create a new store."""
    data = request.json
    try:
        response = supabase.table('stores').insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stores/<int:store_id>', methods=['GET'])
@jwt_required()
def get_store_by_id(store_id):
    """Fetch a store by ID."""
    try:
        response = supabase.table('stores').select('*').eq('id', store_id).execute()
        if response.data:
            return jsonify(response.data[0]), 200
        return jsonify({'error': 'Store not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stores/<int:store_id>', methods=['PUT'])
@jwt_required()
def update_store(store_id):
    """Update store details."""
    data = request.json
    try:
        response = supabase.table('stores').update(data).eq('id', store_id).execute()
        if response.data:
            return jsonify(response.data[0]), 200
        return jsonify({'error': 'Store not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stores/<int:store_id>', methods=['DELETE'])
@jwt_required()
def delete_store(store_id):
    """Delete a store."""
    try:
        response = supabase.table('stores').delete().eq('id', store_id).execute()
        if response.data:
            return jsonify({'message': 'Store deleted successfully'}), 200
        return jsonify({'error': 'Store not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

### QR Scan Data Module ###
@app.route('/scans', methods=['GET'])
@jwt_required()
def get_scans():
    """Fetch all QR scans."""
    try:
        response = supabase.table('qr_scans').select('*').execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scans', methods=['POST'])
@jwt_required()
def create_scan():
    """Create a new QR scan."""
    data = request.json
    try:
        response = supabase.table('qr_scans').insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports/stores', methods=['GET'])
@jwt_required()
def report_stores():
    """Generate a report of all stores."""
    try:
        response = supabase.table('stores').select('*').execute()
        return jsonify({'report': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports/scans', methods=['GET'])
@jwt_required()
def report_scans():
    """Generate a report of all QR scans."""
    try:
        response = supabase.table('qr_scans').select('*').execute()
        return jsonify({'report': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
