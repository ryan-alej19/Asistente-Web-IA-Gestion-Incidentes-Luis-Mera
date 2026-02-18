
import requests
import os

# Configuración
BASE_URL = 'http://127.0.0.1:8000/api'
USERNAME = 'admin'
PASSWORD = 'admin123'  # Asegúrate de que este usuario exista

def get_token():
    url = f"{BASE_URL}/auth/token/"
    data = {'username': USERNAME, 'password': PASSWORD}
    print("Authenticating as admin...")
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json()['token']
        print(f"Token obtained: {token[:10]}...")
        return token
    else:
        print(f"Authentication failed: {response.text}")
        exit(1)

def create_dummy_excel():
    # Helper to create a small file that isn't empty
    filename = "test_file.xlsx"
    with open(filename, "wb") as f:
        f.write(b"PK\x03\x04" + b"\x00" * 1000) # Fake ZIP header (XLSX are zips)
    return filename

def upload_file(token, filepath):
    url = f"{BASE_URL}/incidents/analyze-file-preview/"
    headers = {'Authorization': f'Token {token}'}
    
    print(f"Uploading {filepath}...")
    with open(filepath, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, headers=headers, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("SUCCESS: File analyzed correctly.")
    else:
        print("FAILURE: Analysis failed.")

if __name__ == '__main__':
    token = get_token()
    excel_file = create_dummy_excel()
    try:
        upload_file(token, excel_file)
    finally:
        if os.path.exists(excel_file):
            os.remove(excel_file)
