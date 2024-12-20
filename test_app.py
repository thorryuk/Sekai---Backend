import pytest
from app import app

# Test client fixture
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Helper function for login
def login(client):
    response = client.post('/login', json={
        'username': 'test',  # Replace with valid username
        'password': 'coba2128'  # Replace with valid password
    })
    assert response.status_code == 200
    return response.get_json()


# Authentication Tests
def test_login(client):
    """Test login and token generation."""
    response = client.post('/login', json={
        'username': 'test',
        'password': 'coba2128'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_refresh_token(client):
    """Test token refresh."""
    tokens = login(client)
    refresh_token = tokens['refresh_token']

    response = client.post('/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data


def test_protected_no_token(client):
    """Test accessing a protected endpoint without a token."""
    response = client.get('/stores')
    assert response.status_code == 401  # Unauthorized


# Store Tests
def test_store_crud(client):
    """Test create, read, update, and delete operations for stores."""
    tokens = login(client)
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Create a store
    create_response = client.post('/stores', headers=headers, json={
        'store_name': 'Test Store',
        'store_type': 'Retail',
        'ktp_number': '1234567890123456',
        'owner_name': 'John Doe',
        'address': '123 Test Street',
        'postal_code': '10110',
        'phone_number': '081234567890'
    })
    assert create_response.status_code == 201
    store_id = create_response.get_json()[0]['id']

    # Read the created store
    read_response = client.get(f'/stores/{store_id}', headers=headers)
    assert read_response.status_code == 200
    assert read_response.get_json()['store_name'] == 'Test Store'

    # Update the store
    update_response = client.put(f'/stores/{store_id}', headers=headers, json={
        'store_name': 'Updated Store Name'
    })
    assert update_response.status_code == 200
    assert update_response.get_json()['store_name'] == 'Updated Store Name'

    # Delete the store
    delete_response = client.delete(f'/stores/{store_id}', headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.get_json()['message'] == 'Store deleted successfully'

    # Verify deletion
    verify_response = client.get(f'/stores/{store_id}', headers=headers)
    assert verify_response.status_code == 404  # Store should no longer exist


# QR Scan Tests
def test_qr_scan_crud(client):
    """Test create and fetch QR scans."""
    tokens = login(client)
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Create a QR scan
    create_response = client.post('/scans', headers=headers, json={
        'product_id': 1,
        'scan_time': '2024-12-19T14:30:00Z',
        'scanned_by': 1
    })
    assert create_response.status_code == 201
    scan_id = create_response.get_json()[0]['id']

    # Fetch all QR scans
    fetch_response = client.get('/scans', headers=headers)
    assert fetch_response.status_code == 200
    scans = fetch_response.get_json()
    assert any(scan['id'] == scan_id for scan in scans)


# Report Tests
def test_store_report(client):
    """Test store report generation."""
    tokens = login(client)
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/reports/stores', headers=headers)
    assert response.status_code == 200
    report = response.get_json()
    assert 'report' in report
    assert isinstance(report['report'], list)


def test_qr_scan_report(client):
    """Test QR scan report generation."""
    tokens = login(client)
    access_token = tokens['access_token']

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/reports/scans', headers=headers)
    assert response.status_code == 200
    report = response.get_json()
    assert 'report' in report
    assert isinstance(report['report'], list)
