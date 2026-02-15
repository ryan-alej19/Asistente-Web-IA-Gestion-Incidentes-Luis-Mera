import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tecnicontrol-backend.onrender.com"
AUTH_URL = f"{BASE_URL}/api/auth/token/"
FILE_ANALYSIS_ENDPOINT = f"{BASE_URL}/api/incidents/analyze-file-preview/"
USERNAME = "empleado"
PASSWORD = "empleado123"

def debug_file():
    # 1. Login
    print("🔑 Authenticating...")
    token_resp = requests.post(AUTH_URL, json={"username": USERNAME, "password": PASSWORD})
    if token_resp.status_code != 200:
        print(f"Login failed: {token_resp.text}")
        return
    token = token_resp.json().get('token')
    print("✅ Authenticated")

    # 2. Upload File
    headers = {"Authorization": f"Token {token}"}
    filename = "debug_test.txt"
    with open(filename, "w") as f:
        f.write("This is a test file content.")
        
    print(f"📤 Uploading {filename}...")
    try:
        with open(filename, 'rb') as f:
            files = {'file': (filename, f)}
            # Print headers for debug
            # requests adds Content-Type: multipart/form-data... automatically
            resp = requests.post(FILE_ANALYSIS_ENDPOINT, files=files, headers=headers)
            
        print(f"Response Code: {resp.status_code}")
        print(f"Response Content: {resp.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_file()
