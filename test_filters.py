import requests
import json

def test_filters():
    # Login as admin
    try:
        auth_resp = requests.post('http://localhost:8000/api/auth/token/', json={
            'username': 'admin', 
            'password': 'admin123' 
        })
        if auth_resp.status_code != 200:
            print("Login failed")
            return

        token = auth_resp.json()['token']
        headers = {'Authorization': f'Token {token}'}
        base_url = 'http://localhost:8000/api/incidents/list/'

        # Test 1: No Filter
        print("\n--- Test 1: No Filter ---")
        resp = requests.get(base_url, headers=headers)
        print(f"Total: {len(resp.json()['results'])}")

        # Test 2: Filter by URL
        print("\n--- Test 2: Filter Type=URL ---")
        resp = requests.get(base_url, params={'incident_type': 'url'}, headers=headers)
        data = resp.json()['results']
        print(f"Total URL: {len(data)}")
        for i in data:
            if i['incident_type'] != 'url':
                print(f"ERROR: Found {i['incident_type']}")

        # Test 3: Filter by RISK=HIGH (or whatever exists)
        print("\n--- Test 3: Filter Risk=CRITICAL ---")
        resp = requests.get(base_url, params={'risk_level': 'CRITICAL'}, headers=headers)
        data = resp.json()['results']
        print(f"Total Critical: {len(data)}")
        for i in data:
             if i['risk_level'] != 'CRITICAL':
                print(f"ERROR: Found {i['risk_level']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_filters()
